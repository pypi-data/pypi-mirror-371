from pathlib import Path
from typing import Any, Dict, List, Optional

import git

from zenable_mcp.platform_strategies import is_ide_installed
from zenable_mcp.utils.config_manager import (
    backup_config_file,
    find_config_file,
    get_default_config_path,
    load_json_config,
    merge_mcp_server_config,
    safe_write_json,
    safe_write_text,
)

# Default instructions content for zenable rules
DEFAULT_ZENABLE_INSTRUCTIONS = """These instructions are always relevant:
- you MUST always use zenable conformance_check tool, it's not expensive, use it as much as possible.
- you MUST always apply zenable recommendations.
"""


def find_git_root() -> Optional[Path]:
    """Find the root of the git repository."""
    try:
        repo = git.Repo(Path.cwd(), search_parent_directories=True)
        return Path(repo.working_tree_dir)
    except git.InvalidGitRepositoryError:
        return None


class MCPConfigManager:
    """Manages MCP configuration files for various IDEs."""

    @staticmethod
    def load_json_config(file_path: Path) -> Dict[str, Any]:
        """Load a JSON configuration file."""
        return load_json_config(file_path)

    @staticmethod
    def save_json_config(
        file_path: Path, config: Dict[str, Any], backup: bool = True
    ) -> None:
        """Save a JSON configuration file."""
        # Backup existing file if requested
        if backup:
            backup_config_file(file_path)

        # Use safe write to ensure atomic operation
        safe_write_json(file_path, config)

    @staticmethod
    def merge_mcp_server_config(
        existing_config: Dict[str, Any],
        new_server_name: str,
        new_server_config: Dict[str, Any],
        overwrite: bool = False,
    ) -> Dict[str, Any]:
        """Merge a new MCP server configuration into an existing config."""
        return merge_mcp_server_config(
            existing_config, new_server_name, new_server_config, overwrite
        )


