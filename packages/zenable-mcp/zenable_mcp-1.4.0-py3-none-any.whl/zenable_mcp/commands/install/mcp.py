import os
from typing import List

import click

from zenable_mcp.utils.install_helpers import (
    determine_ides_to_configure,
    install_ide_configuration,
    validate_api_key,
)
from zenable_mcp.utils.install_status import (
    InstallResult,
    get_exit_code,
    show_installation_summary,
    show_post_install_instructions,
)


def _install_mcp_for_ides(
    ctx,
    ides: List[str],
    overwrite: bool,
    no_instructions: bool,
    dry_run: bool,
    is_global: bool,
) -> int:
    """Common function to install MCP for specified IDEs."""
    # Get API key from context or environment
    api_key = None
    if ctx.obj is not None:
        api_key = ctx.obj.get("api_key")
    if not api_key:
        api_key = os.environ.get("ZENABLE_API_KEY")

    # Validate API key
    validate_api_key(api_key, dry_run)

    # Check if Windsurf is in the list and warn if not global
    if "windsurf" in ides and not is_global:
        click.echo(
            f"\n{click.style('Warning:', fg='yellow')} Windsurf does not support project-level MCP configuration.\n"
            f"Skipping Windsurf. To install for Windsurf, run:\n"
            f"  uvx zenable-mcp install mcp windsurf --global"
        )
        # Remove windsurf from the list
        ides = [ide for ide in ides if ide != "windsurf"]
        if not ides:
            # If windsurf was the only IDE, exit
            click.echo("\nNo IDEs to configure.")
            return 0

    # Track results
    results: List[InstallResult] = []

    # Install for each IDE
    for ide_name in ides:
        result = install_ide_configuration(
            ide_name, api_key, overwrite, dry_run, no_instructions, is_global
        )
        results.append(result)

    # In dry-run mode, display grouped file operations
    if dry_run:
        files_to_create = []
        files_to_modify = []
        files_to_overwrite = []
        files_unchanged = []

        for result in results:
            if result.details and ":" in result.details:
                action, path = result.details.split(":", 1)
                if action == "create":
                    files_to_create.append(path)
                elif action == "update":
                    files_to_modify.append(path)
                elif action == "overwrite":
                    files_to_overwrite.append(path)
                elif action == "unchanged":
                    files_unchanged.append(path)

        # Display grouped operations
        if files_to_create:
            click.echo(f"\n{click.style('Would create:', fg='cyan', bold=True)}")
            for path in files_to_create:
                click.echo(f"  • {path}")

        if files_to_modify:
            click.echo(f"\n{click.style('Would modify:', fg='cyan', bold=True)}")
            for path in files_to_modify:
                click.echo(f"  • {path}")

        if files_to_overwrite:
            click.echo(f"\n{click.style('Would overwrite:', fg='cyan', bold=True)}")
            for path in files_to_overwrite:
                click.echo(f"  • {path}")

        if files_unchanged:
            click.echo(f"\n{click.style('Already up-to-date:', fg='green', bold=True)}")
            for path in files_unchanged:
                click.echo(f"  • {path}")

    # Show summary
    show_installation_summary(results, dry_run, "MCP Installation")

    # Show post-install instructions
    show_post_install_instructions(results, no_instructions, dry_run)

    # In dry-run mode, show preview message
    if dry_run and any(r.is_success for r in results):
        click.echo(
            "\nTo actually perform the installation, run the command without --dry-run"
        )

    # Get the exit code
    return get_exit_code(results)


# Create options that will be shared by all subcommands
def common_options(f):
    """Decorator to add common options to all MCP subcommands."""
    f = click.option(
        "--overwrite",
        is_flag=True,
        default=False,
        help="Overwrite existing Zenable configuration if it exists",
    )(f)
    f = click.option(
        "--no-instructions",
        is_flag=True,
        default=False,
        help="Don't show post-installation instructions",
    )(f)
    f = click.option(
        "--dry-run",
        is_flag=True,
        default=False,
        help="Show what would be done without actually performing the installation",
    )(f)
    f = click.option(
        "--global",
        "-g",
        "is_global",
        is_flag=True,
        default=False,
        help="Install globally in user's home directory instead of project directory",
    )(f)
    return f


