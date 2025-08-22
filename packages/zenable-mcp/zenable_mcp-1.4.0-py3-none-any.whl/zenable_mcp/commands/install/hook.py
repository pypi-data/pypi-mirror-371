"""Hook installation commands for zenable-mcp."""

import logging
import re
from pathlib import Path

import click

from zenable_mcp import __version__
from zenable_mcp.mcp_config import ClaudeCodeConfig
from zenable_mcp.utils.config_manager import (
    load_json_config,
    safe_write_json,
)
from zenable_mcp.utils.install_status import (
    InstallResult,
    InstallStatus,
    show_installation_summary,
)

logger = logging.getLogger(__name__)

# Supported matchers for the zenable-mcp hook
SUPPORTED_MATCHERS = ["Write", "Edit"]


def _load_claude_settings(settings_path: Path) -> dict:
    """Load Claude settings file, handling common edge cases.

    Args:
        settings_path: Path to the Claude settings file

    Returns:
        Dictionary of settings, or empty dict if file doesn't exist

    Raises:
        click.ClickException: If file exists but cannot be read/parsed
    """
    if not settings_path.exists():
        return {}

    try:
        return load_json_config(settings_path)
    except (ValueError, IOError) as e:
        raise click.ClickException(
            f"Failed to load Claude settings from {settings_path}: {e}"
        )


def is_supported_matcher_config(matcher: str) -> bool:
    """Check if a matcher configuration is supported for zenable-mcp.

    Args:
        matcher: The matcher string to check

    Returns:
        True if the matcher contains only Edit and/or Write (in any order)
    """
    if not isinstance(matcher, str):
        return False

    parts = [part.strip() for part in matcher.split("|")]
    # Remove empty parts
    parts = [p for p in parts if p]

    # Check if all parts are in SUPPORTED_MATCHERS
    return all(part in SUPPORTED_MATCHERS for part in parts) and len(parts) > 0


def find_git_root():
    """Find the root of the git repository"""
    current = Path.cwd()

    while current != current.parent:
        if (current / ".git").exists():
            return current
        current = current.parent

    return None


def get_settings_path(is_global: bool, find_git_root_func=None):
    """Determine the appropriate settings file path using ClaudeCodeConfig.

    Args:
        is_global: Whether to use global settings
        find_git_root_func: Function to find git root (for testing)

    Returns:
        Path to the settings file

    Raises:
        click.ClickException: If local install but not in a git repository
    """
    # For testing support, use the injected function if provided
    if find_git_root_func is not None:
        if is_global:
            return Path.home() / ".claude" / "settings.json"
        else:
            git_root = find_git_root_func()
            if not git_root:
                raise click.ClickException(
                    "Not in a git repository.\n"
                    "Did you mean to do the global installation with --global?"
                )
            return git_root / ".claude" / "settings.json"

    # Otherwise use the ClaudeCodeConfig for the proper path
    try:
        config = ClaudeCodeConfig(is_global=is_global)
        return config.get_settings_path()
    except ValueError as e:
        raise click.ClickException(str(e))


def load_or_create_settings(settings_path: Path) -> dict:
    """Load existing settings or create new empty settings.

    Args:
        settings_path: Path to the settings file

    Returns:
        Dictionary of settings

    Raises:
        click.ClickException: If JSON is invalid
    """
    if settings_path.exists() and settings_path.stat().st_size > 0:
        try:
            return load_json_config(settings_path)
        except (ValueError, IOError) as e:
            raise click.ClickException(
                f"Failed to load settings from {settings_path}\n"
                f"Details: {e}\n"
                f"Please fix the JSON syntax or backup and remove the file."
            )
    return {}


def ensure_hook_structure(settings: dict) -> None:
    """Ensure the settings have the required hook structure.

    Args:
        settings: Settings dictionary to update in place
    """
    settings.setdefault("hooks", {})
    settings["hooks"].setdefault("PostToolUse", [])