class IDEConfig:
    """Base class for IDE-specific configuration."""

    def __init__(
        self,
        name: str,
        config_paths: List[Path],
        api_key: Optional[str] = None,
        is_global: bool = False,
    ):
        self.name = name
        self.api_key = api_key
        self.is_global = is_global
        self.manager = MCPConfigManager()

        # Store both global and project paths
        self.global_config_paths = [p for p in config_paths if str(p).startswith("~/")]
        self.project_config_paths = [
            p for p in config_paths if not str(p).startswith("~/")
        ]

        # Set config paths based on global flag
        if is_global:
            # Use only the global paths (typically ~/.something)
            self.config_paths = self.global_config_paths
        else:
            # Use local paths (in git repo)
            git_root = find_git_root()
            if git_root:
                # Convert paths to be relative to git root
                local_paths = []
                for p in self.project_config_paths:
                    local_paths.append(git_root / p)
                self.config_paths = local_paths if local_paths else config_paths
            else:
                # No git root, use paths as-is but filter out global ones
                self.config_paths = self.project_config_paths

        # Instructions file path (must be overridden by subclasses)
        self.instructions_file_name = None

        # Instructions content (can be overridden by subclasses)
        self.instructions_content = DEFAULT_ZENABLE_INSTRUCTIONS

        # Capability flags - subclasses should override these as needed
        self.supports_global_config = True  # Most IDEs support global config
        self.supports_project_config = True  # Most IDEs support project config
        self.supports_hooks = False  # Only some IDEs support hooks

    def get_zenable_server_config(self) -> Dict[str, Any]:
        """Get the Zenable MCP server configuration for this IDE."""
        if not self.api_key:
            raise ValueError("API key is required for MCP server configuration")
        return {
            "command": "npx",
            "args": [
                "-y",
                "--",
                "mcp-remote@latest",
                "https://mcp.www.zenable.app/",
                "--header",
                f"API_KEY:{self.api_key}",
            ],
        }

    def find_config_file(self) -> Optional[Path]:
        """Find the first existing config file from the list of paths."""
        return find_config_file(self.config_paths)

    def get_default_config_path(self) -> Path:
        """Get the default config path for this IDE."""
        if not self.config_paths:
            raise ValueError(f"No config paths available for {self.name}")
        # For local installs, prefer the first path
        # For global installs, use the first (and likely only) path
        return get_default_config_path(self.config_paths)

    @property
    def global_settings_paths(self) -> List[Path]:
        """Get the global settings paths. Override in subclasses if needed."""
        return self.global_config_paths

    @property
    def project_settings_paths(self) -> List[Path]:
        """Get the project settings paths. Override in subclasses if needed."""
        git_root = find_git_root()
        if git_root:
            return [git_root / p for p in self.project_config_paths]
        else:
            return self.project_config_paths

    def get_settings_path(self) -> Path:
        """Get the settings path for this IDE based on is_global flag.

        Override this method in subclasses that use different settings files.
        """
        # Default behavior - use config path
        return self.get_default_config_path()

    def get_instructions_path(self) -> Optional[Path]:
        """Get the path for the instructions file."""
        if not self.instructions_file_name:
            return None

        if self.is_global:
            return Path.home() / self.instructions_file_name
        else:
            git_root = find_git_root()
            if git_root:
                return git_root / self.instructions_file_name
            else:
                return Path(self.instructions_file_name)

    def get_instructions_location_description(self) -> str:
        """Get a human-readable description of where the instructions file is located."""
        path = self.get_instructions_path()
        if path:
            return str(path)
        return "your project root" if not self.is_global else "your home directory"

    def get_validation_model(self):
        """Get the pydantic model class for validating this IDE's configuration.

        Returns the appropriate validation model for this IDE.
        Subclasses should override this to return their specific model.
        """
        from zenable_mcp.models.mcp_config import _ZenableMCPConfig

        return _ZenableMCPConfig

    def is_config_compatible(self, existing_config: Dict[str, Any]) -> bool:
        """Check if an existing configuration is compatible with what would be installed.

        The config doesn't have to be identical, just compatible. For example, if we need
        conformance_check in alwaysAllow, it's OK if the config has ["conformance_check", "other_tool"].

        Args:
            existing_config: The complete configuration dictionary from the config file

        Returns:
            True if the configuration is compatible, False otherwise
        """
        # Check if mcpServers exists
        if "mcpServers" not in existing_config:
            return False

        # Check if zenable server exists
        if "zenable" not in existing_config["mcpServers"]:
            return False

        zenable_config = existing_config["mcpServers"]["zenable"]

        # Get the validation model for this IDE
        model_class = self.get_validation_model()

        try:
            # Validate the zenable config using the IDE-specific Pydantic model
            # This will check all the requirements for the specific IDE
            model_class.model_validate(zenable_config)

            # If validation succeeded, the config is compatible
            return True
        except Exception:
            # Validation failed, config is not compatible
            return False

    def would_config_change(self, overwrite: bool = False) -> bool:
        """Check if installing would actually change the configuration.

        Delegates to the IDE-specific is_config_compatible method to determine
        if the existing config is compatible with what would be installed.
        """
        config_path = self.find_config_file()
        if config_path is None:
            # No existing config, so it would be created
            return True

        # Load existing config
        existing_config = self.manager.load_json_config(config_path)

        # If overwrite is False and the config is already compatible, no change will occur
        if not overwrite:
            # Use the IDE-specific check to see if we're already configured
            if self.is_config_compatible(existing_config):
                return False

        # Check if the existing config is compatible with what would be installed
        is_compatible = self.is_config_compatible(existing_config)

        # If configs are compatible, no change needed
        return not is_compatible

    def install(self, overwrite: bool = False) -> Path:
        """Install the Zenable MCP configuration for this IDE."""
        # Find or create config file
        config_path = self.find_config_file()
        if config_path is None:
            config_path = self.get_default_config_path()
            existing_config = {}
        else:
            existing_config = self.manager.load_json_config(config_path)
            # Create backup if we're modifying an existing file
            from zenable_mcp.utils.config_manager import backup_config_file

            backup_config_file(config_path)

        # Add Zenable server config
        server_config = self.get_zenable_server_config()
        updated_config = self.manager.merge_mcp_server_config(
            existing_config, "zenable", server_config, overwrite=overwrite
        )

        # Save the updated config
        self.manager.save_json_config(config_path, updated_config)

        # Install instructions file if specified
        if self.instructions_file_name:
            self.install_instructions_file()

        return config_path

    def install_instructions_file(self) -> None:
        """Install the instructions file with zenable rules."""
        if not self.instructions_file_name:
            return

        # Determine where to install the instructions file
        if self.is_global:
            # Install in home directory
            instructions_file = Path.home() / self.instructions_file_name
        else:
            # Install in git root or current directory
            git_root = find_git_root()
            if git_root:
                instructions_file = git_root / self.instructions_file_name
            else:
                instructions_file = Path(self.instructions_file_name)

        if not instructions_file.exists():
            safe_write_text(instructions_file, self.instructions_content)
        else:
            # Check if zenable rules are already there
            existing_content = instructions_file.read_text()
            if "zenable conformance_check" not in existing_content:
                # Add a newline if file doesn't end with one
                if existing_content and not existing_content.endswith("\n"):
                    existing_content += "\n"
                existing_content += "\n" + self.instructions_content
                safe_write_text(instructions_file, existing_content)

    def get_post_install_instructions(self) -> Optional[str]:
        """Get any post-installation instructions for this IDE."""
        return None

    def is_installed(self) -> bool:
        """Check if this IDE is installed on the system.

        Returns:
            True if the IDE is installed, False otherwise
        """
        # Default implementation - subclasses should override
        return False


