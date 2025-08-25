"""Comprehensive streaming display manager for interleaved tool calls and text output."""

import json
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from rich.console import Console, Group
from rich.syntax import Syntax
from rich.text import Text


class OutputType(Enum):
    """Types of output sections."""

    TEXT = "text"
    TOOL_CALL = "tool_call"
    TOOL_OUTPUT = "tool_output"


@dataclass
class ToolCallTracker:
    """Track a tool call and its associated data."""

    tool_name: str
    call_id: Optional[str] = None
    inputs: Optional[Dict[str, Any]] = None
    output: Optional[str] = None
    completed: bool = False


@dataclass
class OutputSection:
    """Represents a section of output (text or tool)."""

    type: OutputType
    content: str = ""
    tool_tracker: Optional[ToolCallTracker] = None
    complete: bool = False


class StreamingDisplayManager:
    """Manages the state and display of streaming output with interleaved tool calls and text."""

    def __init__(self, console: Console):
        self.console = console

        # State tracking
        self.pending_tool_calls = 0  # Counter for tool calls awaiting outputs
        self.sections: List[OutputSection] = []  # All output sections in order
        self.current_text_section: Optional[OutputSection] = None
        self.active_tool_calls: Dict[str, ToolCallTracker] = {}  # Track by call_id

        # Text streaming by output_index
        self.text_streams: Dict[int, str] = {}

        # Display state
        self.display_lines: List[str] = []

    def handle_text_delta(self, output_index: int, delta_text: str) -> bool:
        """
        Handle streaming text delta. Returns True if display should be updated.
        """
        if delta_text:
            # Initialize stream if needed
            if output_index not in self.text_streams:
                self.text_streams[output_index] = ""

            # Append delta
            self.text_streams[output_index] += delta_text

            # If no pending tool calls, we can stream this text immediately
            if self.pending_tool_calls == 0:
                self._ensure_current_text_section()
                # Use only the current accumulated text (fresh start after tools)
                if self.current_text_section is not None:
                    self.current_text_section.content = "".join(self.text_streams.values())
                return True
            else:
                # If tools are pending, don't display text yet - just accumulate
                return False

        return False

    def handle_tool_called(self, tool_call_item, call_id: Optional[str] = None) -> bool:
        """
        Handle tool call event from ToolCallItem. Returns True if display should be updated.
        """
        # Extract tool information from the item
        if hasattr(tool_call_item, "raw_item") and hasattr(tool_call_item.raw_item, "name"):
            tool_name = tool_call_item.raw_item.name

            # Extract inputs from arguments if available
            inputs = None
            if hasattr(tool_call_item.raw_item, "arguments"):
                try:
                    import json

                    inputs = json.loads(tool_call_item.raw_item.arguments)
                except Exception:
                    inputs = {"arguments": tool_call_item.raw_item.arguments}

            # Use tool call ID if available - try multiple attributes
            actual_call_id = (
                getattr(tool_call_item.raw_item, "call_id", None)
                or getattr(tool_call_item.raw_item, "id", None)
                or call_id
                or tool_name
            )
        else:
            tool_name = str(tool_call_item)
            inputs = None
            actual_call_id = call_id or tool_name

        # Increment pending counter
        self.pending_tool_calls += 1

        # Create tool tracker
        tracker = ToolCallTracker(tool_name=tool_name, call_id=actual_call_id, inputs=inputs)

        # Store tracker
        self.active_tool_calls[actual_call_id] = tracker

        # Finalize current text section if any and clear text streams
        if self.current_text_section and self.current_text_section.content.strip():
            self.current_text_section.complete = True

        # Reset current text section so new text after tools will start fresh
        self.current_text_section = None

        # Clear text streams when starting tool calls - we'll start fresh after tools complete
        self.text_streams.clear()

        # Create a preliminary tool call section for immediate feedback
        tool_section = OutputSection(type=OutputType.TOOL_CALL, tool_tracker=tracker)
        self.sections.append(tool_section)

        return True  # Allow display update for immediate tool call feedback

    def handle_tool_output(self, tool_output_item, call_id: Optional[str] = None) -> bool:
        """
        Handle tool output event from ToolCallOutputItem. Returns True if display should be updated.
        """
        # Extract output information from the item
        output = ""
        actual_call_id = call_id

        # Try multiple ways to extract output
        if hasattr(tool_output_item, "output"):
            output = str(tool_output_item.output)
        elif hasattr(tool_output_item, "raw_item"):
            if hasattr(tool_output_item.raw_item, "output"):
                output = str(tool_output_item.raw_item.output)
            elif (
                isinstance(tool_output_item.raw_item, dict)
                and "output" in tool_output_item.raw_item
            ):
                output = str(tool_output_item.raw_item["output"])

        # Try multiple ways to extract call_id
        if hasattr(tool_output_item, "tool_call_id"):
            actual_call_id = tool_output_item.tool_call_id
        elif hasattr(tool_output_item, "raw_item"):
            if isinstance(tool_output_item.raw_item, dict):
                actual_call_id = tool_output_item.raw_item.get(
                    "call_id"
                ) or tool_output_item.raw_item.get("tool_call_id")
            elif hasattr(tool_output_item.raw_item, "call_id"):
                actual_call_id = tool_output_item.raw_item.call_id
            elif hasattr(tool_output_item.raw_item, "tool_call_id"):
                actual_call_id = tool_output_item.raw_item.tool_call_id

        # Find the tracker - multiple strategies
        tracker = None

        # Strategy 1: Exact call_id match
        if actual_call_id and actual_call_id in self.active_tool_calls:
            tracker = self.active_tool_calls[actual_call_id]

        # Strategy 2: Find oldest uncompleted tracker (FIFO)
        if not tracker:
            oldest_time = float("inf")
            for call_id, t in self.active_tool_calls.items():
                if not t.completed:
                    # Use list index as rough timestamp
                    for i, section in enumerate(self.sections):
                        if (
                            section.type == OutputType.TOOL_CALL
                            and section.tool_tracker
                            and section.tool_tracker.call_id == call_id
                        ):
                            if i < oldest_time:
                                oldest_time = i
                                tracker = t
                            break

        if tracker:
            tracker.output = output
            tracker.completed = True

            # Find the position of the corresponding tool call section
            tool_call_index = -1
            for i, section in enumerate(self.sections):
                if (
                    section.type == OutputType.TOOL_CALL
                    and section.tool_tracker
                    and section.tool_tracker.call_id == tracker.call_id
                ):
                    section.complete = True
                    tool_call_index = i
                    break

            # Create tool output section
            output_section = OutputSection(
                type=OutputType.TOOL_OUTPUT, content=output, tool_tracker=tracker, complete=True
            )

            # Insert output section right after the corresponding tool call
            if tool_call_index != -1:
                # Insert after the tool call section (at position tool_call_index + 1)
                self.sections.insert(tool_call_index + 1, output_section)
            else:
                # Fallback: append to end if tool call section not found
                self.sections.append(output_section)

            # Decrement pending counter
            self.pending_tool_calls = max(0, self.pending_tool_calls - 1)

            # If no more pending tools, prepare for NEW text output (start fresh)
            if self.pending_tool_calls == 0:
                # Clear accumulated text streams and reset current text section
                self.text_streams.clear()
                self.current_text_section = None  # Force creation of new text section

            return True

        return False

    def _ensure_current_text_section(self):
        """Ensure there's a current text section for streaming."""
        if not self.current_text_section or self.current_text_section.complete:
            self.current_text_section = OutputSection(type=OutputType.TEXT)
            self.sections.append(self.current_text_section)

    def get_display_content(self) -> Union[Group, Text]:
        """Generate the current display content as a string for Rich Live compatibility."""
        renderables = []

        for i, section in enumerate(self.sections):
            if section.type == OutputType.TEXT:
                if section.content.strip():
                    # Add spacing between sections
                    if renderables:
                        renderables.append(Text())

                    # Convert markdown to formatted text for more compact display
                    try:
                        content = section.content.strip()
                        formatted_renderables = self._format_markdown_content(content)
                        renderables.extend(formatted_renderables)
                    except Exception:
                        # Fallback to plain text
                        renderables.append(Text(section.content.strip()))

            elif section.type == OutputType.TOOL_CALL:
                if section.tool_tracker:
                    tracker = section.tool_tracker
                    # Add spacing between sections
                    if renderables:
                        renderables.append(Text())

                    # Format tool call with simpler display
                    tool_text = Text()
                    tool_text.append("● ", style="green")
                    tool_text.append(tracker.tool_name, style="bold cyan")

                    # Add inputs if available (show all for most tools, limited for write tools)
                    if tracker.inputs:
                        inputs_str = self._format_tool_inputs_for_display(
                            tracker.tool_name, tracker.inputs
                        )
                        if inputs_str:
                            tool_text.append("(")
                            tool_text.append(inputs_str, style="dim")
                            tool_text.append(")")

                    renderables.append(tool_text)

            elif section.type == OutputType.TOOL_OUTPUT:
                if section.tool_tracker and section.content:
                    # Generate smart summary based on tool and content
                    summary = self._generate_smart_summary(
                        section.tool_tracker.tool_name, section.content
                    )
                    is_error = self._is_error_output(section.content)

                    # Determine style based on success/failure
                    if is_error:
                        style = "red"
                        arrow_style = "red"
                    else:
                        style = "dim green"
                        arrow_style = "dim green"

                    if summary:
                        # Handle multi-line output with proper alignment
                        summary_lines = summary.split("\n")
                        for i, line in enumerate(summary_lines):
                            if line.strip():  # Skip empty lines
                                output_text = Text()
                                if i == 0:
                                    # First line with arrow
                                    output_text.append("  ╰─ ", style=arrow_style)
                                    output_text.append(line, style=style)
                                else:
                                    # Subsequent lines aligned with first line text
                                    output_text.append(
                                        "     ", style=""
                                    )  # 5 spaces to align with text after "╰─ "
                                    output_text.append(line, style=style)
                                renderables.append(output_text)

                    # Show file diff if this is a file update
                    diff_content = self._extract_diff_content(
                        section.tool_tracker.tool_name, section.content
                    )
                    if diff_content:
                        renderables.extend(diff_content)

        # Return a Group for proper rendering
        if renderables:
            return Group(*renderables)
        else:
            return Text()

    def _format_markdown_content(self, content: str):
        """Format markdown content into Rich renderables for compact display."""
        import re

        renderables = []
        lines = content.split("\n")
        i = 0

        while i < len(lines):
            line = lines[i]

            # Handle code blocks
            if line.strip().startswith("```"):
                # Extract language if specified
                lang_match = re.match(r"^```(\w+)?", line.strip())
                language = lang_match.group(1) if lang_match and lang_match.group(1) else "text"

                # Collect code block content
                code_lines = []
                i += 1
                while i < len(lines) and not lines[i].strip().startswith("```"):
                    code_lines.append(lines[i])
                    i += 1

                # Create syntax highlighted code block
                if code_lines:
                    code_content = "\n".join(code_lines)
                    # Use adaptive theme based on terminal background
                    from ..utils.terminal_theme import detect_terminal_theme

                    theme = detect_terminal_theme()
                    syntax_theme = "ansi_light" if theme == "light" else "ansi_dark"
                    syntax = Syntax(
                        code_content,
                        language,
                        theme=syntax_theme,
                        line_numbers=False,
                        background_color="default",
                    )
                    renderables.append(syntax)

                i += 1
                continue

            # Handle headings
            if line.startswith("#"):
                heading_match = re.match(r"^(#+)\s+(.+)", line)
                if heading_match:
                    level = len(heading_match.group(1))
                    text = heading_match.group(2)

                    if level == 1:
                        renderables.append(Text(text, style="bold yellow"))
                    elif level == 2:
                        renderables.append(Text(text, style="bold cyan"))
                    elif level == 3:
                        renderables.append(Text(text, style="bold magenta"))
                    else:
                        renderables.append(Text(text, style="bold"))

                    i += 1
                    continue

            # Handle regular text with inline formatting
            if line.strip():
                # Apply inline formatting
                formatted_line = line

                # Bold text
                formatted_line = re.sub(r"\*\*([^*]+)\*\*", r"[bold]\1[/bold]", formatted_line)

                # Italic text
                formatted_line = re.sub(r"\*([^*]+)\*", r"[italic]\1[/italic]", formatted_line)

                # Inline code
                formatted_line = re.sub(r"`([^`]+)`", r"[cyan]\1[/cyan]", formatted_line)

                renderables.append(Text.from_markup(formatted_line))
            elif renderables and i < len(lines) - 1:
                # Add empty Text for spacing between paragraphs
                renderables.append(Text())

            i += 1

        return renderables

    def _format_tool_inputs(self, inputs: Dict[str, Any]) -> str:
        """Format tool inputs for display."""
        if not inputs:
            return ""

        # Handle common input patterns
        formatted_parts = []

        for key, value in inputs.items():
            if key in ["file_path", "path", "filename"]:
                # Show just filename for paths
                if isinstance(value, str) and "/" in value:
                    filename = value.split("/")[-1]
                    formatted_parts.append(f"{key}={filename}")
                else:
                    formatted_parts.append(f"{key}={value}")
            elif key in ["pattern", "query", "command"]:
                # Show pattern/query/command values
                if isinstance(value, str) and len(value) <= 30:
                    formatted_parts.append(f"{key}={repr(value)}")
                elif isinstance(value, str):
                    formatted_parts.append(f"{key}={repr(value[:27])}...")
                else:
                    formatted_parts.append(f"{key}={value}")
            elif len(formatted_parts) < 2:  # Limit to first 2 key params
                if isinstance(value, str) and len(value) <= 20:
                    formatted_parts.append(f"{key}={repr(value)}")
                elif isinstance(value, (int, float, bool)):
                    formatted_parts.append(f"{key}={value}")

        return ", ".join(formatted_parts[:2])  # Max 2 params

    def _format_tool_inputs_full(self, inputs: Dict[str, Any]) -> str:
        """Format tool inputs for display with full content."""
        if not inputs:
            return ""

        # Show all inputs with full content
        formatted_parts = []

        for key, value in inputs.items():
            if isinstance(value, str):
                # Show full string content
                formatted_parts.append(f"{key}={repr(value)}")
            elif isinstance(value, (int, float, bool)):
                formatted_parts.append(f"{key}={value}")
            elif isinstance(value, (list, dict)):
                # Show JSON representation
                try:
                    json_str = json.dumps(value, ensure_ascii=False)
                    formatted_parts.append(f"{key}={json_str}")
                except Exception:
                    formatted_parts.append(f"{key}={str(value)}")
            else:
                formatted_parts.append(f"{key}={str(value)}")

        return ", ".join(formatted_parts)

    def _format_tool_output_limited(self, output: str) -> str:
        """Format tool output for display with 500 character limit."""
        if not output:
            return ""

        # Clean and limit output to 500 characters
        clean_output = output.strip()

        if len(clean_output) <= 500:
            return clean_output
        else:
            return clean_output[:500] + "..."

    def _format_tool_output(self, output: str) -> str:
        """Format tool output for display."""
        if not output:
            return ""

        # Clean and truncate output
        clean_output = output.strip()

        # Handle different output types
        if clean_output.startswith("{") or clean_output.startswith("["):
            try:
                # Try to parse as JSON for better formatting
                data = json.loads(clean_output)
                if isinstance(data, dict) and len(data) == 1:
                    key, value = next(iter(data.items()))
                    return f"{key}: {str(value)[:50]}..."
                elif isinstance(data, list) and len(data) > 0:
                    return f"[{len(data)} items]"
                else:
                    return "JSON data"
            except Exception:
                pass

        # Handle file operations
        if "File created" in clean_output or "File written" in clean_output:
            return "File created/updated"
        elif "files found" in clean_output.lower():
            return clean_output[:60] + ("..." if len(clean_output) > 60 else "")
        elif "\n" in clean_output:
            # Multi-line output - show first line
            first_line = clean_output.split("\n")[0].strip()
            return (first_line[:50] + "...") if len(first_line) > 50 else first_line
        else:
            # Single line - truncate if needed
            return (clean_output[:60] + "...") if len(clean_output) > 60 else clean_output

    def finalize_text_sections(self):
        """Finalize any pending text sections."""
        if self.current_text_section and not self.current_text_section.complete:
            self.current_text_section.complete = True
            self.current_text_section = None

    def get_final_text(self) -> str:
        """Get the final assembled text response."""
        text_parts = []

        for section in self.sections:
            if section.type == OutputType.TEXT and section.content.strip():
                text_parts.append(section.content.strip())

        return "\n\n".join(text_parts) if text_parts else ""

    def get_final_display(self) -> str:
        """Get the final display content including tools as plain text."""
        from io import StringIO

        from rich.console import Console

        # Create a temporary console to render to string
        temp_output = StringIO()
        temp_console = Console(file=temp_output, width=120, color_system=None)

        # Get the display content and render it
        content = self.get_display_content()
        temp_console.print(content)

        # Get the rendered text
        result = temp_output.getvalue()
        temp_output.close()

        return result.rstrip()  # Remove trailing whitespace

    def _format_tool_inputs_simple(self, inputs: Dict[str, Any]) -> str:
        """Format tool inputs for simplified display."""
        if not inputs:
            return ""

        # Show only the most important parameter
        key_params = ["file_path", "path", "pattern", "query", "command", "url"]

        for key in key_params:
            if key in inputs:
                value = inputs[key]
                if isinstance(value, str):
                    if key in ["file_path", "path"] and "/" in value:
                        # Show just filename for paths
                        return value.split("/")[-1]
                    elif len(value) <= 50:
                        return value
                    else:
                        return f"{value[:47]}..."
                else:
                    return str(value)

        # Fallback to first parameter
        if inputs:
            key, value = next(iter(inputs.items()))
            if isinstance(value, str) and len(value) <= 50:
                return value
            elif isinstance(value, str):
                return f"{value[:47]}..."
            else:
                return str(value)

        return ""

    def _generate_smart_summary(self, tool_name: str, output: str) -> str:
        """Generate smart summary for tool output."""
        if not output:
            return ""

        clean_output = output.strip()

        # Handle read_file tool
        if tool_name == "read_file":
            lines = clean_output.count("\n") + 1 if clean_output else 0
            return f"Read {lines} lines"

        # Handle glob_search tool
        elif tool_name == "glob_search":
            if "No files found" in clean_output:
                return "No files found"
            else:
                # Count files in output
                files = [
                    line
                    for line in clean_output.split("\n")
                    if line.strip() and not line.startswith("Found")
                ]
                # For small number of files (<=5), show them all
                if len(files) <= 5:
                    return "\n".join(files) if files else "No files found"
                else:
                    return f"Found {len(files)} files"

        # Handle grep_search tool
        elif tool_name == "grep_search":
            if "No files found" in clean_output:
                return "No matches found"
            elif "Found" in clean_output and "files" in clean_output:
                # Extract number from "Found X files"
                import re

                match = re.search(r"Found (\d+) files?", clean_output)
                if match:
                    return f"Found {match.group(1)} files"
                else:
                    return "Search completed"
            else:
                return "Search completed"

        # Handle list_directory tool
        elif tool_name == "list_directory":
            lines = [
                line
                for line in clean_output.split("\n")
                if line.strip() and not line.startswith("-")
            ]
            return f"Listed {len(lines)} items"

        # Handle git_command tool
        elif tool_name == "git_command":
            if not clean_output:
                return "Git command completed"
            elif "error" in clean_output.lower() or "failed" in clean_output.lower():
                first_line = clean_output.split("\n")[0][:60]
                return f"Error: {first_line}"
            else:
                lines = clean_output.split("\n")
                # For short outputs (<=10 lines), show all lines
                if len(lines) <= 10 and len(clean_output) <= 500:
                    return clean_output
                # For longer outputs, show summary
                elif len(lines) == 1:
                    return clean_output[:60] + ("..." if len(clean_output) > 60 else "")
                else:
                    return f"Git output {len(lines)} lines"

        # Handle run_shell tool
        elif tool_name == "run_shell":
            if not clean_output:
                return "Command completed"
            elif "error" in clean_output.lower() or "failed" in clean_output.lower():
                first_line = clean_output.split("\n")[0][:60]
                return f"Error: {first_line}"
            else:
                lines = clean_output.split("\n")
                # For short outputs (<=5 lines), show all lines
                if len(lines) <= 5 and len(clean_output) <= 200:
                    return clean_output
                # For longer outputs, show summary
                elif len(lines) == 1:
                    return clean_output[:60] + ("..." if len(clean_output) > 60 else "")
                else:
                    return f"Output {len(lines)} lines"

        # Handle file operation tools
        elif tool_name in ["write_file", "append_file"]:
            if "updated" in clean_output.lower() or "written" in clean_output.lower():
                return "File updated"
            elif "created" in clean_output.lower():
                return "File created"
            else:
                return clean_output[:60] + ("..." if len(clean_output) > 60 else "")

        # Handle todo_write
        elif tool_name == "todo_write":
            if "Updated" in clean_output:
                return clean_output
            else:
                return "Todos updated"

        # Default case
        else:
            if len(clean_output) <= 80:
                return clean_output
            else:
                # Show first line or first 60 chars
                first_line = clean_output.split("\n")[0]
                if len(first_line) <= 80:
                    return first_line
                else:
                    return f"{first_line[:77]}..."

    def _is_error_output(self, output: str) -> bool:
        """Check if the output indicates an error."""
        if not output:
            return False

        error_indicators = [
            "error:",
            "Error:",
            "ERROR:",
            "failed:",
            "Failed:",
            "FAILED:",
            "exception:",
            "Exception:",
            "EXCEPTION:",
            "traceback",
            "Traceback",
            "TRACEBACK",
            "not found",
            "Not found",
            "NOT FOUND",
            "permission denied",
            "Permission denied",
            "no such file",
            "No such file",
        ]

        return any(indicator in output for indicator in error_indicators)

    def _extract_diff_content(self, tool_name: str, output: str) -> List:
        """Extract and format diff content for file updates."""
        renderables = []

        # Only show diffs for file editing tools
        if tool_name not in ["Edit", "MultiEdit", "Write"]:
            return renderables

        # Look for diff-like content in the output
        lines = output.split("\n")
        diff_lines = []
        in_diff = False

        for line in lines:
            # Simple diff detection
            if line.strip().startswith(("+", "-", "@@")) and not in_diff:
                in_diff = True
                diff_lines.append(line)
            elif in_diff and line.strip().startswith(("+", "-", " ", "@@")):
                diff_lines.append(line)
            elif in_diff and not line.strip():
                diff_lines.append(line)
            elif in_diff:
                # End of diff section
                break

        # Format diff if found
        if diff_lines:
            renderables.append(Text())  # Add spacing
            for line in diff_lines[:10]:  # Limit to 10 lines
                diff_text = Text()
                if line.startswith("+"):
                    diff_text.append("    ", style="")
                    diff_text.append(line, style="green")
                elif line.startswith("-"):
                    diff_text.append("    ", style="")
                    diff_text.append(line, style="red")
                elif line.startswith("@@"):
                    diff_text.append("    ", style="")
                    diff_text.append(line, style="cyan")
                else:
                    diff_text.append("    ", style="")
                    diff_text.append(line, style="dim")
                renderables.append(diff_text)

            if len(diff_lines) > 10:
                renderables.append(Text("    ...", style="dim"))

        return renderables

    def _format_tool_inputs_for_display(self, tool_name: str, inputs: Dict[str, Any]) -> str:
        """Format tool inputs for display based on tool type."""
        if not inputs:
            return ""

        # Special handling for Write tools - only show essential params
        if tool_name in ["Write", "write_file"]:
            formatted_parts = []
            for key, value in inputs.items():
                if key == "file_path":
                    # Show just filename for paths
                    if isinstance(value, str) and "/" in value:
                        filename = value.split("/")[-1]
                        formatted_parts.append(f"file_path={filename}")
                    else:
                        formatted_parts.append(f"file_path={value}")
                elif key in ["mode", "encoding"] and len(formatted_parts) < 2:
                    # Show some additional params but limit content length
                    formatted_parts.append(f"{key}={value}")
            return ", ".join(formatted_parts[:2])  # Max 2 params for write

        # For all other tools - show all parameters
        formatted_parts = []
        for key, value in inputs.items():
            if isinstance(value, str):
                if key in ["file_path", "path"] and "/" in value:
                    # Show just filename for paths
                    filename = value.split("/")[-1]
                    formatted_parts.append(f"{key}={filename}")
                elif len(value) <= 100:
                    # Show strings up to 100 chars
                    formatted_parts.append(f"{key}={repr(value)}")
                else:
                    # Truncate long strings
                    formatted_parts.append(f"{key}={repr(value[:97])}...")
            elif isinstance(value, (int, float, bool)):
                formatted_parts.append(f"{key}={value}")
            elif isinstance(value, (list, dict)):
                # Show JSON representation for structured data
                try:
                    json_str = json.dumps(value, ensure_ascii=False)
                    if len(json_str) <= 100:
                        formatted_parts.append(f"{key}={json_str}")
                    else:
                        formatted_parts.append(f"{key}={json_str[:97]}...")
                except Exception:
                    formatted_parts.append(f"{key}={str(value)}")
            else:
                formatted_parts.append(f"{key}={str(value)}")

        return ", ".join(formatted_parts)
