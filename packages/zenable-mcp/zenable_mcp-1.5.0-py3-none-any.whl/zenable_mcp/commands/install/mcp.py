import logging
from pathlib import Path
from typing import List

import click

from zenable_mcp.utils.context_helpers import (
    get_api_key_from_context,
    get_dry_run_from_context,
    get_git_repos_from_context,
    get_is_global_from_context,
    get_recursive_from_context,
)
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
from zenable_mcp.utils.operation_status import OperationStatus
from zenable_mcp.utils.recursive_operations import (
    execute_for_multiple_components,
    find_git_repositories,
)

log = logging.getLogger(__name__)


def _install_mcp_recursive(
    ctx,
    ides: List[str],
    overwrite: bool,
    no_instructions: bool,
    dry_run: bool,
    silent: bool = False,
    return_results: bool = False,
):
    """Install MCP for specified IDEs in all git repositories below current directory."""
    # Get repos from context using helper
    git_repos = get_git_repos_from_context(ctx)
    if git_repos is None:
        git_repos = find_git_repositories()
        # Store for other commands to use
        if ctx.obj:
            ctx.obj["git_repos"] = git_repos

    if not git_repos:
        if not silent:
            click.echo("No git repositories found in the current directory or below.")
        if return_results:
            return []
        return OperationStatus.NO_FILES_FOUND

    if not silent:
        click.echo(f"Found {len(git_repos)} git repositories")
        for repo in git_repos:
            log.info(f"  • {repo}")

        if dry_run:
            click.echo(
                "\n"
                + click.style("DRY RUN MODE:", fg="yellow", bold=True)
                + " Showing what would be done\n"
            )

    # Define the operation function for each repository/IDE combination
    def install_operation(
        repo_path: Path, ide_name: str, dry_run: bool
    ) -> InstallResult:
        # Get API key from context using helper
        api_key = get_api_key_from_context(ctx)
        validate_api_key(api_key, dry_run)

        return install_ide_configuration(
            ide_name,
            api_key,
            overwrite,
            dry_run,
            no_instructions,
            is_global=False,
        )

    # Execute the operation across all repos and IDEs
    all_results = execute_for_multiple_components(
        paths=git_repos,
        components=ides,
        operation_func=install_operation,
        dry_run=dry_run,
        component_type="IDEs",
        silent=silent,
    )

    if not silent:
        # Display overall summary (the utility already shows per-repo results)
        from zenable_mcp.utils.recursive_operations import _display_overall_summary

        _display_overall_summary(all_results, dry_run)

    # If asked to return results (for parent aggregation), return them
    if return_results:
        return all_results

    # Return appropriate exit code
    failed_count = sum(1 for _, r in all_results if r.is_error)
    return 1 if failed_count > 0 else 0


def _install_mcp_for_ides(
    ctx,
    ides: List[str],
    overwrite: bool,
    no_instructions: bool,
    dry_run: bool,
    is_global: bool,
) -> int:
    """Common function to install MCP for specified IDEs."""
    # Get API key from context using helper
    api_key = get_api_key_from_context(ctx)

    # Validate API key
    validate_api_key(api_key, dry_run)

    # Display what we're doing (only if not already displayed by caller)
    # The specific IDE commands already display their own message
    if not dry_run and len(ides) > 1:
        click.echo("Installing Zenable MCP configuration for all supported IDEs")

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
    f = click.option(
        "--recursive",
        is_flag=True,
        default=False,
        help="Install in all git repositories found below the current directory",
    )(f)
    return f