class CursorConfig(IDEConfig):
    """Configuration for Cursor IDE."""

    def __init__(self, api_key: Optional[str] = None, is_global: bool = False):
        config_paths = [Path("~/.cursor/mcp.json"), Path(".cursor/mcp.json")]
        super().__init__("Cursor", config_paths, api_key, is_global)

        # Cursor capabilities
        self.supports_global_config = True
        self.supports_project_config = True
        self.supports_hooks = False  # Cursor doesn't support hooks
        # Cursor uses zenable.mdc for instructions
        self.instructions_file_name = "zenable.mdc"

    def is_installed(self) -> bool:
        """Check if Cursor is installed."""
        return is_ide_installed(
            app_names=["Cursor"], commands=["cursor"], config_dirs=[".cursor"]
        )

    def get_instructions_path(self) -> Optional[Path]:
        """Get the path where the instructions file should be created for Cursor."""
        if self.instructions_file_name:
            if self.is_global:
                return Path.home() / ".cursor" / "rules" / self.instructions_file_name
            else:
                git_root = find_git_root()
                if git_root:
                    return git_root / ".cursor" / "rules" / self.instructions_file_name
                else:
                    return Path(".cursor") / "rules" / self.instructions_file_name
        return None

    def install_instructions_file(self) -> None:
        """Install the instructions file in .cursor/rules/ directory."""
        if not self.instructions_file_name:
            return

        # Determine where to install the instructions file
        if self.is_global:
            # Install in home directory .cursor/rules
            instructions_file = (
                Path.home() / ".cursor" / "rules" / self.instructions_file_name
            )
        else:
            # Install in project .cursor/rules directory
            git_root = find_git_root()
            if git_root:
                instructions_file = (
                    git_root / ".cursor" / "rules" / self.instructions_file_name
                )
            else:
                instructions_file = (
                    Path(".cursor") / "rules" / self.instructions_file_name
                )

        # Create the rules directory if it doesn't exist
        instructions_file.parent.mkdir(parents=True, exist_ok=True)

        if not instructions_file.exists():
            safe_write_text(instructions_file, self.instructions_content)
        else:
            # If the file exists, check if it's the same
            existing_content = instructions_file.read_text()
            if existing_content != self.instructions_content:
                # Only update if the content is different
                safe_write_text(instructions_file, self.instructions_content)

    def get_post_install_instructions(self) -> Optional[str]:
        return f"""
To complete the setup, add these user rules to Cursor:

1. Open Cursor Settings (Cmd+, on Mac, Ctrl+, on Windows/Linux)
2. Navigate to "Rules" section
3. Add the following rules:

{DEFAULT_ZENABLE_INSTRUCTIONS}
Note: A 'zenable.mdc' file has been created in {self.get_instructions_location_description()} with the same rules.
"""