def create_hook_config(matcher: str = None) -> dict:
    """Create a standard hook configuration.

    Args:
        matcher: Optional custom matcher string. If None, uses default supported matchers.

    Returns:
        Hook configuration dictionary
    """
    if matcher is None:
        matcher = "|".join(SUPPORTED_MATCHERS)

    return {
        "matcher": matcher,
        "hooks": [{"type": "command", "command": "uvx zenable-mcp@latest check"}],
    }


def should_update_matcher(matcher: str) -> bool:
    """Check if a matcher should be updated to include both Edit and Write.

    Args:
        matcher: The matcher string to check

    Returns:
        True if the matcher should be updated
    """
    if not isinstance(matcher, str):
        return False

    parts = [part.strip() for part in matcher.split("|")]
    has_edit = "Edit" in parts
    has_write = "Write" in parts

    if (has_write and not has_edit) or (has_edit and not has_write):
        return len(parts) <= 2

    return False


def extract_command_from_hook(hook: dict) -> str:
    """Extract the command from a hook configuration.

    Args:
        hook: Hook configuration dictionary

    Returns:
        Command string or empty string if not found
    """
    if isinstance(hook, dict) and "hooks" in hook:
        for sub_hook in hook.get("hooks", []):
            if isinstance(sub_hook, dict) and sub_hook.get("type") == "command":
                return sub_hook.get("command", "")
    return ""


def analyze_existing_hooks(post_tool_use: list, new_hook_config: dict) -> dict:
    """Analyze existing hooks for duplicates and similar configurations.

    Args:
        post_tool_use: List of existing PostToolUse hooks
        new_hook_config: The new hook configuration to check against

    Returns:
        Dictionary with analysis results
    """
    result = {
        "hook_exists": False,
        "has_latest": False,
        "similar_hook_indices": [],
        "pinned_version_indices": [],
        "matcher_update_indices": [],
    }

    # Matches semantic versions in package specifications (e.g., uvx zenable-mcp@1.2.3)
    # The @ prefix is required as it's part of the package@version syntax
    semver_pattern = re.compile(
        r"@(\d+\.\d+\.\d+(?:-[a-zA-Z0-9.-]+)?(?:\+[a-zA-Z0-9.-]+)?)"
    )

    for i, existing_hook in enumerate(post_tool_use):
        if existing_hook == new_hook_config:
            result["hook_exists"] = True
            break

        command = extract_command_from_hook(existing_hook)

        if command.startswith("uvx zenable-mcp"):
            matcher = existing_hook.get("matcher", "")

            if not is_supported_matcher_config(matcher):
                click.echo(
                    f"⚠️  Warning: Hook with matcher '{matcher}' is not a supported configuration for zenable-mcp.\n"
                    f"   Supported configuration should only contain {' and '.join(SUPPORTED_MATCHERS)}.\n"
                    f"   The check may not behave as expected.",
                    err=True,
                )

            if (
                should_update_matcher(matcher)
                and i not in result["matcher_update_indices"]
            ):
                result["matcher_update_indices"].append(i)

            if "@latest" in command:
                result["has_latest"] = True
            elif semver_pattern.search(command):
                result["pinned_version_indices"].append(i)
            elif command != "uvx zenable-mcp@latest check":
                result["similar_hook_indices"].append(i)

    return result


def update_hook_matcher(hook: dict, new_matcher: str = None) -> dict:
    """Update a hook's matcher to include both Edit and Write.

    Args:
        hook: Hook configuration to update
        new_matcher: Optional new matcher. If None, updates existing.

    Returns:
        Updated hook configuration
    """
    if new_matcher:
        hook["matcher"] = new_matcher
    else:
        old_matcher = hook.get("matcher", "")
        parts = [part.strip() for part in old_matcher.split("|")]
        if "Write" not in parts:
            parts.append("Write")
        if "Edit" not in parts:
            parts.append("Edit")
        hook["matcher"] = "|".join(parts)

    return hook


