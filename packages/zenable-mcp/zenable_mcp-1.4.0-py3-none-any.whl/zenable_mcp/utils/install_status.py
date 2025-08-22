"""Shared utilities for handling installation status and results."""

from enum import Enum
from typing import Dict, List, Optional, Tuple

import click

from zenable_mcp.mcp_config import create_ide_config
from zenable_mcp.utils.validation_errors import format_validation_error


class InstallStatus(Enum):
    """Installation status for a component."""

    SUCCESS = "success"  # Successfully installed
    ALREADY_INSTALLED = "already_installed"  # Already properly installed
    ALREADY_INSTALLED_UNSUPPORTED = (
        "already_installed_unsupported"  # Installed but not supported
    )
    FAILED = "failed"  # Installation failed
    SKIPPED = "skipped"  # Skipped (e.g., due to existing config without overwrite)


class InstallResult:
    """Result of an installation attempt."""

    def __init__(
        self,
        status: InstallStatus,
        component_name: str,
        message: Optional[str] = None,
        details: Optional[str] = None,
        post_install_message: Optional[str] = None,
    ):
        self.status = status
        self.component_name = component_name
        self.message = message
        self.details = details
        self.post_install_message = post_install_message

    @property
    def is_success(self) -> bool:
        """Check if the installation was successful or already properly installed."""
        return self.status in (InstallStatus.SUCCESS, InstallStatus.ALREADY_INSTALLED)

    @property
    def is_error(self) -> bool:
        """Check if the installation had an error."""
        return self.status in (
            InstallStatus.FAILED,
            InstallStatus.ALREADY_INSTALLED_UNSUPPORTED,
        )


def categorize_results(results: List[InstallResult]) -> Dict[str, List[InstallResult]]:
    """Categorize installation results by status.

    Returns:
        Dictionary with keys: 'success', 'already_installed',
        'already_installed_unsupported', 'failed', 'skipped'
    """
    categorized = {
        "success": [],
        "already_installed": [],
        "already_installed_unsupported": [],
        "failed": [],
        "skipped": [],
    }

    for result in results:
        if result.status == InstallStatus.SUCCESS:
            categorized["success"].append(result)
        elif result.status == InstallStatus.ALREADY_INSTALLED:
            categorized["already_installed"].append(result)
        elif result.status == InstallStatus.ALREADY_INSTALLED_UNSUPPORTED:
            categorized["already_installed_unsupported"].append(result)
        elif result.status == InstallStatus.FAILED:
            categorized["failed"].append(result)
        elif result.status == InstallStatus.SKIPPED:
            categorized["skipped"].append(result)

    return categorized


def show_installation_summary(
    results: List[InstallResult],
    dry_run: bool = False,
    install_type: str = "Installation",
) -> None:
    """Display the installation summary with proper categorization.

    Args:
        results: List of installation results
        dry_run: Whether this is a dry-run
        install_type: Type of installation (e.g., "MCP Installation", "Hooks Installation")
    """
    categorized = categorize_results(results)

    click.echo("\n" + "=" * 60)
    if dry_run:
        click.echo(
            click.style(f"{install_type} Preview (Dry-Run Mode)", fg="white", bold=True)
        )
    else:
        click.echo(click.style(f"{install_type} Summary", fg="white", bold=True))
    click.echo("=" * 60)

    # Show successfully installed
    if categorized["success"]:
        components = [r.component_name for r in categorized["success"]]
        if dry_run:
            click.echo(
                f"\n{click.style('• Would install:', fg='cyan', bold=True)} {', '.join(components)}"
            )
        else:
            click.echo(
                f"\n{click.style('✓ Successfully installed:', fg='green', bold=True)} {', '.join(components)}"
            )

    # Show already installed (properly)
    if categorized["already_installed"]:
        components = [r.component_name for r in categorized["already_installed"]]
        if dry_run:
            click.echo(
                f"\n{click.style('• Already installed:', fg='green', bold=True)} {', '.join(components)}"
            )
        else:
            click.echo(
                f"\n{click.style('✓ Already installed:', fg='green', bold=True)} {', '.join(components)}"
            )

    # Show already installed but unsupported
    if categorized["already_installed_unsupported"]:
        click.echo(
            f"\n{click.style('⚠ Already installed (unsupported configuration):', fg='yellow', bold=True)}"
        )
        for result in categorized["already_installed_unsupported"]:
            msg = f"  - {result.component_name}"
            if result.details:
                msg += f": {result.details}"
            click.echo(msg)

    # Show failed installations
    if categorized["failed"]:
        components = [r.component_name for r in categorized["failed"]]
        if dry_run:
            click.echo(
                f"\n{click.style('• Would fail:', fg='red', bold=True)} {', '.join(components)}"
            )
        else:
            click.echo(
                f"\n{click.style('✗ Failed:', fg='red', bold=True)} {', '.join(components)}"
            )

    # Show skipped installations
    if categorized["skipped"]:
        components = [r.component_name for r in categorized["skipped"]]
        click.echo(
            f"\n{click.style('• Skipped:', fg='yellow', bold=True)} {', '.join(components)}"
        )