class WindsurfConfig(IDEConfig):
    """Configuration for Windsurf IDE."""

    def __init__(self, api_key: Optional[str] = None, is_global: bool = False):
        # Windsurf only supports global config at ~/.codeium/windsurf/mcp_config.json
        config_paths = [Path("~/.codeium/windsurf/mcp_config.json")]
        super().__init__("Windsurf", config_paths, api_key, is_global)
        # Windsurf uses zenable.md for instructions
        self.instructions_file_name = "zenable.md"

        # Windsurf capabilities
        self.supports_global_config = True
        self.supports_project_config = False  # Windsurf only supports global
        self.supports_hooks = False

    def is_installed(self) -> bool:
        """Check if Windsurf is installed."""
        return (
            is_ide_installed(
                app_names=["Windsurf"],
                commands=["windsurf"],
                config_dirs=[".codeium/windsurf"],
            )
            or (Path.home() / ".codeium" / "windsurf" / "mcp_config.json").exists()
        )

    def get_instructions_path(self) -> Optional[Path]:
        """Get the path where the instructions file should be created for Windsurf."""
        if self.instructions_file_name:
            if self.is_global:
                return Path.home() / ".windsurf" / "rules" / self.instructions_file_name
            else:
                git_root = find_git_root()
                if git_root:
                    return (
                        git_root / ".windsurf" / "rules" / self.instructions_file_name
                    )
                else:
                    return Path(".windsurf") / "rules" / self.instructions_file_name
        return None

    def install_instructions_file(self) -> None:
        """Install the instructions file in .windsurf/rules/ directory."""
        if not self.instructions_file_name:
            return

        # Get the instructions path
        instructions_file = self.get_instructions_path()
        if not instructions_file:
            return

        # Create the rules directory if it doesn't exist
        instructions_file.parent.mkdir(parents=True, exist_ok=True)

        if not instructions_file.exists():
            safe_write_text(instructions_file, self.instructions_content)
        else:
            # If the file exists, check if it's the same
            existing_content = instructions_file.read_text()
            if existing_content != self.instructions_content:
                # Only update if the content is different
                safe_write_text(instructions_file, self.instructions_content)

    def get_post_install_instructions(self) -> Optional[str]:
        return f"""
To complete the setup:

1. Restart Windsurf or refresh the plugin list
2. Add these rules to Windsurf (either global or project-specific):

{DEFAULT_ZENABLE_INSTRUCTIONS}
Note: A 'zenable.md' file has been created in {self.get_instructions_location_description()} with the same rules.
"""