def _claude_impl(is_global: bool, dry_run: bool = False, find_git_root_func=None):
    """Implementation of claude command with dependency injection.

    Args:
        is_global: Whether to install globally
        dry_run: Whether to show what would be done without making changes
        find_git_root_func: Function to find git root (for testing)

    Returns:
        InstallResult object

    Raises:
        click.ClickException: On any error
    """
    settings_path = get_settings_path(is_global, find_git_root_func)

    new_hook_config = create_hook_config()

    # Don't print here in dry-run mode - will be handled later
    if not dry_run:
        settings_path.parent.mkdir(parents=True, exist_ok=True)

    settings = load_or_create_settings(settings_path)
    ensure_hook_structure(settings)

    # Log the number of existing hooks found
    num_hooks = len(settings["hooks"].get("PostToolUse", []))
    if num_hooks > 0:
        logger.info(
            f"Found {num_hooks} existing PostToolUse hook(s) in {settings_path}"
        )
    else:
        logger.info(f"No existing PostToolUse hooks found in {settings_path}")

    post_tool_use = settings["hooks"]["PostToolUse"]
    analysis = analyze_existing_hooks(post_tool_use, new_hook_config)

    hook_exists = analysis["hook_exists"]
    has_latest = analysis["has_latest"]
    similar_hook_indices = analysis["similar_hook_indices"]
    pinned_version_indices = analysis["pinned_version_indices"]
    matcher_update_indices = analysis["matcher_update_indices"]

    # Matches semantic versions in package specifications (e.g., uvx zenable-mcp@1.2.3)
    # The @ prefix is required as it's part of the package@version syntax
    semver_pattern = re.compile(
        r"@(\d+\.\d+\.\d+(?:-[a-zA-Z0-9.-]+)?(?:\+[a-zA-Z0-9.-]+)?)"
    )

    if hook_exists:
        logger.info(f"Claude Code hook already properly installed in {settings_path}")
        return InstallResult(
            InstallStatus.ALREADY_INSTALLED,
            "Claude Code hook",
            "Hook already installed - no changes needed",
        )
    elif has_latest and not matcher_update_indices:
        logger.info(
            f"Claude Code hook with @latest already installed in {settings_path}"
        )
        return InstallResult(
            InstallStatus.ALREADY_INSTALLED,
            "Claude Code hook",
            "Hook with @latest already installed - no changes needed",
        )
    elif pinned_version_indices:
        # Found pinned version hooks - update them to current version
        updated = False
        for idx in pinned_version_indices:
            old_hook = post_tool_use[idx]
            old_command = ""
            if isinstance(old_hook, dict) and "hooks" in old_hook:
                for sub_hook in old_hook.get("hooks", []):
                    if isinstance(sub_hook, dict) and sub_hook.get("type") == "command":
                        old_command = sub_hook.get("command", "")
                        break

            # Extract the version from the command
            version_match = semver_pattern.search(old_command)
            old_version = version_match.group(1) if version_match else "unknown"

            old_matcher = old_hook.get("matcher", "")
            if should_update_matcher(old_matcher):
                post_tool_use[idx] = new_hook_config
            else:
                post_tool_use[idx] = create_hook_config(old_matcher)
            updated = True

        if updated:
            if not dry_run:
                # Save the updated settings safely
                safe_write_json(settings_path, settings)

            # Return success with appropriate message
            if old_version != __version__:
                message = f"Updated hook from pinned version ({old_version}) to @latest (current: {__version__})"
            else:
                message = f"Updated hook from pinned version ({old_version}) to @latest"

            return InstallResult(InstallStatus.SUCCESS, "Claude Code hook", message)
    elif similar_hook_indices:
        # Update similar hooks
        for idx in reversed(
            similar_hook_indices
        ):  # Reverse to maintain indices while removing
            old_hook = post_tool_use[idx]
            old_matcher = old_hook.get("matcher", "")

            if should_update_matcher(old_matcher):
                post_tool_use[idx] = new_hook_config
            else:
                post_tool_use[idx] = create_hook_config(old_matcher)

            old_command = extract_command_from_hook(old_hook)

        if not dry_run:
            # Save the updated settings safely
            safe_write_json(settings_path, settings)

        return InstallResult(
            InstallStatus.SUCCESS,
            "Claude Code hook",
            "Updated existing hook to 'uvx zenable-mcp@latest check'",
        )
    elif matcher_update_indices:
        # Update matchers for zenable-mcp hooks that need it
        # Remove any indices that were already handled in pinned_version_indices or similar_hook_indices
        remaining_matcher_indices = [
            idx
            for idx in matcher_update_indices
            if idx not in pinned_version_indices and idx not in similar_hook_indices
        ]

        if remaining_matcher_indices:
            updated_matchers = []
            for idx in remaining_matcher_indices:
                old_hook = post_tool_use[idx]
                old_matcher = old_hook.get("matcher", "")

                post_tool_use[idx] = update_hook_matcher(post_tool_use[idx])

                # Also update the command if needed
                for sub_hook in post_tool_use[idx].get("hooks", []):
                    if isinstance(sub_hook, dict) and sub_hook.get("type") == "command":
                        old_command = sub_hook.get("command", "")
                        if (
                            old_command.startswith("uvx zenable-mcp")
                            and old_command != "uvx zenable-mcp@latest check"
                        ):
                            sub_hook["command"] = "uvx zenable-mcp@latest check"

                new_matcher = post_tool_use[idx]["matcher"]
                updated_matchers.append(f"'{old_matcher}' → '{new_matcher}'")

            if not dry_run:
                # Save the updated settings safely
                safe_write_json(settings_path, settings)

            if len(updated_matchers) == 1:
                message = f"Updated matcher from {updated_matchers[0]}"
            else:
                message = f"Updated {len(updated_matchers)} matchers"

            return InstallResult(InstallStatus.SUCCESS, "Claude Code hook", message)
        else:
            # All matcher updates were handled by other scenarios, add new hook
            if not dry_run:
                post_tool_use.append(new_hook_config)
                safe_write_json(settings_path, settings)

            return InstallResult(
                InstallStatus.SUCCESS, "Claude Code hook", "Claude Code hook installed"
            )
    else:
        # Add new hook
        if not dry_run:
            post_tool_use.append(new_hook_config)
            # Save the file safely
            safe_write_json(settings_path, settings)

        return InstallResult(
            InstallStatus.SUCCESS, "Claude Code hook", "Claude Code hook installed"
        )


