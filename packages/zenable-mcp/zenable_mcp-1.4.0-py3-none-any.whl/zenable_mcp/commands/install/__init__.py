"""Install command group for zenable-mcp."""

import signal
import sys

import click

from zenable_mcp.commands.install.hook import hook
from zenable_mcp.commands.install.mcp import mcp
from zenable_mcp.utils.config_manager import cleanup_temp_files


def signal_handler(signum, frame):
    """Handle interrupt signals gracefully."""
    click.echo("\n⚠️  Installation interrupted by user", err=True)
    cleanup_temp_files()
    sys.exit(130)  # Standard exit code for SIGINT


@click.group(invoke_without_command=True)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Preview what would be done without actually performing the installation",
)
@click.pass_context
def install(ctx, dry_run):
    """Install zenable-mcp integrations"""
    # Set up signal handler for graceful interruption
    signal.signal(signal.SIGINT, signal_handler)
    # Also handle SIGTERM for completeness
    signal.signal(signal.SIGTERM, signal_handler)

    # Store dry_run in context for subcommands
    ctx.ensure_object(dict)
    ctx.obj["dry_run"] = dry_run

    # If no subcommand is provided, run both mcp all and hook all
    if ctx.invoked_subcommand is None:
        if not dry_run:
            click.echo("Installing all zenable-mcp integrations...")

        # Run mcp with dry_run flag if provided (defaults to all IDEs)
        if not dry_run:
            click.echo("\nInstalling MCP for all IDEs...")
        ctx.invoke(mcp, dry_run=dry_run)

        # Run hook with dry_run flag if provided (defaults to all)
        ctx.invoke(hook, dry_run=dry_run)


install.add_command(hook)
install.add_command(mcp)

# Export signal_handler for testing
__all__ = ["install", "mcp", "signal_handler"]