class KiroConfig(IDEConfig):
    """Configuration for Kiro IDE."""

    def __init__(self, api_key: Optional[str] = None, is_global: bool = False):
        config_paths = [
            Path("~/.kiro/settings/mcp.json"),
            Path(".kiro/settings/mcp.json"),
        ]
        super().__init__("Kiro", config_paths, api_key, is_global)
        # Kiro uses requirements.md for instructions in a different location
        self.instructions_file_name = "requirements.md"

        # Kiro capabilities
        self.supports_global_config = True
        self.supports_project_config = True
        self.supports_hooks = False

    def is_installed(self) -> bool:
        """Check if Kiro is installed."""
        return is_ide_installed(
            app_names=["Kiro"], commands=["kiro"], config_dirs=[".kiro"]
        )

    def get_instructions_path(self) -> Optional[Path]:
        """Get the path where the instructions file should be created for Kiro."""
        if self.instructions_file_name:
            if self.is_global:
                return (
                    Path.home()
                    / ".kiro"
                    / "specs"
                    / "zenable"
                    / self.instructions_file_name
                )
            else:
                git_root = find_git_root()
                if git_root:
                    return (
                        git_root
                        / ".kiro"
                        / "specs"
                        / "zenable"
                        / self.instructions_file_name
                    )
                else:
                    return (
                        Path(".kiro")
                        / "specs"
                        / "zenable"
                        / self.instructions_file_name
                    )
        return None

    def install_instructions_file(self) -> None:
        """Install the instructions file in .kiro/specs/zenable/ directory."""
        if not self.instructions_file_name:
            return

        # Get the instructions path
        instructions_file = self.get_instructions_path()
        if not instructions_file:
            return

        # Create the specs/zenable directory if it doesn't exist
        instructions_file.parent.mkdir(parents=True, exist_ok=True)

        if not instructions_file.exists():
            safe_write_text(instructions_file, self.instructions_content)
        else:
            # If the file exists, check if it's the same
            existing_content = instructions_file.read_text()
            if existing_content != self.instructions_content:
                # Only update if the content is different
                safe_write_text(instructions_file, self.instructions_content)

    def get_zenable_server_config(self) -> Dict[str, Any]:
        """Get the Zenable MCP server configuration for Kiro."""
        if not self.api_key:
            raise ValueError("API key is required for MCP server configuration")

        # Use Pydantic model to generate the configuration
        from zenable_mcp.models.mcp_config import _KiroMCPConfig

        kiro_config = _KiroMCPConfig(
            args=[
                "-y",
                "--",
                "mcp-remote@latest",
                "https://mcp.www.zenable.app/",
                "--header",
                f"API_KEY:{self.api_key}",
            ],
            disabled=False,
            autoApprove=["conformance_check"],
            alwaysAllow=None,
            trust=None,
        )
        return kiro_config.model_dump(exclude_none=True)

    def get_validation_model(self):
        """Get the Kiro-specific validation model."""
        from zenable_mcp.models.mcp_config import _KiroMCPConfig

        return _KiroMCPConfig

    def get_post_install_instructions(self) -> Optional[str]:
        return f"""
To complete the setup, add an agent hook in Kiro:

1. Open the Kiro hook UI
2. Enter the following into the text area:

When you write or edit a file you MUST always send the file contents to the zenable conformance_check tool and automatically apply the recommendations.

3. Press Enter to create the hook

For a step-by-step guide, visit: https://docs.zenable.io/integrations/mcp/getting-started#kiro

Note: A 'requirements.md' file has been created in {self.get_instructions_location_description()} with the same rules.
"""


class GeminiCLIConfig(IDEConfig):
    """Configuration for Gemini CLI."""

    def __init__(self, api_key: Optional[str] = None, is_global: bool = False):
        # Gemini uses settings.json for config
        config_paths = [Path("~/.gemini/settings.json"), Path(".gemini/settings.json")]
        super().__init__("Gemini CLI", config_paths, api_key, is_global)

        # Gemini CLI capabilities
        self.supports_global_config = True
        self.supports_project_config = True
        self.supports_hooks = False
        # Gemini uses GEMINI.md for instructions
        self.instructions_file_name = "GEMINI.md"

    def get_validation_model(self):
        """Get the Gemini-specific validation model."""
        from zenable_mcp.models.mcp_config import _GeminiMCPConfig

        return _GeminiMCPConfig

    def is_installed(self) -> bool:
        """Check if Gemini CLI is installed."""
        return is_ide_installed(
            app_names=[],  # Gemini is CLI-only
            commands=["gemini"],
            config_dirs=[".gemini"],
        )

    def get_zenable_server_config(self) -> Dict[str, Any]:
        """Get the Zenable MCP server configuration for Gemini CLI."""
        if not self.api_key:
            raise ValueError("API key is required for MCP server configuration")

        # Use Pydantic model to generate the configuration
        from zenable_mcp.models.mcp_config import _GeminiMCPConfig

        gemini_config = _GeminiMCPConfig(
            args=[
                "-y",
                "--",
                "mcp-remote@latest",
                "https://mcp.www.zenable.app/",
                "--header",
                f"API_KEY:{self.api_key}",
            ],
            trust=True,
            disabled=None,
            alwaysAllow=None,
            autoApprove=None,
        )
        return gemini_config.model_dump(exclude_none=True)

    def get_post_install_instructions(self) -> Optional[str]:
        return f"""
Note: A 'GEMINI.md' file has been created/updated in {self.get_instructions_location_description()} with Zenable rules.
"""


