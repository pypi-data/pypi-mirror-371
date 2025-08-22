import logging
import sys
from typing import List, Optional

import click

from zenable_mcp.mcp_config import create_ide_config, get_supported_ides
from zenable_mcp.utils.install_status import (
    InstallResult,
    InstallStatus,
    check_zenable_config_status,
)

logger = logging.getLogger(__name__)


def validate_api_key(api_key: Optional[str], dry_run: bool) -> None:
    """Validate that an API key is provided when needed."""
    if not api_key and not dry_run:
        click.echo(
            click.style("Error: ", fg="red", bold=True)
            + "No API key provided. Please set ZENABLE_API_KEY environment variable.\n"
            "Visit https://zenable.io/#mcp to get your API key."
        )
        sys.exit(1)


def determine_ides_to_configure(
    ide: str, dry_run: bool, is_global: bool = False
) -> List[str]:
    """Determine which IDEs should be configured based on user input."""
    if ide == "all":
        ides_to_configure = get_supported_ides()
        if not dry_run:
            click.echo("Installing Zenable MCP configuration for all supported IDEs...")
    else:
        ides_to_configure = [ide]
        if not dry_run:
            # Get the display name for the IDE
            try:
                temp_config = create_ide_config(ide, None, is_global)
                display_name = temp_config.name
            except (ValueError, KeyError):
                display_name = ide
            location = "globally" if is_global else "locally"
            click.echo(
                f"Installing Zenable MCP configuration for {display_name} {location}..."
            )

    return ides_to_configure


def install_ide_configuration(
    ide_name: str,
    api_key: str,
    overwrite: bool,
    dry_run: bool,
    no_instructions: bool,
    is_global: bool = False,
) -> InstallResult:
    """
    Install configuration for a single IDE.
    Returns an InstallResult object with status and details.
    """
    # Initialize display_name with ide_name as fallback
    display_name = ide_name

    try:
        # Create IDE config
        ide_config = create_ide_config(ide_name, api_key, is_global)

        # Use the display name from the config
        display_name = ide_config.name

        if not dry_run:
            click.echo(f"\n{click.style('→', fg='blue')} Configuring {display_name}...")

        # Check existing configuration
        existing_config_path = ide_config.find_config_file()
        if existing_config_path:
            try:
                existing_data = ide_config.manager.load_json_config(
                    existing_config_path
                )
                is_configured, is_supported, details = check_zenable_config_status(
                    existing_data, ide_name=ide_name, api_key=api_key
                )

                if is_configured:
                    if is_supported:
                        click.echo(
                            f"  {click.style('✓', fg='green')} Already properly configured in {existing_config_path}"
                        )
                        return InstallResult(
                            status=InstallStatus.ALREADY_INSTALLED,
                            component_name=display_name,
                            message=f"Already configured in {existing_config_path}",
                        )
                    else:
                        # Configured but not supported
                        logger.info(
                            f"Found unsupported MCP configuration for {display_name} in {existing_config_path}: {details}"
                        )
                        if not overwrite:
                            if dry_run:
                                click.echo(
                                    f"  {click.style('⚠', fg='yellow')} Would skip: {existing_config_path} (unsupported configuration)"
                                )
                            else:
                                click.echo(
                                    f"  {click.style('⚠', fg='yellow')} Unsupported configuration in {existing_config_path}"
                                )
                                if details:
                                    click.echo(f"    Details: {details}")
                                click.echo(
                                    "    Use --overwrite to update to supported configuration"
                                )
                            return InstallResult(
                                status=InstallStatus.ALREADY_INSTALLED_UNSUPPORTED,
                                component_name=display_name,
                                message=f"Unsupported configuration in {existing_config_path}",
                                details=details,
                            )
                        # Will overwrite unsupported configuration
                        if dry_run:
                            click.echo(
                                f"  {click.style('•', fg='cyan')} Would overwrite unsupported configuration: {existing_config_path}"
                            )
            except Exception:
                # Error reading config, proceed with installation
                pass

        # Install configuration (or show what would be done)
        if dry_run:
            config_path = ide_config.get_default_config_path()
            if not existing_config_path:
                logger.info(
                    f"No existing MCP configuration found for {display_name}, would create new configuration at: {config_path}"
                )
            # Don't print here - just return the result with details
            if existing_config_path:
                # Check if the configuration would actually change
                would_change = ide_config.would_config_change(overwrite=overwrite)

                if not would_change:
                    action = "unchanged"
                elif overwrite:
                    action = "overwrite"
                else:
                    action = "update"
                path = existing_config_path
            else:
                action = "create"
                path = config_path
            return InstallResult(
                status=InstallStatus.SUCCESS,
                component_name=display_name,
                message=f"Would install to {config_path}",
                details=f"{action}:{path}",  # Store action:path for later processing
            )
        else:
            if not existing_config_path:
                config_path = ide_config.get_default_config_path()
                logger.info(
                    f"No existing MCP configuration found for {display_name}, creating new configuration at: {config_path}"
                )
            else:
                logger.info(
                    f"Updating existing MCP configuration for {display_name} at: {existing_config_path}"
                )
            config_path = ide_config.install(overwrite=overwrite)
            logger.info(
                f"Successfully installed MCP configuration for {display_name} at: {config_path}"
            )
            click.echo(
                f"  {click.style('✓', fg='green')} Configuration saved to: {config_path}"
            )

            # Collect post-install instructions
            post_install_message = None
            instructions = ide_config.get_post_install_instructions()
            if instructions and not no_instructions:
                post_install_message = f"\n{click.style(f'{display_name.upper()} Setup:', fg='cyan', bold=True)}{instructions}"

            return InstallResult(
                status=InstallStatus.SUCCESS,
                component_name=display_name,
                message=f"Configuration saved to {config_path}",
                post_install_message=post_install_message,
            )

    except FileNotFoundError as e:
        if dry_run:
            click.echo(
                f"  {click.style('✗', fg='red')} Would fail: Configuration directory not found: {e}"
            )
        else:
            click.echo(
                f"  {click.style('✗', fg='red')} Configuration directory not found: {e}"
            )
        return InstallResult(
            status=InstallStatus.FAILED,
            component_name=display_name,
            message="Directory not found",
            details=str(e),
        )
    except PermissionError as e:
        if dry_run:
            click.echo(
                f"  {click.style('✗', fg='red')} Would fail: Permission denied: {e}"
            )
        else:
            click.echo(f"  {click.style('✗', fg='red')} Permission denied: {e}")
        return InstallResult(
            status=InstallStatus.FAILED,
            component_name=display_name,
            message="Permission denied",
            details=str(e),
        )
    except Exception as e:
        if dry_run:
            click.echo(f"  {click.style('✗', fg='red')} Would fail: {e}")
        else:
            click.echo(f"  {click.style('✗', fg='red')} Failed: {e}")
        return InstallResult(
            status=InstallStatus.FAILED,
            component_name=display_name,
            message="Installation failed",
            details=str(e),
        )
