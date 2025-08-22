"""Shared configuration management utilities for safe JSON file operations."""

import json
import logging
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import click

logger = logging.getLogger(__name__)

# Global variable to track temporary files for cleanup
_temp_files_to_cleanup: List[Path] = []


def cleanup_temp_files() -> None:
    """Clean up any temporary .zenable files that were created."""
    global _temp_files_to_cleanup
    for temp_file in _temp_files_to_cleanup:
        if temp_file.exists():
            try:
                temp_file.unlink()
                click.echo(f"Cleaned up temporary file: {temp_file}", err=True)
            except OSError:
                pass  # Best effort cleanup
    _temp_files_to_cleanup.clear()


def safe_write_text(file_path: Path, content: str) -> None:
    """Safely write text content using a .zenable temporary file.

    This function writes to a temporary file first and then atomically
    renames it to the target path, ensuring data integrity even if the
    process is interrupted.

    Args:
        file_path: Path to the target file
        content: Text content to write

    Raises:
        click.ClickException: On any write error
    """
    global _temp_files_to_cleanup

    # Write to .zenable file first
    zenable_path = file_path.with_suffix(file_path.suffix + ".zenable")

    # Track the temp file for cleanup
    _temp_files_to_cleanup.append(zenable_path)

    try:
        # Ensure parent directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Write content to temp file
        with open(zenable_path, "w") as f:
            f.write(content)

        # Atomically rename to target
        zenable_path.rename(file_path)

        # Remove from cleanup list since it's been renamed
        _temp_files_to_cleanup.remove(zenable_path)

        logger.info(f"Successfully wrote file to {file_path}")

    except Exception as e:
        # Clean up temp file if it exists
        if zenable_path.exists():
            zenable_path.unlink()
        raise click.ClickException(f"Failed to write {file_path}: {e}")


def safe_write_json(settings_path: Path, settings: dict) -> None:
    """Safely write JSON settings using a .zenable temporary file.

    This function writes to a temporary file first and then atomically
    renames it to the target path, ensuring data integrity even if the
    process is interrupted.

    Args:
        settings_path: Path to the settings file
        settings: Dictionary to write as JSON

    Raises:
        click.ClickException: On any write error
    """
    global _temp_files_to_cleanup

    # Write to .zenable file first
    zenable_path = settings_path.with_suffix(".json.zenable")

    # Track the temp file for cleanup
    _temp_files_to_cleanup.append(zenable_path)

    try:
        # Ensure parent directory exists
        settings_path.parent.mkdir(parents=True, exist_ok=True)

        # Test write permissions and disk space
        with open(zenable_path, "w") as f:
            json.dump(settings, f, indent=2)
            f.write("\n")
            f.flush()  # Ensure data is written
            os.fsync(f.fileno())  # Force write to disk

        # Atomic rename (on POSIX systems)
        zenable_path.replace(settings_path)

        # Remove from cleanup list after successful rename
        if zenable_path in _temp_files_to_cleanup:
            _temp_files_to_cleanup.remove(zenable_path)

        logger.info(f"Successfully wrote configuration to {settings_path}")

    except OSError as e:
        # Clean up zenable file on error
        if zenable_path.exists():
            try:
                zenable_path.unlink()
                # Remove from cleanup list after manual cleanup
                if zenable_path in _temp_files_to_cleanup:
                    _temp_files_to_cleanup.remove(zenable_path)
            except OSError:
                pass  # Best effort cleanup

        error_msg = f"Failed to write settings to {settings_path}: {e}"

        # Check for specific error conditions
        if "No space left on device" in str(e):
            error_msg += "\nDisk is full. Please free up space and try again."
        elif "Permission denied" in str(e):
            error_msg += (
                "\nInsufficient permissions. Check file and directory permissions."
            )

        raise click.ClickException(error_msg)

    except (TypeError, ValueError) as e:
        # Clean up zenable file on error
        if zenable_path.exists():
            try:
                zenable_path.unlink()
                # Remove from cleanup list after manual cleanup
                if zenable_path in _temp_files_to_cleanup:
                    _temp_files_to_cleanup.remove(zenable_path)
            except OSError:
                pass

        raise click.ClickException(
            f"Failed to serialize settings to JSON for {settings_path}: {e}"
        )


def load_json_config(file_path: Path) -> Dict[str, Any]:
    """Load a JSON configuration file.

    Args:
        file_path: Path to the JSON file

    Returns:
        Dictionary containing the parsed JSON data, or empty dict if file doesn't exist

    Raises:
        ValueError: If the JSON is invalid
        IOError: If there's an error reading the file
    """
    if not file_path.exists():
        return {}

    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {file_path}: {e}")
    except Exception as e:
        raise IOError(f"Error reading {file_path}: {e}")


def merge_mcp_server_config(
    existing_config: Dict[str, Any],
    new_server_name: str,
    new_server_config: Dict[str, Any],
    overwrite: bool = False,
) -> Dict[str, Any]:
    """Merge a new MCP server configuration into an existing config.

    Args:
        existing_config: The existing configuration dictionary
        new_server_name: Name of the new server to add
        new_server_config: Configuration for the new server
        overwrite: Whether to overwrite if server already exists

    Returns:
        Updated configuration dictionary

    Raises:
        ValueError: If server already exists and overwrite is False
    """
    if "mcpServers" not in existing_config:
        existing_config["mcpServers"] = {}

    if new_server_name in existing_config["mcpServers"] and not overwrite:
        raise ValueError(
            f"Server '{new_server_name}' already exists in configuration. "
            "Use --overwrite to replace it."
        )

    existing_config["mcpServers"][new_server_name] = new_server_config
    return existing_config


def backup_config_file(file_path: Path) -> Optional[Path]:
    """Create a backup of a configuration file in the system temp directory.

    Args:
        file_path: Path to the file to backup

    Returns:
        Path to the backup file if created, None if original doesn't exist

    Raises:
        IOError: If backup fails
    """
    if not file_path.exists():
        return None

    # Create backup filename with UTC timestamp
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_UTC")
    original_name = file_path.name
    backup_name = f"{original_name}_{timestamp}.bkp"

    # Get system temp directory
    temp_dir = Path(tempfile.gettempdir())
    backup_path = temp_dir / backup_name

    try:
        import shutil

        shutil.copy2(file_path, backup_path)

        logger.info(f"Created backup: {backup_path}")
        logger.info(f"  Original file: {file_path}")
        logger.info(f"  Backup location: {temp_dir}")

        return backup_path
    except Exception as e:
        raise IOError(f"Failed to create backup of {file_path}: {e}")


def find_config_file(config_paths: List[Path]) -> Optional[Path]:
    """Find the first existing config file from a list of paths.

    Args:
        config_paths: List of potential configuration file paths

    Returns:
        First existing path, or None if none exist
    """
    for path in config_paths:
        expanded_path = Path(str(path)).expanduser()
        if expanded_path.exists():
            return expanded_path
    return None


def get_default_config_path(config_paths: List[Path]) -> Path:
    """Get the default (first) config path from a list.

    Args:
        config_paths: List of potential configuration file paths

    Returns:
        The first path, expanded with ~ resolved
    """
    if not config_paths:
        raise ValueError("No config paths provided")

    return Path(str(config_paths[0])).expanduser()