# Common options decorator for hook subcommands
def common_hook_options(f):
    """Decorator to add common options to all hook subcommands."""
    f = click.option(
        "--global",
        "-g",
        "is_global",
        is_flag=True,
        default=False,
        help="Install globally for all tools",
    )(f)
    f = click.option(
        "--dry-run",
        is_flag=True,
        default=False,
        help="Preview what would be done without actually performing the installation",
    )(f)
    return f


@click.group(invoke_without_command=True)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Preview what would be done without actually performing the installation",
)
@click.pass_context
def hook(ctx, dry_run):
    """Install hooks for various tools.

    \b
    Examples:
      # Install all hooks (default)
      zenable-mcp install hook
      zenable-mcp install hook all
    \b
      # Install Claude Code hook specifically
      zenable-mcp install hook claude-code
    \b
      # Preview what would be installed
      zenable-mcp install hook --dry-run
      zenable-mcp install hook claude-code --dry-run

    \b
    For more information, visit:
    https://docs.zenable.io/integrations/mcp/hooks
    """
    # Store dry_run in context for subcommands
    ctx.ensure_object(dict)
    ctx.obj["dry_run"] = dry_run

    # If no subcommand is provided, default to 'all'
    if ctx.invoked_subcommand is None:
        ctx.invoke(all_hooks)


