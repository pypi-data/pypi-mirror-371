import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import click
import git
from fastmcp import Client as FastMCPClient

from zenable_mcp.exceptions import APIError, ConfigurationError
from zenable_mcp.exit_codes import ExitCode
from zenable_mcp.hook_input_handlers import InputHandlerRegistry
from zenable_mcp.ide_context import IDEContextDetector, IDEType
from zenable_mcp.user_config.config_handler_factory import get_local_config_handler
from zenable_mcp.utils.files import (
    expand_file_patterns,
    filter_files_by_patterns,
    get_relative_paths,
)
from zenable_mcp.utils.zenable_config import filter_files_by_zenable_config

logger = logging.getLogger(__name__)


def process_handler_files(
    input_context,
    active_handler,
    config_patterns: Optional[List[str]],
    config_exclude_patterns: Optional[List[str]],
    exclude: Optional[List[str]],
) -> tuple[List[Path], bool, Optional[str]]:
    """
    Process files from input handlers (hooks).

    Returns:
        Tuple of (file_paths, files_from_handler, file_content_from_handler)
    """
    handler_files = input_context.files
    if not handler_files:
        logger.debug(f"No files to process from {active_handler.name}")
        return [], False, None

    files_from_handler = True

    # Apply pattern filtering if we have config patterns
    if config_patterns or config_exclude_patterns:
        # When patterns are provided, only use explicitly provided exclude patterns
        effective_exclude = list(exclude) if exclude else config_exclude_patterns
        handler_files = filter_files_by_patterns(
            handler_files,
            patterns=config_patterns,
            exclude_patterns=effective_exclude,
            handler_name=active_handler.name,
        )

        if not handler_files:
            click.echo("No files to check after filtering")
            sys.exit(ExitCode.SUCCESS)

    # Check if we have file content (e.g., from Write tool)
    file_content_from_handler = None
    if input_context.metadata.get("file_content"):
        file_content_from_handler = input_context.metadata["file_content"]

    tool_name = input_context.metadata.get("tool_name", "Unknown")
    for fp in handler_files:
        logger.debug(f"Using file from {active_handler.name} {tool_name} hook: {fp}")

    return handler_files, files_from_handler, file_content_from_handler


def detect_files_from_ide_context(base_path: Optional[Path]) -> List[Path]:
    """
    Auto-detect files from IDE context when no patterns are provided.

    Returns:
        List of file paths detected from IDE context
    """
    detector = IDEContextDetector()
    ide_type = detector.detect_context()

    if ide_type.value != "unknown":
        logger.info(f"Detected {ide_type.value} IDE context")

    env_files = detector.get_file_paths()
    if not env_files:
        logger.info("No files detected from IDE context. This could mean:")
        logger.info("  1. No modified files in the git repository")
        logger.info("  2. All modified files are filtered by .gitignore")
        logger.info("  3. All modified files are filtered by Zenable config")
        logger.info("  4. Not in a git repository")
        click.echo(
            "Error: No files specified and none detected from IDE context", err=True
        )
        click.echo(
            "Please provide file patterns or run from an IDE hook context", err=True
        )
        sys.exit(ExitCode.NO_FILES_SPECIFIED)

    # Check if we're using the fallback mechanism (most recently edited file)
    if ide_type == IDEType.UNKNOWN:
        logger.info(
            f"Auto-detected {len(env_files)} file(s) using the fallback mechanism of last modified file"
        )
        # Files are already filtered by zenable config in the fallback mechanism
        file_paths = []
        for file_str in env_files:
            file_path = Path(file_str)
            if file_path.exists():
                file_paths.append(file_path)
            else:
                click.echo(
                    f"Warning: File from IDE context not found: {file_str}",
                    err=True,
                )
        return file_paths
    else:
        logger.info(
            f"Auto-detected {len(env_files)} file(s) from {ide_type.value} IDE context"
        )
        # Convert environment file paths to Path objects
        env_file_paths = []
        for file_str in env_files:
            file_path = Path(file_str)
            if file_path.exists():
                env_file_paths.append(file_path)
            else:
                click.echo(
                    f"Warning: File from IDE context not found: {file_str}",
                    err=True,
                )

        # Filter based on zenable config using the shared utility
        files_before_filter = len(env_file_paths)
        file_paths = filter_files_by_zenable_config(env_file_paths)
        filtered_count = files_before_filter - len(file_paths)

        if filtered_count > 0:
            logger.info(
                f"Filtered out {filtered_count} file(s) based on Zenable config skip patterns"
            )

        # If all files were filtered out, provide a helpful message
        if not file_paths and filtered_count > 0:
            click.echo(
                "All files from IDE context were filtered out by Zenable config skip patterns"
            )
            click.echo("No files to check.")
            sys.exit(
                ExitCode.SUCCESS
            )  # Exit with success since this is expected behavior

        return file_paths