def get_exit_code(results: List[InstallResult]) -> int:
    """Determine the appropriate exit code based on installation results.

    Returns:
        0 if all succeeded or were already properly installed
        1 if any had unsupported configurations or failures
        2 if mixed success/failure (partial success)
    """
    categorized = categorize_results(results)

    has_success = bool(categorized["success"] or categorized["already_installed"])
    has_unsupported = bool(categorized["already_installed_unsupported"])
    has_failures = bool(categorized["failed"])

    if has_unsupported or (has_failures and not has_success):
        return 1  # Error condition
    elif has_failures and has_success:
        return 2  # Partial success
    else:
        return 0  # Full success (including already installed)


def show_post_install_instructions(
    results: List[InstallResult], no_instructions: bool = False, dry_run: bool = False
) -> None:
    """Display post-installation instructions from results."""
    if no_instructions or dry_run:
        return

    post_install_messages = [
        r.post_install_message
        for r in results
        if r.post_install_message and r.status == InstallStatus.SUCCESS
    ]

    if post_install_messages:
        click.echo("\n" + "=" * 60)
        click.echo(click.style("Post-Installation Instructions", fg="white", bold=True))
        click.echo("=" * 60)
        for message in post_install_messages:
            click.echo(message)

        click.echo("\n" + "=" * 60)
        click.echo(click.style("Next Steps", fg="white", bold=True))
        click.echo("=" * 60)
        click.echo("\n1. Complete the setup instructions above for each IDE")
        click.echo("2. Restart your IDE(s) to load the new configuration")
        click.echo(
            "3. Visit https://docs.zenable.io/integrations/mcp/troubleshooting for help"
        )


def check_zenable_config_status(
    existing_config: Dict,
    ide_name: Optional[str] = None,
    api_key: Optional[str] = None,
) -> Tuple[bool, bool, Optional[str]]:
    """Check if Zenable configuration exists and is properly configured.

    Args:
        existing_config: The existing configuration dictionary
        ide_name: Optional IDE name for specific validation
        api_key: Optional API key for creating IDE config

    Returns:
        Tuple of (is_configured, is_compatible, details)
        - is_configured: True if Zenable is configured
        - is_compatible: True if the configuration matches expectations
        - details: Optional details about incompatible configuration
    """
    # Check if Zenable server exists
    if "mcpServers" not in existing_config:
        return False, False, None

    if "zenable" not in existing_config.get("mcpServers", {}):
        return False, False, None

    # Configuration exists, now check if it's compatible
    if ide_name and api_key:
        try:
            # Create IDE config and use its validation method
            ide_config = create_ide_config(ide_name, api_key, is_global=False)
            is_compatible = ide_config.is_config_compatible(existing_config)

            if is_compatible:
                return True, True, None

            # Try to get more specific error by validating the config
            try:
                model_class = ide_config.get_validation_model()
                zenable_config = existing_config["mcpServers"]["zenable"]
                model_class.model_validate(zenable_config)
            except Exception as e:
                return True, False, format_validation_error(e)

        except ValueError:
            # Unknown IDE, fall back to basic check
            pass

    # Fallback: Use basic Zenable MCP validation model
    from zenable_mcp.models.mcp_config import _ZenableMCPConfig

    zenable_config = existing_config["mcpServers"]["zenable"]

    try:
        # Validate using the base Zenable model
        _ZenableMCPConfig.model_validate(zenable_config)
        return True, True, None
    except Exception as e:
        return True, False, format_validation_error(e)