@hook.command(name="all")
@common_hook_options
@click.pass_context
def all_hooks(ctx, is_global, dry_run):
    """Install hooks for all supported tools."""
    # Get parent's dry_run if available (from either hook group or install command)
    if not dry_run:
        if ctx.parent and ctx.parent.obj:
            dry_run = ctx.parent.obj.get("dry_run", False)
        if not dry_run and ctx.parent and ctx.parent.parent and ctx.parent.parent.obj:
            dry_run = ctx.parent.parent.obj.get("dry_run", False)

    # Execute the logic - currently only Claude Code is supported
    results = []

    try:
        # Currently only Claude Code is supported
        result = _claude_impl(is_global, dry_run)
        results.append(result)
    except click.ClickException as e:
        click.echo(f"Error installing Claude Code hook: {e}", err=True)
        results.append(
            InstallResult(InstallStatus.FAILED, "Claude Code hook", f"Failed: {e}")
        )

    # In dry-run mode, display file operations
    if dry_run and any(r.status == InstallStatus.SUCCESS for r in results):
        settings_path = get_settings_path(is_global)
        if settings_path.exists():
            click.echo(f"\n{click.style('Would modify:', fg='cyan', bold=True)}")
            click.echo(f"  • {settings_path}")
        else:
            click.echo(f"\n{click.style('Would create:', fg='cyan', bold=True)}")
            click.echo(f"  • {settings_path}")

    # Show summary
    show_installation_summary(results, dry_run, "Hooks Installation")

    # In dry-run mode, show preview message
    if dry_run and any(r.is_success for r in results):
        click.echo(
            "\nTo actually perform the installation, run the command without --dry-run"
        )

    # Return appropriate exit code
    if any(r.is_error for r in results):
        ctx.exit(1)
    else:
        return 0


@hook.command(name="claude-code")
@common_hook_options
@click.pass_context
def claude_code_hook(ctx, is_global, dry_run):
    """Install Claude Code hooks."""
    # Get parent's dry_run if available (from either hook group or install command)
    if not dry_run:
        if ctx.parent and ctx.parent.obj:
            dry_run = ctx.parent.obj.get("dry_run", False)
        if not dry_run and ctx.parent and ctx.parent.parent and ctx.parent.parent.obj:
            dry_run = ctx.parent.parent.obj.get("dry_run", False)

    results = []

    try:
        result = _claude_impl(is_global, dry_run)
        results.append(result)
    except click.ClickException as e:
        click.echo(f"Error installing Claude Code hook: {e}", err=True)
        results.append(
            InstallResult(InstallStatus.FAILED, "Claude Code hook", f"Failed: {e}")
        )

    # In dry-run mode, display file operations
    if dry_run and any(r.status == InstallStatus.SUCCESS for r in results):
        settings_path = get_settings_path(is_global)
        if settings_path.exists():
            click.echo(f"\n{click.style('Would modify:', fg='cyan', bold=True)}")
            click.echo(f"  • {settings_path}")
        else:
            click.echo(f"\n{click.style('Would create:', fg='cyan', bold=True)}")
            click.echo(f"  • {settings_path}")

    # Show summary
    show_installation_summary(results, dry_run, "Hooks Installation")

    # In dry-run mode, show preview message
    if dry_run and any(r.is_success for r in results):
        click.echo(
            "\nTo actually perform the installation, run the command without --dry-run"
        )

    # Return appropriate exit code
    if any(r.is_error for r in results):
        ctx.exit(1)
    else:
        return 0


@hook.command(name="claude")
@common_hook_options
@click.pass_context
def claude_hook(ctx, is_global, dry_run):
    """Install Claude Code hooks."""
    # Just invoke claude-code
    ctx.invoke(claude_code_hook, is_global=is_global, dry_run=dry_run)