def create_header(*lines: str, padding: int = 8) -> str:
    """
    Create a centered header with equal signs.

    Args:
        lines: Text lines to display in the header
        padding: Number of spaces/equals on each side (default 8)

    Returns:
        Formatted header string
    """
    if not lines:
        return ""

    # Find the longest line
    max_length = max(len(line) for line in lines)

    # Total width is padding + max_length + padding
    total_width = padding * 2 + max_length

    # Build the header
    header_lines = []
    header_lines.append("=" * total_width)

    for line in lines:
        # Center each line within the available space
        centered = line.center(max_length)
        # Add padding on both sides
        header_lines.append(" " * padding + centered + " " * padding)

    header_lines.append("=" * total_width)

    return "\n".join(header_lines)


class ZenableMCPClient:
    def __init__(self, api_key: str, base_url: Optional[str] = None):
        if not api_key:
            raise ConfigurationError("API key cannot be empty")
        self.api_key = api_key
        self.base_url: str = (
            base_url
            or os.environ.get("ZENABLE_MCP_URL")
            or "https://mcp.www.zenable.app"
        )
        # Configure fastmcp client with authentication
        self.config = {
            "mcpServers": {
                "zenable": {
                    "transport": "sse",
                    "url": f"{self.base_url}/",
                    "headers": {
                        "API_KEY": self.api_key,
                        "Content-Type": "application/json",
                    },
                }
            }
        }
        self.client = None

    async def __aenter__(self):
        logger.info(f"Connecting to MCP server at {self.base_url}")
        self.client = FastMCPClient(self.config)
        await self.client.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.__aexit__(exc_type, exc_val, exc_tb)

    async def check_conformance(
        self,
        files: List[Dict[str, str]],
        batch_size: int = 5,
        ctx: click.Context = None,
    ) -> List[Dict[str, Any]]:
        """
        Call the conformance_check tool with the list of files.

        Args:
            files: List of file dictionaries with 'path' and 'content'
            batch_size: Maximum number of files to send at once (default 5, max 5)
            ctx: Click context object containing configuration

        Returns:
            List of results for each batch with files
        """
        if not self.client:
            raise APIError("Client not initialized. Use async with statement.")

        # Enforce maximum batch size of 5
        if batch_size > 5:
            batch_size = 5

        all_results = []
        total_files = len(files)
        files_processed = 0
        files_with_issues = 0

        # Process files in batches
        logger.debug(f"Processing {total_files} files in batches of {batch_size}")
        for i in range(0, total_files, batch_size):
            batch = files[i : i + batch_size]
            batch_num = (i // batch_size) + 1
            logger.debug(f"Processing batch {batch_num} with {len(batch)} files")

            # Show progress
            click.echo(
                f"\nChecking files {i + 1}-{min(i + len(batch), total_files)} of {total_files}..."
            )

            # Show which files are in this batch
            for file_dict in batch:
                file_path = Path(file_dict["path"])
                # Try to make path relative to working directory
                try:
                    rel_path = file_path.relative_to(Path.cwd())
                except ValueError:
                    # If not relative to cwd, try relative to git root
                    try:
                        repo = git.Repo(search_parent_directories=True)
                        rel_path = file_path.relative_to(repo.working_dir)
                    except Exception:
                        rel_path = file_path
                logger.info(f"  - {rel_path}")

            try:
                logger.debug(f"Calling conformance_check tool for batch {batch_num}")
                result = await self.client.call_tool(
                    "conformance_check", {"list_of_files": batch}
                )
                logger.debug(f"Received response for batch {batch_num}")

                # Store batch with its files for later processing
                batch_results = {
                    "batch": batch_num,
                    "files": batch,
                    "result": result,
                    "error": None,
                }
                all_results.append(batch_results)

                # Parse and show interim results
                if (
                    hasattr(result, "content")
                    and result.content
                    and len(result.content) > 0
                ):
                    content_text = (
                        result.content[0].text
                        if hasattr(result.content[0], "text")
                        else str(result.content[0])
                    )

                    # Try to parse the result to get file-specific information
                    try:
                        parsed_result = json.loads(content_text)
                        # Assume the result contains information about each file
                        # This structure depends on the MCP server response
                        if isinstance(parsed_result, dict):
                            # Count files with issues in this batch
                            batch_issues = 0
                            if "files" in parsed_result:
                                for file_result in parsed_result["files"]:
                                    if file_result.get("issues", []):
                                        batch_issues += 1
                            elif "issues" in parsed_result and parsed_result["issues"]:
                                batch_issues = len(batch)

                            files_with_issues += batch_issues
                            files_processed += len(batch)

                            # Show running total
                            click.echo(
                                f"Progress: {files_processed}/{total_files} files checked, {files_with_issues} with issues"
                            )
                    except (json.JSONDecodeError, KeyError):
                        files_processed += len(batch)
                        click.echo(
                            f"Progress: {files_processed}/{total_files} files checked"
                        )
                else:
                    files_processed += len(batch)
                    click.echo(
                        f"Progress: {files_processed}/{total_files} files checked"
                    )

            except Exception as e:
                # Handle errors per batch
                click.echo(f"✗ Error processing files: {e}", err=True)
                batch_results = {
                    "batch": batch_num,
                    "files": batch,
                    "result": None,
                    "error": str(e),
                }
                all_results.append(batch_results)
                files_processed += len(batch)
                files_with_issues += len(batch)  # Count errored files as having issues

        return all_results


@click.command(context_settings=dict(help_option_names=["-h", "--help"]))
@click.argument("patterns", nargs=-1, required=False)
@click.option(
    "--exclude",
    multiple=True,
    help="Patterns to exclude from checking",
)
@click.option(
    "--base-path",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    help="Base directory for pattern matching (defaults to current directory)",
)
@click.pass_context
def check(ctx, patterns, exclude, base_path):
    """Check files for conformance using patterns.

    Automatically detects files from IDE context (e.g., Claude hooks) when no patterns
    are provided. Supports glob patterns like **/*.py to check all Python files recursively.

    \b
    Examples:
      # Auto-detect from IDE context (e.g., Claude Code hooks)
      zenable-mcp check
    \b
      # Check a single file
      zenable-mcp check example.py
    \b
      # Check all Python files recursively
      zenable-mcp check '**/*.py'
    \b
      # Check multiple patterns
      zenable-mcp check 'src/**/*.js' 'tests/**/*.js'
    \b
      # Exclude test files from checking
      zenable-mcp check '**/*.py' --exclude '**/test_*.py'
    """

    api_key = ctx.obj.get("api_key", "")

    if not api_key:
        click.echo("Error: ZENABLE_API_KEY environment variable not set", err=True)
        click.echo("Please set it with: export ZENABLE_API_KEY=your-api-key", err=True)
        sys.exit(ExitCode.MISSING_API_KEY)

    # Initialize input handler registry with auto-registration
    registry = InputHandlerRegistry()

    # Detect and parse input using the registry
    try:
        input_context = registry.detect_and_parse()
        active_handler = registry.get_active_handler()
    except RuntimeError as e:
        # Multiple handlers claiming they can handle - exit with non-2 exit code
        click.echo(f"Error: {e}", err=True)
        sys.exit(ExitCode.HANDLER_CONFLICT)

    if input_context:
        logger.info(f"{active_handler.name} Input Detected")
        if input_context.raw_data:
            logger.debug(json.dumps(input_context.raw_data, indent=2))

    # Load configuration to get check patterns
    config_patterns = None
    config_exclude_patterns = None
    try:
        config_handler = get_local_config_handler()
        config, error = config_handler.load_config()

        if error:
            logger.debug(f"Error loading config: {error}, using defaults")

        # Get check patterns from config if available
        if hasattr(config, "check") and config.check:
            config_patterns = getattr(config.check, "patterns", None)
            config_exclude_patterns = getattr(config.check, "exclude_patterns", None)
    except Exception as e:
        logger.debug(f"Error loading config: {e}")

    # Determine which files to check
    file_paths = []
    files_from_handler = False
    file_content_from_handler = None

    # Display welcome header early (but not for hooks in non-debug mode)
    if not input_context:
        welcome_header = create_header(
            "Welcome to Zenable", "Production-Grade AI Coding Tools"
        )
        click.echo("\n" + welcome_header + "\n")
        click.echo("Detecting files...")

    # Determine files based on source: handler, IDE context, or CLI patterns
    if input_context and not patterns:
        # Files from handler (hook)
        file_paths, files_from_handler, file_content_from_handler = (
            process_handler_files(
                input_context,
                active_handler,
                config_patterns,
                config_exclude_patterns,
                exclude,
            )
        )
    elif not patterns:
        # Auto-detect from IDE context
        file_paths = detect_files_from_ide_context(base_path)
    else:
        # Use provided CLI patterns
        try:
            file_paths = expand_file_patterns(
                list(patterns),
                base_path=base_path,
                exclude_patterns=list(exclude) if exclude else None,
            )
        except Exception as e:
            click.echo(f"Error expanding file patterns: {e}", err=True)
            sys.exit(ExitCode.NO_FILES_FOUND)

    if not file_paths:
        click.echo("No files found matching the specified patterns", err=True)
        sys.exit(ExitCode.NO_FILES_FOUND)

    # Read file contents
    files = []

    # Special handling when we have content from handler (e.g., Write tool)
    if files_from_handler and file_content_from_handler and file_paths:
        # Use content provided by handler
        files.append({"path": str(file_paths[0]), "content": file_content_from_handler})
    else:
        # Normal file reading for all other cases
        for file_path in file_paths:
            try:
                content = file_path.read_text()
                files.append({"path": str(file_path), "content": content})
            except Exception as e:
                click.echo(f"Error reading {file_path}: {e}", err=True)
                continue

    if not files:
        click.echo("No files could be read", err=True)
        sys.exit(ExitCode.FILE_READ_ERROR)

    async def check_files():
        # Store relative paths for use in batch processing
        get_relative_paths(file_paths, base_path)

        try:
            async with ZenableMCPClient(api_key) as client:
                # Process files in batches, passing the context
                results = await client.check_conformance(files, ctx=ctx)

                # Collect all results
                all_results = []
                has_errors = False

                for batch_result in results:
                    if batch_result["error"]:
                        has_errors = True
                        all_results.append(f"Error: {batch_result['error']}")
                    else:
                        # Extract the text result from the MCP server
                        result = batch_result["result"]
                        if (
                            hasattr(result, "content")
                            and result.content
                            and len(result.content) > 0
                        ):
                            content_text = (
                                result.content[0].text
                                if hasattr(result.content[0], "text")
                                else str(result.content[0])
                            )
                            all_results.append(content_text)
                        else:
                            all_results.append("No results returned")

                # Check if we have any findings (issues)
                has_findings = False
                findings_summary = []

                for result_text in all_results:
                    if "Error:" in result_text:
                        has_findings = True
                    elif result_text != "No results returned":
                        # Try to parse the result to check for issues
                        try:
                            parsed = json.loads(result_text)
                            if isinstance(parsed, dict):
                                # Check for any non-PASS statuses
                                for file_path, file_result in parsed.items():
                                    if isinstance(file_result, dict):
                                        status = file_result.get("status", "")
                                        if status != "PASS" and status:
                                            has_findings = True
                                            findings_summary.append(result_text)
                                            break
                        except (json.JSONDecodeError, KeyError):
                            # If we can't parse it, check for common non-pass indicators
                            if any(
                                indicator in result_text
                                for indicator in [
                                    "FAIL",
                                    "ERROR",
                                    "WARNING",
                                    "Issue",
                                    "issue",
                                ]
                            ):
                                has_findings = True
                                findings_summary.append(result_text)

                # Output results based on context
                if active_handler:
                    # Use handler-specific response formatting
                    formatted_response = active_handler.build_response_to_hook_call(
                        has_findings,
                        "\n".join(findings_summary)
                        if findings_summary
                        else "\n".join(all_results),
                    )
                    if formatted_response:
                        print(formatted_response)
                        # Use handler-specific exit code
                        exit_code = active_handler.get_exit_code(has_findings)
                        sys.exit(exit_code)

                # Normal CLI mode or debug mode - display results normally
                complete_header = create_header("CONFORMANCE CHECK COMPLETE")
                click.echo("\n" + complete_header)

                # Display all results as returned by the MCP server
                if all_results:
                    for result_text in all_results:
                        click.echo("\n" + result_text)

                # Exit with appropriate code based on findings or errors
                if has_errors or has_findings:
                    sys.exit(ExitCode.CONFORMANCE_ISSUES_FOUND)

        except Exception as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(ExitCode.API_ERROR)

    asyncio.run(check_files())
