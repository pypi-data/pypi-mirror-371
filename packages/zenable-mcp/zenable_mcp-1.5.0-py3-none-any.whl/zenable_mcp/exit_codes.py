"""Exit code definitions for zenable_mcp."""

from enum import IntEnum


class ExitCode(IntEnum):
    """Exit codes for zenable_mcp commands.

    These exit codes provide clear semantic meaning for different
    types of errors and outcomes that can occur during execution.
    """

    # Success codes
    SUCCESS = 0  # Command completed successfully

    # Configuration and environment errors
    MISSING_API_KEY = 1  # ZENABLE_API_KEY environment variable not set

    # Input/hook related codes
    HOOK_ADDRESS_FINDINGS = 2  # Used by handlers to instruct IDE to address findings
    HANDLER_CONFLICT = 3  # Multiple input handlers claiming they can handle

    # File and pattern errors
    NO_FILES_SPECIFIED = 10  # No files specified and none detected from context
    NO_FILES_FOUND = 11  # No files found matching specified patterns
    FILE_READ_ERROR = 12  # Error reading one or more files

    # API and network errors
    API_ERROR = 20  # Error communicating with Zenable MCP server

    # Conformance check results
    CONFORMANCE_ISSUES_FOUND = 30  # Conformance issues were detected