@click.group(
    invoke_without_command=True,
    context_settings=dict(help_option_names=["-h", "--help"]),
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Show what would be done without actually performing the installation",
)
@click.option(
    "--recursive",
    is_flag=True,
    default=False,
    help="Install in all git repositories found below the current directory",
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
def mcp(ctx, dry_run, recursive, is_global):
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
    # Check for mutual exclusivity of --global and --recursive
    if is_global and recursive:
        raise click.ClickException(
            "--global and --recursive options are mutually exclusive"
        )

    # Store dry_run, is_global and recursive in context for subcommands
    ctx.ensure_object(dict)

    # Inherit from parent context if not explicitly set
    if not dry_run and ctx.parent and ctx.parent.obj:
        dry_run = ctx.parent.obj.get("dry_run", False)
    if not is_global:
        is_global = get_is_global_from_context(ctx)

    ctx.obj["dry_run"] = dry_run
    ctx.obj["is_global"] = is_global
    ctx.obj["recursive"] = recursive

    # Pass through git_repos from parent context if available
    if ctx.parent and ctx.parent.obj and "git_repos" in ctx.parent.obj:
        ctx.obj["git_repos"] = ctx.parent.obj["git_repos"]

    # If no subcommand is provided, default to 'all'
    if ctx.invoked_subcommand is None:
        # Get parent's recursive flag if available
        if not recursive and ctx.parent and ctx.parent.obj:
            recursive = ctx.parent.obj.get("recursive", False)

        ctx.invoke(
            all_ides,
            overwrite=False,
            no_instructions=False,
            dry_run=dry_run,
            is_global=is_global,
            recursive=recursive,
        )


@mcp.command(name="all")
@common_options
@click.pass_context
def all_ides(ctx, overwrite, no_instructions, dry_run, is_global, recursive):
    """Install MCP for all supported IDEs."""
    # Check for mutual exclusivity of --global and --recursive
    if is_global and recursive:
        raise click.ClickException(
            "--global and --recursive options are mutually exclusive"
        )

    # Get flags from context hierarchy if not explicitly set
    if not dry_run:
        dry_run = get_dry_run_from_context(ctx)
    if not is_global:
        is_global = get_is_global_from_context(ctx)
    if not recursive:
        recursive = get_recursive_from_context(ctx)

    # Check if we're being called from parent install command
    from_parent_install = ctx.obj and ctx.obj.get("from_parent_install", False)

    ides = determine_ides_to_configure("all", dry_run, is_global)

    if recursive:
        result = _install_mcp_recursive(
            ctx,
            ides,
            overwrite,
            no_instructions,
            dry_run,
            silent=from_parent_install,
            return_results=from_parent_install,
        )
        # If called from parent, return results for aggregation
        if from_parent_install:
            return result
        exit_code = result
    else:
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
def cursor(ctx, overwrite, no_instructions, dry_run, is_global, recursive):
    """Install MCP for Cursor IDE."""
    # Check for mutual exclusivity of --global and --recursive
    if is_global and recursive:
        raise click.ClickException(
            "--global and --recursive options are mutually exclusive"
        )

    # Get is_global from parent if not explicitly set
    if not is_global:
        is_global = get_is_global_from_context(ctx)

    # Get flags from context hierarchy if not explicitly set
    if not dry_run:
        dry_run = get_dry_run_from_context(ctx)
    if not recursive:
        recursive = get_recursive_from_context(ctx)

    if not dry_run and not recursive:
        location = "globally" if is_global else "locally"
        click.echo(f"Installing Zenable MCP configuration for Cursor {location}...")

    if recursive:
        exit_code = _install_mcp_recursive(
            ctx, ["cursor"], overwrite, no_instructions, dry_run
        )
    else:
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
def windsurf(ctx, overwrite, no_instructions, dry_run, is_global, recursive):
    """Install MCP for Windsurf IDE."""
    # Check for mutual exclusivity of --global and --recursive
    if is_global and recursive:
        raise click.ClickException(
            "--global and --recursive options are mutually exclusive"
        )

    # Get flags from context hierarchy if not explicitly set
    if not dry_run:
        dry_run = get_dry_run_from_context(ctx)
    if not recursive:
        recursive = get_recursive_from_context(ctx)

    # Get is_global from parent if not explicitly set
    if not is_global:
        is_global = get_is_global_from_context(ctx)

    # Check if user is trying to install project-level (not global)
    if not is_global and not recursive:
        click.echo(
            f"\n{click.style('Warning:', fg='yellow', bold=True)} Windsurf does not support project-level MCP configuration.\n"
            f"Please run with --global flag to install globally:\n"
            f"  uvx zenable-mcp install mcp windsurf --global\n\n"
            f"For more information, see: https://docs.windsurf.com/windsurf/cascade/mcp#mcp-config-json"
        )
        ctx.exit(1)

    if not dry_run and not recursive:
        click.echo("Installing Zenable MCP configuration for Windsurf globally...")

    if recursive:
        # Windsurf doesn't support project-level, so skip in recursive mode
        click.echo(
            f"\n{click.style('Warning:', fg='yellow')} Skipping Windsurf in recursive mode (only supports global installation)"
        )
        return 0
    else:
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
def kiro(ctx, overwrite, no_instructions, dry_run, is_global, recursive):
    """Install MCP for Kiro IDE."""
    # Check for mutual exclusivity of --global and --recursive
    if is_global and recursive:
        raise click.ClickException(
            "--global and --recursive options are mutually exclusive"
        )

    # Get is_global from parent if not explicitly set
    if not is_global:
        is_global = get_is_global_from_context(ctx)

    # Get flags from context hierarchy if not explicitly set
    if not dry_run:
        dry_run = get_dry_run_from_context(ctx)
    if not recursive:
        recursive = get_recursive_from_context(ctx)

    if not dry_run and not recursive:
        location = "globally" if is_global else "locally"
        click.echo(f"Installing Zenable MCP configuration for Kiro {location}...")

    if recursive:
        exit_code = _install_mcp_recursive(
            ctx, ["kiro"], overwrite, no_instructions, dry_run
        )
    else:
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
def gemini(ctx, overwrite, no_instructions, dry_run, is_global, recursive):
    """Install MCP for Gemini CLI."""
    # Check for mutual exclusivity of --global and --recursive
    if is_global and recursive:
        raise click.ClickException(
            "--global and --recursive options are mutually exclusive"
        )

    # Get is_global from parent if not explicitly set
    if not is_global:
        is_global = get_is_global_from_context(ctx)

    # Get flags from context hierarchy if not explicitly set
    if not dry_run:
        dry_run = get_dry_run_from_context(ctx)
    if not recursive:
        recursive = get_recursive_from_context(ctx)

    if not dry_run and not recursive:
        location = "globally" if is_global else "locally"
        click.echo(f"Installing Zenable MCP configuration for Gemini CLI {location}...")

    if recursive:
        exit_code = _install_mcp_recursive(
            ctx, ["gemini"], overwrite, no_instructions, dry_run
        )
    else:
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
def roo(ctx, overwrite, no_instructions, dry_run, is_global, recursive):
    """Install MCP for Roo Code."""
    # Check for mutual exclusivity of --global and --recursive
    if is_global and recursive:
        raise click.ClickException(
            "--global and --recursive options are mutually exclusive"
        )

    # Get is_global from parent if not explicitly set
    if not is_global:
        is_global = get_is_global_from_context(ctx)

    # Get flags from context hierarchy if not explicitly set
    if not dry_run:
        dry_run = get_dry_run_from_context(ctx)
    if not recursive:
        recursive = get_recursive_from_context(ctx)

    if not dry_run and not recursive:
        location = "globally" if is_global else "locally"
        click.echo(f"Installing Zenable MCP configuration for Roo Code {location}...")

    if recursive:
        exit_code = _install_mcp_recursive(
            ctx, ["roo"], overwrite, no_instructions, dry_run
        )
    else:
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
def claude(ctx, overwrite, no_instructions, dry_run, is_global, recursive):
    """Install MCP for Claude Code."""
    # Check for mutual exclusivity of --global and --recursive
    if is_global and recursive:
        raise click.ClickException(
            "--global and --recursive options are mutually exclusive"
        )

    # Get is_global from parent if not explicitly set
    if not is_global:
        is_global = get_is_global_from_context(ctx)

    # Get flags from context hierarchy if not explicitly set
    if not dry_run:
        dry_run = get_dry_run_from_context(ctx)
    if not recursive:
        recursive = get_recursive_from_context(ctx)

    if not dry_run and not recursive:
        location = "globally" if is_global else "locally"
        click.echo(
            f"Installing Zenable MCP configuration for Claude Code {location}..."
        )

    if recursive:
        exit_code = _install_mcp_recursive(
            ctx, ["claude-code"], overwrite, no_instructions, dry_run
        )
    else:
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
def claude_code(ctx, overwrite, no_instructions, dry_run, is_global, recursive):
    """Install MCP for Claude Code."""
    # Just call the claude command
    ctx.invoke(
        claude,
        overwrite=overwrite,
        no_instructions=no_instructions,
        dry_run=dry_run,
        is_global=is_global,
        recursive=recursive,
    )
