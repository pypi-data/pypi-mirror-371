"""Install command group for zenable-mcp."""

import signal
import sys

import click

from zenable_mcp.commands.install.hook import all_hooks, hook
from zenable_mcp.commands.install.mcp import all_ides, mcp
from zenable_mcp.utils.config_manager import cleanup_temp_files
from zenable_mcp.utils.context_helpers import get_is_global_from_context
from zenable_mcp.utils.recursive_operations import (
    display_aggregated_results,
    find_git_repositories,
)


def signal_handler(signum, frame):
    """Handle interrupt signals gracefully."""
    click.echo("\n⚠️  Installation interrupted by user", err=True)
    cleanup_temp_files()
    sys.exit(130)  # Standard exit code for SIGINT


@click.group(
    invoke_without_command=True,
    context_settings=dict(help_option_names=["-h", "--help"]),
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Preview what would be done without actually performing the installation",
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
def install(ctx, dry_run, recursive, is_global):
    """Install zenable-mcp integrations"""
    # Set up signal handler for graceful interruption
    signal.signal(signal.SIGINT, signal_handler)
    # Also handle SIGTERM for completeness
    signal.signal(signal.SIGTERM, signal_handler)

    # Store dry_run, global, and recursive in context for subcommands
    ctx.ensure_object(dict)
    ctx.obj["dry_run"] = dry_run
    ctx.obj["is_global"] = is_global
    ctx.obj["recursive"] = recursive

    # If recursive, find repositories once and store them in context
    if recursive:
        git_repos = find_git_repositories()
        ctx.obj["git_repos"] = git_repos

    # If no subcommand is provided, run both mcp all and hook all
    if ctx.invoked_subcommand is None:
        if recursive:
            # Handle recursive installation with aggregated output
            click.echo("Installing all of the Zenable integrations recursively...")
            if git_repos := ctx.obj.get("git_repos"):
                click.echo(f"Found {len(git_repos)} git repositories")

            if dry_run:
                click.echo(
                    "\n"
                    + click.style("DRY RUN MODE:", fg="yellow", bold=True)
                    + " Showing what would be done\n"
                )

            # Set flag so subcommands know they're being called from parent
            ctx.obj["from_parent_install"] = True

            # Call subcommands and get results
            mcp_results = ctx.invoke(
                all_ides,
                overwrite=False,
                no_instructions=True,
                dry_run=dry_run,
                recursive=recursive,
                is_global=is_global,
            )
            hook_results = ctx.invoke(
                all_hooks, is_global=is_global, dry_run=dry_run, recursive=recursive
            )

            # Ensure results are lists
            if not isinstance(mcp_results, list):
                mcp_results = []
            if not isinstance(hook_results, list):
                hook_results = []

            # Display aggregated results
            display_aggregated_results(
                mcp_results=mcp_results,
                hook_results=hook_results,
                dry_run=dry_run,
            )

            # Calculate exit code
            all_results = []
            if mcp_results:
                all_results.extend(mcp_results)
            if hook_results:
                all_results.extend(hook_results)

            failed_count = sum(1 for _, r in all_results if r.is_error)
            exit_code = 1 if failed_count > 0 else 0

            # Exit with the appropriate code
            ctx.exit(exit_code)
        else:
            # Non-recursive installation
            if not dry_run:
                # Check if we're being called with --global from parent
                is_global = get_is_global_from_context(ctx)
                if is_global:
                    click.echo("Installing all of the Zenable integrations globally...")
                else:
                    click.echo("Installing all of the Zenable integrations...")

            if not dry_run:
                click.echo("\nInstalling MCP for all IDEs...")

            ctx.invoke(mcp, dry_run=dry_run, recursive=recursive, is_global=is_global)
            ctx.invoke(hook, dry_run=dry_run, recursive=recursive)


install.add_command(hook)
install.add_command(mcp)

# Export signal_handler for testing
__all__ = ["install", "mcp", "signal_handler"]