def get_claude_settings_description() -> str:
    """Get a description of where Claude Code settings will be installed (for help text)."""
    # Create a config just to get the path
    config = ClaudeCodeConfig(is_global=False)

    # Show the global path in help text since that's what --global flag does
    global_paths = config.global_settings_paths
    if global_paths:
        return str(global_paths[0])
    else:
        return "~/.claude/settings.json"


# Additional commands for specific hook installations (kept for backward compatibility)
# These are exported separately and added as sibling commands to 'hook'
@click.command(name="hook-claude-code", hidden=True)
@click.option(
    "--global",
    "-g",
    "is_global",
    is_flag=True,
    default=False,
    help=f"Install globally in {get_claude_settings_description()} (default: False)",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Preview what would be done without actually performing the installation",
)
@click.pass_context
def claude_code(ctx, is_global, dry_run):
    """Install the Zenable hooks for Claude Code"""
    # Check if dry_run is in the parent context (from install command)
    if ctx.parent and ctx.parent.obj and "dry_run" in ctx.parent.obj:
        # Use parent's dry_run if it's set and we don't have our own
        if not dry_run:
            dry_run = ctx.parent.obj["dry_run"]

    try:
        result = _claude_impl(is_global, dry_run)
        # Show the installation summary
        show_installation_summary([result], dry_run, "Claude Code Hook Installation")
        # Return the exit code
        if result.is_error:
            ctx.exit(1)
        return 0
    except click.ClickException as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(1)


@click.command(name="hook-claude", hidden=True)
@click.option(
    "--global",
    "-g",
    "is_global",
    is_flag=True,
    default=False,
    help=f"Install globally in {get_claude_settings_description()} (default: False)",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Preview what would be done without actually performing the installation",
)
@click.pass_context
def claude(ctx, is_global, dry_run):
    """Install the Zenable hooks for Claude Code"""
    # Just calls claude_code for now
    return ctx.invoke(claude_code, is_global=is_global, dry_run=dry_run)


# Note: We name this function install_all instead of all to avoid
# shadowing Python's built-in all() function, but register it as "all"
# for the CLI command
@click.command(name="hook-all", hidden=True)
@click.option(
    "--global",
    "-g",
    "is_global",
    is_flag=True,
    default=False,
    help="Install globally for all tools (default: False)",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Preview what would be done without actually performing the installation",
)
@click.pass_context
def install_all(ctx, is_global, dry_run):
    """Install hooks for all supported tools"""
    # Check if dry_run is in the parent context (from install command)
    if ctx.parent and ctx.parent.obj and "dry_run" in ctx.parent.obj:
        # Use parent's dry_run if it's set and we don't have our own
        if not dry_run:
            dry_run = ctx.parent.obj["dry_run"]

    results = []

    try:
        # Currently only Claude Code is supported
        result = _claude_impl(is_global, dry_run)
        results.append(result)
    except click.ClickException as e:
        click.echo(f"Error installing Claude Code hook: {e}", err=True)
        results.append(
            InstallResult(InstallStatus.FAILED, "Claude Code hook", f"Failed: {e}")
        )

    # In dry-run mode, display file operations
    if dry_run and any(r.status == InstallStatus.SUCCESS for r in results):
        settings_path = get_settings_path(is_global)
        if settings_path.exists():
            click.echo(f"\n{click.style('Would modify:', fg='cyan', bold=True)}")
            click.echo(f"  • {settings_path}")
        else:
            click.echo(f"\n{click.style('Would create:', fg='cyan', bold=True)}")
            click.echo(f"  • {settings_path}")

    # Show summary
    show_installation_summary(results, dry_run, "Hooks Installation")

    # In dry-run mode, show preview message
    if dry_run and any(r.is_success for r in results):
        click.echo(
            "\nTo actually perform the installation, run the command without --dry-run"
        )

    # Return appropriate exit code
    if any(r.is_error for r in results):
        ctx.exit(1)
    else:
        return 0