@click.group(invoke_without_command=True)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Show what would be done without actually performing the installation",
)
@click.option(
    "--global",
    "-g",
    "is_global",
    is_flag=True,
    default=False,
    help="Install globally in user's home directory instead of project directory",
)
@click.pass_context
def mcp(ctx, dry_run, is_global):
    """Install Zenable MCP server configuration.

    **Requires ZENABLE_API_KEY environment variable to be set.**

    \b
    Examples:
      # Install MCP for all supported IDEs (default)
      zenable-mcp install mcp
      zenable-mcp install mcp all
    \b
      # Install MCP globally for all supported IDEs
      zenable-mcp install mcp --global
      zenable-mcp install mcp all --global
    \b
      # Install MCP for a specific IDE
      zenable-mcp install mcp cursor
      zenable-mcp install mcp claude
    \b
      # Preview what would be done without installing
      zenable-mcp install mcp --dry-run
      zenable-mcp install mcp cursor --dry-run

    \b
    For more information, visit:
    https://docs.zenable.io/integrations/mcp
    """
    # Store dry_run and is_global in context for subcommands
    ctx.ensure_object(dict)
    ctx.obj["dry_run"] = dry_run
    ctx.obj["is_global"] = is_global

    # If no subcommand is provided, default to 'all'
    if ctx.invoked_subcommand is None:
        ctx.invoke(
            all_ides,
            overwrite=False,
            no_instructions=False,
            dry_run=dry_run,
            is_global=is_global,
        )


@mcp.command(name="all")
@common_options
@click.pass_context
def all_ides(ctx, overwrite, no_instructions, dry_run, is_global):
    """Install MCP for all supported IDEs."""
    # Get parent's dry_run and is_global if available (from either mcp group or install command)
    if not dry_run:
        if ctx.parent and ctx.parent.obj:
            dry_run = ctx.parent.obj.get("dry_run", False)
        if not dry_run and ctx.parent and ctx.parent.parent and ctx.parent.parent.obj:
            dry_run = ctx.parent.parent.obj.get("dry_run", False)

    # Get is_global from parent if not explicitly set
    if not is_global:
        if ctx.parent and ctx.parent.obj:
            is_global = ctx.parent.obj.get("is_global", False)

    ides = determine_ides_to_configure("all", dry_run, is_global)
    exit_code = _install_mcp_for_ides(
        ctx, ides, overwrite, no_instructions, dry_run, is_global
    )

    # Handle exit code
    if ctx.parent and ctx.parent.parent:
        return exit_code
    else:
        ctx.exit(exit_code)


@mcp.command()
@common_options
@click.pass_context
def cursor(ctx, overwrite, no_instructions, dry_run, is_global):
    """Install MCP for Cursor IDE."""
    # Get parent's dry_run if available (from either mcp group or install command)
    if not dry_run:
        if ctx.parent and ctx.parent.obj:
            dry_run = ctx.parent.obj.get("dry_run", False)
        if not dry_run and ctx.parent and ctx.parent.parent and ctx.parent.parent.obj:
            dry_run = ctx.parent.parent.obj.get("dry_run", False)

    if not dry_run:
        location = "globally" if is_global else "locally"
        click.echo(f"Installing Zenable MCP configuration for Cursor {location}...")

    exit_code = _install_mcp_for_ides(
        ctx, ["cursor"], overwrite, no_instructions, dry_run, is_global
    )

    # Handle exit code
    if ctx.parent and ctx.parent.parent:
        return exit_code
    else:
        ctx.exit(exit_code)


@mcp.command()
@common_options
@click.pass_context
def windsurf(ctx, overwrite, no_instructions, dry_run, is_global):
    """Install MCP for Windsurf IDE."""
    # Get parent's dry_run if available (from either mcp group or install command)
    if not dry_run:
        if ctx.parent and ctx.parent.obj:
            dry_run = ctx.parent.obj.get("dry_run", False)
        if not dry_run and ctx.parent and ctx.parent.parent and ctx.parent.parent.obj:
            dry_run = ctx.parent.parent.obj.get("dry_run", False)

    # Check if user is trying to install project-level (not global)
    if not is_global:
        click.echo(
            f"\n{click.style('Warning:', fg='yellow', bold=True)} Windsurf does not support project-level MCP configuration.\n"
            f"Please run with --global flag to install globally:\n"
            f"  uvx zenable-mcp install mcp windsurf --global\n\n"
            f"For more information, see: https://docs.windsurf.com/windsurf/cascade/mcp#mcp-config-json"
        )
        ctx.exit(1)

    if not dry_run:
        click.echo("Installing Zenable MCP configuration for Windsurf globally...")

    exit_code = _install_mcp_for_ides(
        ctx, ["windsurf"], overwrite, no_instructions, dry_run, is_global
    )

    # Handle exit code
    if ctx.parent and ctx.parent.parent:
        return exit_code
    else:
        ctx.exit(exit_code)


