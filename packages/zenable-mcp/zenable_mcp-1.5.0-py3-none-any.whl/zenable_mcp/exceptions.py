"""Custom exceptions for zenable_mcp."""

from typing import List, Optional

from zenable_mcp.exit_codes import ExitCode


class ZenableMCPError(Exception):
    """Base exception for all zenable_mcp errors.

    Attributes:
        exit_code: The exit code to use when this error causes program termination
        message: The error message
    """

    exit_code: ExitCode = ExitCode.SUCCESS

    def __init__(self, message: str, exit_code: Optional[ExitCode] = None):
        super().__init__(message)
        if exit_code is not None:
            self.exit_code = exit_code


class ConfigurationError(ZenableMCPError):
    """Raised when there are configuration issues."""

    exit_code = ExitCode.MISSING_API_KEY


class HandlerConflictError(ZenableMCPError):
    """Raised when multiple input handlers claim they can handle the input.

    Attributes:
        conflicting_handlers: List of handler names that are in conflict
    """

    exit_code = ExitCode.HANDLER_CONFLICT

    def __init__(self, handlers: List[str]):
        self.conflicting_handlers = handlers
        handler_names = " or ".join(handlers)
        super().__init__(f"Unable to identify which handler to use: {handler_names}")


class HandlerEnvironmentError(ZenableMCPError):
    """Raised when a handler detects it's not in the appropriate environment.

    This is used when handlers like ClaudeCodeInputHandler
    detect they're not running in their expected environment.
    """

    def __init__(self, handler_name: str, reason: str):
        super().__init__(f"{handler_name}: {reason}")


class FileOperationError(ZenableMCPError):
    """Base class for file-related errors."""

    exit_code = ExitCode.FILE_READ_ERROR


class NoFilesSpecifiedError(FileOperationError):
    """Raised when no files are specified and none can be detected from context."""

    exit_code = ExitCode.NO_FILES_SPECIFIED

    def __init__(self):
        super().__init__("No files specified and none detected from context")


class NoFilesFoundError(FileOperationError):
    """Raised when no files are found matching the specified patterns."""

    exit_code = ExitCode.NO_FILES_FOUND

    def __init__(self, patterns: Optional[List[str]] = None):
        if patterns:
            message = f"No files found matching patterns: {', '.join(patterns)}"
        else:
            message = "No files found matching specified patterns"
        super().__init__(message)


class FileReadError(FileOperationError):
    """Raised when there's an error reading a file."""

    exit_code = ExitCode.FILE_READ_ERROR

    def __init__(self, file_path: str, reason: str):
        super().__init__(f"Error reading file {file_path}: {reason}")


class APIError(ZenableMCPError):
    """Raised when there's an error communicating with the Zenable MCP server."""

    exit_code = ExitCode.API_ERROR

    def __init__(self, message: str):
        super().__init__(f"API error: {message}")


class ConformanceError(ZenableMCPError):
    """Raised when conformance issues are found."""

    exit_code = ExitCode.CONFORMANCE_ISSUES_FOUND

    def __init__(self, issues_count: int):
        super().__init__(f"Found {issues_count} conformance issue(s)")


class ParserError(ZenableMCPError):
    """Raised when there's an error parsing a file or configuration."""

    def __init__(self, file_path: str, reason: str):
        super().__init__(f"Failed to parse {file_path}: {reason}")