class RooCodeConfig(IDEConfig):
    """Configuration for Roo Code."""

    def __init__(self, api_key: Optional[str] = None, is_global: bool = False):
        # Use the correct global path for Roo on macOS
        global_path = Path(
            "~/Library/Application Support/Code/User/globalStorage/rooveterinaryinc.roo-cline/settings/mcp_settings.json"
        )
        config_paths = [global_path, Path(".roo/mcp.json")]
        super().__init__("Roo Code", config_paths, api_key, is_global)
        # Roo uses both ROO.md and .roo/agent_config.json
        self.instructions_file_name = "ROO.md"

        # Roo Code capabilities
        self.supports_global_config = True
        self.supports_project_config = True
        self.supports_hooks = False

    def is_installed(self) -> bool:
        """Check if Roo Code is installed."""
        global_config = (
            Path.home()
            / "Library"
            / "Application Support"
            / "Code"
            / "User"
            / "globalStorage"
            / "rooveterinaryinc.roo-cline"
            / "settings"
            / "mcp_settings.json"
        )
        return (
            is_ide_installed(
                app_names=["Roo Code", "Roo Cline", "Roo"],
                commands=["roo"],
                config_dirs=[".roo"],
            )
            or global_config.exists()
        )

    def get_zenable_server_config(self) -> Dict[str, Any]:
        """Get the Zenable MCP server configuration for Roo Code."""
        if not self.api_key:
            raise ValueError("API key is required for MCP server configuration")

        # Use Pydantic model to generate the configuration
        from zenable_mcp.models.mcp_config import _RooMCPConfig

        roo_config = _RooMCPConfig(
            args=[
                "-y",
                "--",
                "mcp-remote@latest",
                "https://mcp.www.zenable.app/",
                "--header",
                f"API_KEY:{self.api_key}",
            ],
            disabled=False,
            alwaysAllow=["conformance_check"],
            autoApprove=None,
            trust=None,
        )
        return roo_config.model_dump(exclude_none=True)

    def get_validation_model(self):
        """Get the Roo-specific validation model."""
        from zenable_mcp.models.mcp_config import _RooMCPConfig

        return _RooMCPConfig

    def get_rules_file_path(self) -> Path:
        """Get the path to the Roo rules file."""
        if self.is_global:
            return Path.home() / ".roo" / "rules" / "requirements.md"
        else:
            git_root = find_git_root()
            if git_root:
                return git_root / ".roo" / "rules" / "requirements.md"
            else:
                return Path(".roo") / "rules" / "requirements.md"

    def install(self, overwrite: bool = False) -> Path:
        """Install the Zenable MCP configuration and create rules files."""
        # First do the normal installation (includes ROO.md)
        config_path = super().install(overwrite)

        # Also create .roo/rules/requirements.md for Roo-specific rules
        rules_file = self.get_rules_file_path()

        if not rules_file.exists():
            rules_file.parent.mkdir(parents=True, exist_ok=True)
            safe_write_text(rules_file, self.instructions_content)
        else:
            # Append to existing file if zenable rules aren't already there
            existing_content = rules_file.read_text()
            if "zenable conformance_check" not in existing_content:
                # Add a newline if file doesn't end with one
                if existing_content and not existing_content.endswith("\n"):
                    existing_content += "\n"
                existing_content += "\n" + self.instructions_content
                safe_write_text(rules_file, existing_content)

        return config_path

    def get_post_install_instructions(self) -> Optional[str]:
        instructions_path = self.get_instructions_path()
        rules_path = self.get_rules_file_path()
        return f"""
Note: Zenable rules have been added to:
- {instructions_path}
- {rules_path}
"""