@mcp.command()
@common_options
@click.pass_context
def kiro(ctx, overwrite, no_instructions, dry_run, is_global):
    """Install MCP for Kiro IDE."""
    # Get parent's dry_run if available (from either mcp group or install command)
    if not dry_run:
        if ctx.parent and ctx.parent.obj:
            dry_run = ctx.parent.obj.get("dry_run", False)
        if not dry_run and ctx.parent and ctx.parent.parent and ctx.parent.parent.obj:
            dry_run = ctx.parent.parent.obj.get("dry_run", False)

    if not dry_run:
        location = "globally" if is_global else "locally"
        click.echo(f"Installing Zenable MCP configuration for Kiro {location}...")

    exit_code = _install_mcp_for_ides(
        ctx, ["kiro"], overwrite, no_instructions, dry_run, is_global
    )

    # Handle exit code
    if ctx.parent and ctx.parent.parent:
        return exit_code
    else:
        ctx.exit(exit_code)


@mcp.command()
@common_options
@click.pass_context
def gemini(ctx, overwrite, no_instructions, dry_run, is_global):
    """Install MCP for Gemini CLI."""
    # Get parent's dry_run if available (from either mcp group or install command)
    if not dry_run:
        if ctx.parent and ctx.parent.obj:
            dry_run = ctx.parent.obj.get("dry_run", False)
        if not dry_run and ctx.parent and ctx.parent.parent and ctx.parent.parent.obj:
            dry_run = ctx.parent.parent.obj.get("dry_run", False)

    if not dry_run:
        location = "globally" if is_global else "locally"
        click.echo(f"Installing Zenable MCP configuration for Gemini CLI {location}...")

    exit_code = _install_mcp_for_ides(
        ctx, ["gemini"], overwrite, no_instructions, dry_run, is_global
    )

    # Handle exit code
    if ctx.parent and ctx.parent.parent:
        return exit_code
    else:
        ctx.exit(exit_code)


@mcp.command()
@common_options
@click.pass_context
def roo(ctx, overwrite, no_instructions, dry_run, is_global):
    """Install MCP for Roo Code."""
    # Get parent's dry_run if available (from either mcp group or install command)
    if not dry_run:
        if ctx.parent and ctx.parent.obj:
            dry_run = ctx.parent.obj.get("dry_run", False)
        if not dry_run and ctx.parent and ctx.parent.parent and ctx.parent.parent.obj:
            dry_run = ctx.parent.parent.obj.get("dry_run", False)

    if not dry_run:
        location = "globally" if is_global else "locally"
        click.echo(f"Installing Zenable MCP configuration for Roo Code {location}...")

    exit_code = _install_mcp_for_ides(
        ctx, ["roo"], overwrite, no_instructions, dry_run, is_global
    )

    # Handle exit code
    if ctx.parent and ctx.parent.parent:
        return exit_code
    else:
        ctx.exit(exit_code)


@mcp.command(name="claude")
@common_options
@click.pass_context
def claude(ctx, overwrite, no_instructions, dry_run, is_global):
    """Install MCP for Claude Code."""
    # Get parent's dry_run if available (from either mcp group or install command)
    if not dry_run:
        if ctx.parent and ctx.parent.obj:
            dry_run = ctx.parent.obj.get("dry_run", False)
        if not dry_run and ctx.parent and ctx.parent.parent and ctx.parent.parent.obj:
            dry_run = ctx.parent.parent.obj.get("dry_run", False)

    if not dry_run:
        location = "globally" if is_global else "locally"
        click.echo(
            f"Installing Zenable MCP configuration for Claude Code {location}..."
        )

    exit_code = _install_mcp_for_ides(
        ctx, ["claude-code"], overwrite, no_instructions, dry_run, is_global
    )

    # Handle exit code
    if ctx.parent and ctx.parent.parent:
        return exit_code
    else:
        ctx.exit(exit_code)


@mcp.command(name="claude-code", hidden=True)
@common_options
@click.pass_context
def claude_code(ctx, overwrite, no_instructions, dry_run, is_global):
    """Install MCP for Claude Code."""
    # Just call the claude command
    ctx.invoke(
        claude,
        overwrite=overwrite,
        no_instructions=no_instructions,
        dry_run=dry_run,
        is_global=is_global,
    )