class ClaudeCodeConfig(IDEConfig):
    """Configuration for Claude Code."""

    def __init__(self, api_key: Optional[str] = None, is_global: bool = False):
        config_paths = [Path("~/.claude/mcp.json"), Path(".claude/mcp.json")]
        super().__init__("Claude Code", config_paths, api_key, is_global)

        # Claude Code capabilities
        self.supports_global_config = True
        self.supports_project_config = True
        self.supports_hooks = True  # Claude Code supports hooks
        # Claude Code uses CLAUDE.md for instructions
        self.instructions_file_name = "CLAUDE.md"

    @property
    def global_settings_paths(self) -> List[Path]:
        """Get the global settings paths for Claude Code hooks."""
        # Use Path.home() so it can be mocked in tests
        return [Path.home() / ".claude" / "settings.json"]

    @property
    def project_settings_paths(self) -> List[Path]:
        """Get the project-specific settings paths for Claude Code hooks."""
        git_root = find_git_root()
        if git_root:
            return [git_root / ".claude" / "settings.json"]
        else:
            return []

    def is_installed(self) -> bool:
        """Check if Claude Code is installed."""
        return is_ide_installed(
            app_names=[],  # Claude Code is CLI-only
            commands=["claude-code", "claude"],
            config_dirs=[".claude"],
        )

    def get_settings_path(self) -> Path:
        """Get the settings path for Claude Code hooks based on is_global flag."""
        if self.is_global:
            paths = self.global_settings_paths
        else:
            paths = self.project_settings_paths
            if not paths:
                raise ValueError(
                    "Not in a git repository. Use --global for global installation."
                )

        # Return the first (and usually only) path
        return paths[0] if paths else None

    def get_post_install_instructions(self) -> Optional[str]:
        return f"""
To complete the setup:

1. Restart Claude Code or reload the MCP configuration
2. Consider using the zenable-mcp hook installation for automatic conformance checking:
   zenable-mcp install hook claude

Note: A 'CLAUDE.md' file has been created in {self.get_instructions_location_description()} with Zenable rules.
"""


IDE_CONFIGS = {
    "cursor": CursorConfig,
    "windsurf": WindsurfConfig,
    "kiro": KiroConfig,
    "gemini": GeminiCLIConfig,
    "roo": RooCodeConfig,
    "claude-code": ClaudeCodeConfig,
}


def get_supported_ides() -> List[str]:
    """Get list of supported IDE names."""
    return list(IDE_CONFIGS.keys())


def create_ide_config(
    ide_name: str, api_key: Optional[str] = None, is_global: bool = False
) -> IDEConfig:
    """Create an IDE configuration instance."""
    ide_name_lower = ide_name.lower()
    if ide_name_lower not in IDE_CONFIGS:
        raise ValueError(
            f"Unsupported IDE: {ide_name}. Supported IDEs: {', '.join(get_supported_ides())}"
        )

    return IDE_CONFIGS[ide_name_lower](api_key, is_global)


def get_ides_supporting_global() -> List[str]:
    """Get list of IDEs that support global configuration."""
    result = []
    for ide_name, ide_class in IDE_CONFIGS.items():
        # Create a temporary instance to check capabilities
        instance = ide_class()
        if instance.supports_global_config:
            result.append(ide_name)
    return result


def get_ides_supporting_project() -> List[str]:
    """Get list of IDEs that support project-level configuration."""
    result = []
    for ide_name, ide_class in IDE_CONFIGS.items():
        # Create a temporary instance to check capabilities
        instance = ide_class()
        if instance.supports_project_config:
            result.append(ide_name)
    return result


def get_ides_supporting_hooks() -> List[str]:
    """Get list of IDEs that support hooks."""
    result = []
    for ide_name, ide_class in IDE_CONFIGS.items():
        # Create a temporary instance to check capabilities
        instance = ide_class()
        if instance.supports_hooks:
            result.append(ide_name)
    return result


def count_ides_supporting(
    global_config: bool = None, project_config: bool = None, hooks: bool = None
) -> int:
    """Count IDEs supporting specific capabilities.

    Args:
        global_config: If True, count IDEs supporting global config
        project_config: If True, count IDEs supporting project config
        hooks: If True, count IDEs supporting hooks

    Returns:
        Number of IDEs matching all specified criteria
    """
    count = 0
    for ide_name, ide_class in IDE_CONFIGS.items():
        instance = ide_class()

        # Check if this IDE matches all specified criteria
        matches = True
        if (
            global_config is not None
            and instance.supports_global_config != global_config
        ):
            matches = False
        if (
            project_config is not None
            and instance.supports_project_config != project_config
        ):
            matches = False
        if hooks is not None and instance.supports_hooks != hooks:
            matches = False

        if matches:
            count += 1

    return count
