# repl_ui.py
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.markdown import Markdown
from rich.live import Live
from typing import List
import json

import asyncio
import sys
import time
import signal
from datetime import datetime

# Simple readline support for history
try:
    import readline
    import atexit
    READLINE_AVAILABLE = True
except ImportError:
    READLINE_AVAILABLE = False

from pantheon.agent import Agent
from pantheon.agent import RemoteAgent
from ..utils.display import print_agent_message, print_agent, print_banner, print_agent_message_modern_style



class ReplUI:
    """Presentation layer for REPL: printing, input, formatting."""
    def __init__(self):
        self.console = Console()
        self.input_panel = Panel(Text("Type your message here...", style="dim"),
                                 title="Input", border_style="bright_blue")
        self._tools_executing = False
        self._processing_live: Live | None = None
        self._current_tool_name = None
        
        # Conversation history for /save command
        self.conversation_history = []

    def _should_display_bash_in_box(self, command: str) -> bool:
        """Determine if a bash command should be displayed in a code box instead of inline"""
        command = command.strip()
        
        # List of bioinformatics tools that should always use code box
        bio_tools = [
            'fastqc', 'multiqc', 'trim_galore', 'cutadapt', 
            'bowtie2', 'bwa', 'minimap2', 'hisat2',
            'samtools', 'bcftools', 'picard', 'sambamba',
            'macs2', 'genrich', 'hmmratac',
            'bamCoverage', 'computeMatrix', 'plotHeatmap', 'plotProfile',
            'bedtools', 'findMotifsGenome.pl', 'homer',
            'featureCounts', 'htseq-count', 'star', 'rsem', 'kallisto'
        ]
        
        # Check if command starts with any bio tool
        command_parts = command.split()
        if command_parts:
            first_command = command_parts[0].split('/')[-1]  # Get just the command name (no path)
            if any(tool in first_command.lower() for tool in bio_tools):
                return True
        
        # Check command length (long commands should use code box)
        if len(command) > 80:
            return True
        
        # Check if command has many arguments (likely complex)
        if len(command_parts) > 6:
            return True
        
        # Check for multi-line commands
        if '\n' in command or '&&' in command or '||' in command or ';' in command:
            return True
        
        # Check for file paths (likely data processing)
        if any(ext in command for ext in ['.fastq', '.fq', '.bam', '.sam', '.bed', '.gtf', '.gff', '.fa', '.fasta']):
            return True
        
        return False

    def _get_bash_command_title(self, command: str) -> str:
        """Get an appropriate title for a bash command based on the tool being used"""
        command = command.strip().lower()
        command_parts = command.split()
        
        if not command_parts:
            return "Run bash command"
        
        # Extract the actual command name (remove path if present)
        first_command = command_parts[0].split('/')[-1]
        
        # Define titles for common bioinformatics tools
        tool_titles = {
            'fastqc': 'Quality Control with FastQC',
            'multiqc': 'Generate MultiQC Report',
            'trim_galore': 'Adapter Trimming with Trim Galore',
            'cutadapt': 'Adapter Trimming with Cutadapt',
            'bowtie2': 'Sequence Alignment with Bowtie2',
            'bwa': 'Sequence Alignment with BWA',
            'minimap2': 'Long-read Alignment with Minimap2',
            'hisat2': 'RNA-seq Alignment with HISAT2',
            'samtools': 'SAM/BAM Processing with Samtools',
            'bcftools': 'Variant Processing with BCFtools',
            'picard': 'BAM Processing with Picard',
            'sambamba': 'BAM Processing with Sambamba',
            'macs2': 'Peak Calling with MACS2',
            'genrich': 'Peak Calling with Genrich',
            'hmmratac': 'Peak Calling with HMMRATAC',
            'bamcoverage': 'Generate Coverage Tracks',
            'computematrix': 'Compute Matrix for Visualization',
            'plotheatmap': 'Generate Heatmap',
            'plotprofile': 'Generate Profile Plot',
            'bedtools': 'Genomic Interval Operations',
            'findmotifsgenome.pl': 'Motif Discovery with HOMER',
            'homer': 'Motif Analysis with HOMER',
            'featurecounts': 'Count Features with featureCounts',
            'htseq-count': 'Count Features with HTSeq',
            'star': 'RNA-seq Alignment with STAR',
            'rsem': 'Expression Quantification with RSEM',
            'kallisto': 'Expression Quantification with Kallisto'
        }
        
        # Check for exact matches first
        for tool, title in tool_titles.items():
            if first_command == tool:
                return title
        
        # Check for partial matches (in case of versioned tools like fastqc-0.11.9)
        for tool, title in tool_titles.items():
            if tool in first_command:
                return title
        
        # Check for pipeline-style commands
        if any(connector in command for connector in ['&&', '||', ';', '|']):
            return "Run multi-step pipeline"
        
        # Check for common patterns
        if 'wget' in first_command or 'curl' in first_command:
            return "Download files"
        elif 'gunzip' in first_command or 'tar' in first_command or 'unzip' in first_command:
            return "Extract/decompress files"
        elif first_command in ['mkdir', 'cp', 'mv', 'rm']:
            return "File system operations"
        elif first_command in ['grep', 'awk', 'sed', 'sort', 'uniq']:
            return "Text processing"
        
        return "Run bash command"

    def _wrap_bash_command(self, command: str, max_width: int = 71) -> List[str]:
        """Wrap a bash command for display, breaking at appropriate points"""
        # If command already has newlines, split by those first
        if '\n' in command:
            lines = command.split('\n')
        else:
            lines = [command]
        
        wrapped_lines = []
        for line in lines:
            # If line is short enough, keep it as is
            if len(line) <= max_width:
                wrapped_lines.append(line)
                continue
            
            # Try to break at logical points
            # Priority: space before flags (-), pipes (|), && or ||, semicolons, spaces
            current_line = ""
            remaining = line
            
            while remaining:
                if len(remaining) <= max_width:
                    wrapped_lines.append(remaining)
                    break
                
                # Find best break point
                break_point = max_width
                
                # Look for good break points in priority order
                # 1. Before a flag (space followed by -)
                for i in range(max_width - 1, max(0, max_width - 20), -1):
                    if i < len(remaining) - 1 and remaining[i] == ' ' and remaining[i + 1] == '-':
                        break_point = i + 1
                        break
                
                # 2. Before pipes, redirects, or logical operators
                if break_point == max_width:
                    for pattern in [' | ', ' > ', ' >> ', ' && ', ' || ', ' ; ']:
                        idx = remaining[:max_width].rfind(pattern)
                        if idx > 0:
                            break_point = idx + 1
                            break
                
                # 3. At any space
                if break_point == max_width:
                    space_idx = remaining[:max_width].rfind(' ')
                    if space_idx > 0:
                        break_point = space_idx + 1
                
                # 4. If no good break point, break at max_width
                wrapped_lines.append(remaining[:break_point].rstrip())
                remaining = remaining[break_point:].lstrip()
                
                # Add continuation indicator for wrapped lines (except last)
                if remaining and not wrapped_lines[-1].endswith('\\'):
                    wrapped_lines[-1] = wrapped_lines[-1]
        
        return wrapped_lines

    async def print_greeting(self):
        self.console.print("[purple]Aristotle © 2025[/purple]")
        await print_banner(self.console)
        self.console.print()
        self.console.print(
            "[bold italic]We're not just building another CLI tool.[/bold italic]\n" +
            "[bold italic purple]We're redefining how scientists interact with data in the AI era.\n[/bold italic purple]"
            "[bold italic dim]Pantheon-CLI is a research project, use with caution.[/bold italic dim]"
        )
        self.console.print()
        
        # Agent info in a compact format
        self.console.print("[dim][bold blue]-- MODEL ------------------------------------------------------------[/bold blue][/dim]")
        self.console.print()
        agent_info = f"  - [bright_blue]{self.agent.name}[/bright_blue]"
        if hasattr(self.agent, 'models') and self.agent.models:
            model = self.agent.models[0] if isinstance(self.agent.models, list) else self.agent.models
            agent_info = f"[dim]  • [bold]{model}[/bold][/dim]"
        self.console.print(agent_info)

        self.console.print()
        self.console.print("[dim][bold blue]-- HELP -------------------------------------------------------------[/bold blue][/dim]")
        self.console.print()
        self.console.print("[dim]  • [bold purple]/exit   [/bold purple] to quit[/dim]")
        self.console.print("[dim]  • [bold purple]/help   [/bold purple] for commands[/dim]")

        self.console.print("[dim]  • [bold purple]/model  [/bold purple] for available models[/dim]")
        self.console.print("[dim]  • [bold purple]/api-key[/bold purple] for API keys[/dim]")
        if READLINE_AVAILABLE:
            self.console.print()
            self.console.print("[dim][bold blue]-- CONTROL ----------------------------------------------------------[/bold blue][/dim]")
            self.console.print()
            self.console.print("[dim]Use ↑/↓ arrows for command history[/dim]")
        self.console.print()
    
    # --- Input ---
    def ask_user_input(self) -> str:
        """Get user input with multi-line support and readline history."""
        try:
            self.console.print("[dim]Enter your message (press Enter twice to finish)[/dim]")
            lines = []
            while True:
                # First input uses "> " prompt, subsequent lines use "... "
                prompt_text = "... " if lines else ">   "

                if READLINE_AVAILABLE:
                    line = input(prompt_text)
                else:
                    self.console.print(f"[bright_blue]{prompt_text}[/bright_blue]", end=" ")
                    line = input()

                # 空行结束
                if line.strip() == "":
                    break

                lines.append(line)

            # 返回多行合并的字符串
            return "\n".join(lines).strip()

        except KeyboardInterrupt:
            self.console.print("\n[dim]Ctrl+C pressed - operation cancelled[/dim]")
            return ""
        except EOFError:
            raise

    def _print_help(self):
        """Print available commands"""
        #self.console.print("\n[bold]Commands:[/bold]")
        self.console.print("[dim][bold blue]-- BASIC ------------------------------------------------------------[/bold blue][/dim]")
        self.console.print()
        self.console.print("[dim][bold purple]/help    [/bold purple][/dim] - Show this help")
        self.console.print("[dim][bold purple]/status  [/bold purple][/dim] - Session info")
        self.console.print("[dim][bold purple]/history [/bold purple][/dim] - Show command history")
        self.console.print("[dim][bold purple]/tokens  [/bold purple][/dim] - Token usage analysis")  
        self.console.print("[dim][bold purple]/save    [/bold purple][/dim] - Save conversation with terminal output to markdown")
        self.console.print("[dim][bold purple]/clear   [/bold purple][/dim] - Clear screen")
        self.console.print("[dim][bold purple]/restart [/bold purple][/dim] - Restart Python interpreter (clear all state)")
        self.console.print("[dim][bold purple]/bio     [/bold purple][/dim] - Bioinformatics analysis helper 🧬")
        self.console.print("[dim][bold purple]!<cmd>   [/bold purple][/dim] - Execute bash command directly (no LLM)")
        self.console.print("[dim][bold purple]%<code>  [/bold purple][/dim] - Execute Python code directly (no LLM)")
        self.console.print("[dim][bold purple]><code>  [/bold purple][/dim] - Execute R code directly (no LLM)")
        self.console.print("[dim][bold purple]/exit    [/bold purple][/dim] - Exit cleanly")
        self.console.print("[dim]Ctrl+C   [/dim] - Cancel current operation")
        self.console.print("[dim]Ctrl+C x2[/dim] - Force exit (within 2 seconds)")
        self.console.print()
        
        # Check if model/API key management is available
        if hasattr(self.agent, '_model_manager') or hasattr(self.agent, '_api_key_manager'):
            #self.console.print("\n[bold]Model & API Management:[/bold]")
            self.console.print("[dim][bold blue]-- MODEL & API ------------------------------------------------------[/bold blue][/dim]")
            self.console.print()
            if hasattr(self.agent, '_model_manager'):
                self.console.print("[dim][bold purple]/model[/bold purple] list              [/dim] - List available models")
                self.console.print("[dim][bold purple]/model[/bold purple] current           [/dim] - Show current model")  
                self.console.print("[dim][bold purple]/model[/bold purple] <id>              [/dim] - Switch to model")
            if hasattr(self.agent, '_api_key_manager'):
                self.console.print("[dim][bold purple]/api-key[/bold purple] list            [/dim] - Show API key status")
                self.console.print("[dim][bold purple]/api-key[/bold purple] <provider> <key>[/dim] - Set API key")
            self.console.print()
        
        if READLINE_AVAILABLE:
            #self.console.print("\n[bold]Navigation:[/bold]")
            self.console.print("[dim][bold blue]-- NAVIGATION -------------------------------------------------------[/bold blue][/dim]")
            self.console.print()
            self.console.print("[dim][bold purple]↑/↓[/bold purple] - Browse command history")
        self.console.print()
        
    
    def _print_history(self):
        """Print recent command history"""
        self.console.print()
        self.console.print("[dim][bold blue]-- HISTORY ---------------------------------------------------------------[/bold blue][/dim]")
        self.console.print()
        if not self.command_history:
            self.console.print("[dim]No command history yet[/dim]\n")
            return
            
        self.console.print(f"[bold purple]Command History[/bold purple] [dim]({len(self.command_history)} commands)[/dim]")
        
        # Show last 10 commands
        recent = self.command_history[-10:]
        for i, cmd in enumerate(recent, 1):
            if len(recent) == 10 and i == 1 and len(self.command_history) > 10:
                self.console.print("[dim]...[/dim]")
            self.console.print(f"[dim]{len(self.command_history) - len(recent) + i:2d}.[/dim] {cmd}")
        self.console.print()
    
    def _print_token_analysis(self):
        """Print detailed token usage analysis"""
        total_tokens = self.total_input_tokens + self.total_output_tokens
        #self.console.print(f"\n[bold]Token Analysis[/bold]")
        self.console.print()
        self.console.print("[dim][bold blue]-- TOKENS -----------------------------------------------------------[/bold blue][/dim]")
        self.console.print()

        if total_tokens == 0:
            self.console.print("\n[dim]No token usage data yet[/dim]\n")
            return
        
        
        
        # Basic stats
        self.console.print(f"[dim]  • Total:[/dim] {self._format_token_count(total_tokens)} tokens")
        self.console.print(f"[dim]  • Input: [/dim] {self._format_token_count(self.total_input_tokens)} ({self.total_input_tokens/total_tokens*100:.1f}%)")
        self.console.print(f"[dim]  • Output: [/dim] {self._format_token_count(self.total_output_tokens)} ({self.total_output_tokens/total_tokens*100:.1f}%)")
        self.console.print()
        
        # Efficiency metrics
        if self.message_count > 0:
            avg_total = total_tokens / self.message_count
            avg_input = self.total_input_tokens / self.message_count
            avg_output = self.total_output_tokens / self.message_count
            
            #self.console.print(f"\n[bold]Per Message Average:[/bold]")
            self.console.print("[dim][bold blue]-- PER MSG/AVG ------------------------------------------------------[/bold blue][/dim]")
            self.console.print()
            self.console.print(f"[dim]  • Total:[/dim] {self._format_token_count(int(avg_total))}")
            self.console.print(f"[dim]  • Input:[/dim] {self._format_token_count(int(avg_input))}")
            self.console.print(f"[dim]  • Output:[/dim] {self._format_token_count(int(avg_output))}")
            self.console.print()
        # Usage recommendations
        #self.console.print(f"\n[bold]Tips:[/bold]")
        self.console.print("[dim][bold blue]-- TIPS --------------------------------------------------------------[/bold blue][/dim]")
        self.console.print()
        if avg_input > 1000:
            self.console.print("[dim]  • Consider shorter prompts to reduce input tokens[/dim]")
        if self.total_output_tokens / max(1, self.total_input_tokens) > 3:
            self.console.print("[dim]  • High output ratio - responses are verbose[/dim]")
        if self.message_count > 5 and avg_total < 100:
            self.console.print("[dim]  • Efficient usage - good token management[/dim]")
        elif avg_total > 2000:
            self.console.print("[dim]  • High token usage - consider optimizing prompts[/dim]")
        
        self.console.print()
        
    def _print_status(self):
        """Print current session status"""
        session_duration = datetime.now() - self.session_start
        duration_mins = int(session_duration.total_seconds() / 60)
        
        #self.console.print(f"\n[bold]Session Status:[/bold]")
        self.console.print()
        self.console.print("[dim][bold blue]-- STATUS -----------------------------------------------------------[/bold blue][/dim]")
        self.console.print()
        self.console.print(f"[dim]• Agent:    [/dim] {self.agent.name}")
        if hasattr(self.agent, 'models') and self.agent.models:
            model = self.agent.models[0] if isinstance(self.agent.models, list) else self.agent.models
            self.console.print(f"[dim]• Model:    [/dim] {model}")
        self.console.print(f"[dim]• Messages: [/dim] {self.message_count}")
        self.console.print(f"[dim]• Duration: [/dim] {duration_mins}m")
        self.console.print(f"[dim]• History:  [/dim] {len(self.command_history)} commands")
        self.console.print()
        
        # Token usage statistics
        total_tokens = self.total_input_tokens + self.total_output_tokens
        if total_tokens > 0:
            self.console.print("[dim][bold blue]-- TOKENS -----------------------------------------------------------[/bold blue][/dim]")
            self.console.print()
            self.console.print(f"[dim]  • Total:  [/dim] {self._format_token_count(total_tokens)}")
            self.console.print(f"[dim]  • Input:  [/dim] {self._format_token_count(self.total_input_tokens)}")
            self.console.print(f"[dim]  • Output: [/dim] {self._format_token_count(self.total_output_tokens)}")
            
            # Show efficiency metrics
            if self.message_count > 0:
                avg_tokens_per_msg = total_tokens / self.message_count
                self.console.print(f"[dim]  • Avg/msg:[/dim] {self._format_token_count(int(avg_tokens_per_msg))}")
            self.console.print()
        
        if READLINE_AVAILABLE:
            self.console.print(f"[dim]Input:[/dim] readline (with history)")
        else:
            self.console.print(f"[dim]Input:[/dim] basic")
        self.console.print()

    def _print_session_summary(self):
        """Print a brief session summary before exit"""
        session_duration = datetime.now() - self.session_start
        duration_mins = int(session_duration.total_seconds() / 60)
        
        if self.message_count > 0:
            summary = f"Session: {self.message_count} messages in {duration_mins}m"
            total_tokens = self.total_input_tokens + self.total_output_tokens
            if total_tokens > 0:
                summary += f" • {self._format_token_count(total_tokens)} tokens"
            self.console.print(f"\n[dim]{summary}[/dim]")
        self.console.print("[dim]Goodbye![/dim]")

    def add_to_conversation(self, message_type: str, content: str, metadata: dict = None):
        """Add a message to the conversation history"""
        entry = {
            "type": message_type,  # "user", "assistant", "tool_call", "tool_result", "terminal_output"
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        self.conversation_history.append(entry)
    
    def capture_terminal_output(self, content: str):
        """Capture raw terminal output for preservation in saved conversations"""
        self.add_to_conversation("terminal_output", content, {"source": "terminal"})

    def _format_tool_output(self, output):
        """Format tool output for better readability in markdown"""
        import json
        
        if output is None:
            return "*No output*"
        
        # Handle dict outputs
        if isinstance(output, dict):
            # Special handling for common tool outputs
            if "result" in output and isinstance(output.get("result"), dict):
                # Python/R code execution results
                result = output["result"]
                stdout = output.get("stdout", "").strip()
                stderr = output.get("stderr", "").strip()
                
                formatted_lines = []
                
                # Format the main result
                if result:
                    try:
                        # Pretty print the result
                        result_str = json.dumps(result, indent=2, ensure_ascii=False)
                        formatted_lines.append("**Result:**")
                        formatted_lines.append("```json")
                        formatted_lines.append(result_str)
                        formatted_lines.append("```")
                    except:
                        formatted_lines.append("**Result:**")
                        formatted_lines.append("```")
                        formatted_lines.append(str(result))
                        formatted_lines.append("```")
                
                # Add stdout if present
                if stdout:
                    formatted_lines.append("")
                    formatted_lines.append("**Standard Output:**")
                    formatted_lines.append("```")
                    formatted_lines.append(stdout)
                    formatted_lines.append("```")
                
                # Add stderr if present
                if stderr:
                    formatted_lines.append("")
                    formatted_lines.append("**Error Output:**")
                    formatted_lines.append("```")
                    formatted_lines.append(stderr)
                    formatted_lines.append("```")
                
                return "\n".join(formatted_lines) if formatted_lines else "```\n{}\n```".format(str(output))
            
            # Special handling for todo outputs
            elif "success" in output and "summary" in output:
                formatted_lines = []
                if output.get("success"):
                    summary = output.get("summary", {})
                    total = output.get("total_todos", 0)
                    
                    formatted_lines.append(f"✅ **Todo Status:** {total} total tasks")
                    if summary:
                        formatted_lines.append(f"- Pending: {summary.get('pending', 0)}")
                        formatted_lines.append(f"- In Progress: {summary.get('in_progress', 0)}")
                        formatted_lines.append(f"- Completed: {summary.get('completed', 0)}")
                    
                    # Add todos list if present
                    if "todos" in output and output["todos"]:
                        formatted_lines.append("")
                        formatted_lines.append("**Tasks:**")
                        for todo in output["todos"]:
                            status_icon = "✅" if todo.get("status") == "completed" else "🔄" if todo.get("status") == "in_progress" else "⏳"
                            formatted_lines.append(f"- {status_icon} {todo.get('content', 'Unknown task')}")
                    
                    return "\n".join(formatted_lines)
            
            # Generic dict formatting
            try:
                formatted = json.dumps(output, indent=2, ensure_ascii=False)
                return f"```json\n{formatted}\n```"
            except:
                return f"```\n{str(output)}\n```"
        
        # Handle list outputs
        elif isinstance(output, list):
            try:
                formatted = json.dumps(output, indent=2, ensure_ascii=False)
                return f"```json\n{formatted}\n```"
            except:
                return f"```\n{str(output)}\n```"
        
        # Handle string outputs
        elif isinstance(output, str):
            if "\n" in output or len(output) > 80:
                return f"```\n{output}\n```"
            else:
                return output
        
        # Default formatting
        else:
            return f"```\n{str(output)}\n```"

    def export_conversation_to_markdown(self, filename: str = None) -> str:
        """Export conversation history to a markdown file with full terminal display"""
        if not filename:
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"pantheon_conversation_{timestamp}.md"
        
        # Build markdown content
        lines = []
        lines.append("# 🧬 Pantheon CLI Conversation")
        lines.append("")
        lines.append(f"**Exported on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        lines.append("---")
        lines.append("")
        
        current_user_message = None
        
        for entry in self.conversation_history:
            if entry["type"] == "user":
                lines.append(f"## 💬 User Input")
                lines.append("")
                lines.append(f"```")
                lines.append(entry["content"])
                lines.append("```")
                lines.append("")
                current_user_message = entry["content"]
                
            elif entry["type"] == "assistant":
                lines.append(f"## 🤖 Assistant Response")
                lines.append("")
                lines.append(entry["content"])
                lines.append("")
                
            elif entry["type"] == "tool_call":
                tool_name = entry["metadata"].get("tool_name", "unknown")
                lines.append(f"### 🔧 Tool Call: `{tool_name}`")
                lines.append("")
                
                # Show terminal display if available
                if "terminal_display" in entry["metadata"]:
                    lines.append("**Terminal Display:**")
                    lines.append("```")
                    # Split the terminal display to preserve formatting
                    for line in entry["metadata"]["terminal_display"].split('\n'):
                        lines.append(line)
                    lines.append("```")
                elif "code" in entry["metadata"]:
                    # For code execution tools
                    lang = "python" if "python" in tool_name.lower() else "r" if "r" in tool_name.lower() else "julia" if "julia" in tool_name.lower() else "bash"
                    lines.append(f"```{lang}")
                    lines.append(entry["metadata"]["code"])
                    lines.append("```")
                else:
                    lines.append(f"```")
                    lines.append(entry["content"])
                    lines.append("```")
                lines.append("")
                
            elif entry["type"] == "tool_result":
                lines.append("#### 📤 Output:")
                lines.append("")
                
                # Check if we have the full result stored
                full_result = entry.get("metadata", {}).get("full_result")
                tool_name = entry.get("metadata", {}).get("tool_name", "")
                
                # Show actual terminal output if captured
                actual_output = entry.get("metadata", {}).get("actual_terminal_output")
                if actual_output:
                    lines.append("**Terminal Output:**")
                    lines.append("```")
                    # Split by newlines to preserve formatting
                    for line in actual_output.split('\n'):
                        lines.append(line)
                    lines.append("```")
                    lines.append("")
                
                # Special handling for code execution tools (only if no actual terminal output captured)
                elif tool_name in ['run_python_code', 'run_julia_code', 'run_r_code'] and isinstance(full_result, dict):
                    # Extract stdout, stderr, and result from the execution
                    if 'stdout' in full_result and full_result['stdout']:
                        lines.append("**stdout:**")
                        lines.append("```")
                        # Properly handle the stdout content
                        stdout_content = full_result['stdout']
                        if isinstance(stdout_content, str):
                            # Split by newlines to preserve formatting
                            for line in stdout_content.split('\n'):
                                lines.append(line)
                        else:
                            lines.append(str(stdout_content))
                        lines.append("```")
                        lines.append("")
                    
                    if 'stderr' in full_result and full_result['stderr']:
                        lines.append("**stderr:**")
                        lines.append("```")
                        stderr_content = full_result['stderr']
                        if isinstance(stderr_content, str):
                            for line in stderr_content.split('\n'):
                                lines.append(line)
                        else:
                            lines.append(str(stderr_content))
                        lines.append("```")
                        lines.append("")
                    
                    if 'result' in full_result and full_result['result'] is not None:
                        lines.append("**result:**")
                        lines.append("```")
                        lines.append(str(full_result['result']))
                        lines.append("```")
                        lines.append("")
                
                # Special handling for bash/shell commands (only if no actual terminal output captured)
                elif tool_name in ['run_command', 'run_command_in_shell', 'bash'] and isinstance(full_result, dict):
                    if 'output' in full_result:
                        lines.append("```bash")
                        output = full_result['output']
                        if isinstance(output, str):
                            for line in output.split('\n'):
                                lines.append(line)
                        else:
                            lines.append(str(output))
                        lines.append("```")
                    elif 'stdout' in full_result:
                        lines.append("```bash")
                        stdout = full_result['stdout']
                        if isinstance(stdout, str):
                            for line in stdout.split('\n'):
                                lines.append(line)
                        else:
                            lines.append(str(stdout))
                        lines.append("```")
                    else:
                        lines.append("```")
                        lines.append(str(full_result))
                        lines.append("```")
                
                # Default handling for other tools or when full_result is not available
                else:
                    output_content = entry["content"]
                    
                    # Try to parse and format JSON/dict output
                    if isinstance(output_content, str):
                        # Check if it contains newlines that need preserving
                        if '\n' in output_content:
                            lines.append("```")
                            # Split and add each line separately to preserve formatting
                            for line in output_content.split('\n'):
                                lines.append(line)
                            lines.append("```")
                        elif output_content.startswith("{") and output_content.endswith("}"):
                            try:
                                import json
                                import ast
                                # Try to parse as Python dict literal first
                                parsed = ast.literal_eval(output_content)
                                formatted = self._format_tool_output(parsed)
                                lines.extend(formatted.split("\n"))
                            except:
                                # Fallback to raw output in code block
                                lines.append("```")
                                lines.append(output_content)
                                lines.append("```")
                        else:
                            # For single-line output
                            if len(output_content) > 80:
                                lines.append("```")
                                lines.append(output_content)
                                lines.append("```")
                            else:
                                lines.append(output_content)
                    else:
                        # If it's already a dict/list, format it nicely
                        formatted = self._format_tool_output(output_content)
                        lines.extend(formatted.split("\n"))
                
                lines.append("")
            
            elif entry["type"] == "terminal_output":
                # Special handling for captured terminal output
                lines.append("#### 🖥️ Terminal Display:")
                lines.append("")
                lines.append("```")
                lines.append(entry["content"])
                lines.append("```")
                lines.append("")
        
        # Add footer
        lines.append("---")
        lines.append("")
        lines.append("*End of conversation*")
        lines.append("")
        lines.append(f"📊 **Statistics:**")
        lines.append(f"- Total interactions: {len([e for e in self.conversation_history if e['type'] == 'user'])}")
        lines.append(f"- Tool calls: {len([e for e in self.conversation_history if e['type'] == 'tool_call'])}")
        lines.append("")
        
        markdown_content = "\n".join(lines)
        
        # Write to file
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            return filename
        except Exception as e:
            raise Exception(f"Failed to save conversation: {str(e)}")

    def print_tool_call(self, tool_name: str, args: dict = None):
        """Print tool call in Claude Code style with fancy boxes"""
        # Mark that tools are executing
        self._tools_executing = True
        # Set current tool name for progress display
        self._current_tool_name = tool_name
        
        
        # Record tool call in conversation history
        metadata = {"tool_name": tool_name}
        if args:
            metadata.update(args)
        
        # Generate terminal display content for saving
        terminal_display_lines = []
        if tool_name in ["run_code", "run_code_in_interpreter", "run_python_code",
                          "run_r_code", "run_julia_code"] and args and 'code' in args:
            # Capture the code box display
            if tool_name in ["run_python_code", "run_code", "run_code_in_interpreter"]:
                terminal_display_lines.append("⏺ Python")
                header_title = "Run Python code"
            elif tool_name == "run_r_code":
                terminal_display_lines.append("⏺ R")
                header_title = "Run R code"
            elif tool_name == "run_julia_code":
                terminal_display_lines.append("⏺ Julia")
                header_title = "Run Julia code"
            
            terminal_display_lines.append("╭" + "─" * 77 + "╮")
            terminal_display_lines.append(f"│ {header_title}" + " " * (77 - len(header_title) - 4) + "   │")
            terminal_display_lines.append("│ ╭" + "─" * 73 + "╮ │")
            
            code = args['code']
            lines = code.split('\n')
            for line in lines[:20]:  # Limit to first 20 lines for display
                display_line = line[:71] if len(line) <= 71 else line[:68] + "..."
                terminal_display_lines.append(f"│ │ {display_line.ljust(71)} │ │")
            
            terminal_display_lines.append("│ ╰" + "─" * 73 + "╯ │")
            terminal_display_lines.append("╰" + "─" * 77 + "╯")
            
            metadata["terminal_display"] = "\n".join(terminal_display_lines)
        
        elif tool_name in ["run_command", "run_command_in_shell"] and args and 'command' in args:
            # Capture bash command display
            command = args['command']
            if self._should_display_bash_in_box(command):
                terminal_display_lines.append("⏺ Bash")
                header_title = self._get_bash_command_title(command)
                wrapped_lines = self._wrap_bash_command(command, max_width=71)
                
                terminal_display_lines.append("╭" + "─" * 77 + "╮")
                terminal_display_lines.append(f"│ {header_title}" + " " * (77 - len(header_title) - 4) + "   │")
                terminal_display_lines.append("│ ╭" + "─" * 73 + "╮ │")
                
                for line in wrapped_lines[:20]:  # Limit display
                    terminal_display_lines.append(f"│ │ {line.ljust(71)} │ │")
                
                terminal_display_lines.append("│ ╰" + "─" * 73 + "╯ │")
                terminal_display_lines.append("╰" + "─" * 77 + "╯")
                
                metadata["terminal_display"] = "\n".join(terminal_display_lines)
            else:
                metadata["terminal_display"] = f"⏺ Bash({command})"
        
        self.add_to_conversation("tool_call", f"{tool_name}({args or {}})", metadata)
        
        self.console.print()  # Add some space

        # Claude Code style tool call display
        if tool_name in ["run_code", "run_code_in_interpreter", "run_python_code",
                          "run_r_code", "run_julia_code"] and args and 'code' in args:
            # Special handling for code execution
            if tool_name in ["run_python_code", "run_code", "run_code_in_interpreter"]:
                self.console.print("⏺ [bold]Python[/bold]")
                header_title = "Run Python code"
            elif tool_name == "run_r_code":
                self.console.print("⏺ [bold]R[/bold]")
                header_title = "Run R code"
            elif tool_name == "run_julia_code":
                self.console.print("⏺ [bold]Julia[/bold]")
                header_title = "Run Julia code"
            
            # Create a fancy code block
            code = args['code']
            lines = code.split('\n')
            
            # Create the box
            self.console.print("╭" + "─" * 77 + "╮")
            title_padding = " " * (77 - len(header_title) - 4)
            self.console.print(f"│ [bold]{header_title}[/bold]{title_padding}   │")
            self.console.print("│ ╭" + "─" * 73 + "╮ │")

            # Limit display lines (show first 10 + last 10 if > 20 lines)
            max_display_lines = 20
            if len(lines) <= max_display_lines:
                # Show all lines
                display_lines = lines
            else:
                # Show first 10, ellipsis, last 10
                first_lines = lines[:10]
                last_lines = lines[-10:]
                display_lines = first_lines + [f"... (showing 20 of {len(lines)} lines) ..."] + last_lines
            
            for line in display_lines:
                # Truncate long lines and pad short ones
                display_line = line[:73] if len(line) <= 73 else line[:70] + "..."
                padded_line = display_line.ljust(73)
                self.console.print(f"│ │ {padded_line[:71-2]}   │ │")
            
            self.console.print("│ ╰" + "─" * 73 + "╯ │")
            self.console.print("╰" + "─" * 77 + "╯")
            
        elif tool_name in ["run_command", "run_command_in_shell"] and args and 'command' in args:
            # Shell command execution
            command = args['command']
            
            # Check if this command should be displayed in a code box
            should_use_code_box = self._should_display_bash_in_box(command)
            
            if should_use_code_box:
                # Display complex bash commands in a code box (similar to Python)
                self.console.print("⏺ [bold]Bash[/bold]")
                header_title = self._get_bash_command_title(command)
                
                # Wrap the command for better display
                wrapped_lines = self._wrap_bash_command(command, max_width=71)
                
                self.console.print("╭" + "─" * 77 + "╮")
                title_padding = " " * (77 - len(header_title) - 4)
                self.console.print(f"│ [bold]{header_title}[/bold]{title_padding}   │")
                self.console.print("│ ╭" + "─" * 73 + "╮ │")

                # Limit display lines (show first 10 + last 10 if > 20 lines)
                max_display_lines = 20
                if len(wrapped_lines) <= max_display_lines:
                    display_lines = wrapped_lines
                else:
                    first_lines = wrapped_lines[:10]
                    last_lines = wrapped_lines[-10:]
                    # Calculate actual hidden lines
                    hidden_count = len(wrapped_lines) - 20
                    display_lines = first_lines + [f"... ({hidden_count} more lines) ..."] + last_lines
                
                for line in display_lines:
                    # Lines are already wrapped to fit, just pad them
                    padded_line = line.ljust(71)
                    self.console.print(f"│ │ {padded_line} │ │")
                
                self.console.print("│ ╰" + "─" * 73 + "╯ │")
                self.console.print("╰" + "─" * 77 + "╯")
            else:
                # Simple commands use the original format
                self.console.print(f"⏺ [bold]Bash[/bold]({command})")
            
        elif tool_name in ["ATAC_Upstream", "ATAC_Analysis", "ScATAC_Upstream", 
                           "ScATAC_Analysis", "RNA_Upstream", "RNA_Analysis",
                             "HiC_Upstream", "HiC_Analysis", "Spatial_Bin2Cell_Analysis", "Dock_Workflow"] and args and 'workflow_type' in args:
            # Special handling for workflow calls
            workflow_type = args['workflow_type']
            description = args.get('description', '')
            
            # Determine the workflow category and icon
            if tool_name == "ATAC_Upstream":
                icon = "🧬"  # DNA for upstream processing
                workflow_title = f"ATAC Upstream: {workflow_type}"
            elif tool_name == "ATAC_Analysis":
                icon = "📊"  # Chart for downstream analysis
                workflow_title = f"ATAC Analysis: {workflow_type}"
            elif tool_name == "ScATAC_Upstream":
                icon = "🧬"  # DNA for upstream processing
                workflow_title = f"scATAC Upstream: {workflow_type}"
            elif tool_name == "ScATAC_Analysis":
                icon = "📊"  # Chart for downstream analysis
                workflow_title = f"scATAC Analysis: {workflow_type}"
            elif tool_name == "RNA_Upstream":
                icon = "🧬"  # DNA for upstream processing
                workflow_title = f"RNA Upstream: {workflow_type}"
            elif tool_name == "RNA_Analysis":
                icon = "📊"  # Chart for downstream analysis
                workflow_title = f"RNA Analysis: {workflow_type}"
            elif tool_name == "HiC_Upstream":
                icon = "🧬"  # DNA for upstream processing
                workflow_title = f"Hi-C Upstream: {workflow_type}"
            elif tool_name == "Spatial_Bin2Cell_Analysis":
                icon = "🧬"  # DNA for upstream processing
                workflow_title = f"Spatial Bin2Cell Analysis: {workflow_type}"
            elif tool_name == "Dock_Workflow":
                icon = "🧬"  # DNA for molecular docking
                workflow_title = f"Molecular Docking: {workflow_type}"
            else:  # HiC_Analysis
                icon = "📊"  # Chart for downstream analysis
                workflow_title = f"Hi-C Analysis: {workflow_type}"
                        
            self.console.print(f"⏺ [bold]{icon} {tool_name}[/bold]")
            
            # Create a workflow-specific box
            self.console.print("╭" + "─" * 77 + "╮")
            title_padding = " " * (77 - len(workflow_title) - 4)
            self.console.print(f"│ [bold cyan]{workflow_title}[/bold cyan]{title_padding}   │")
            
            if description:
                self.console.print("│ ╭" + "─" * 73 + "╮ │")
                desc_line = description[:71] if len(description) <= 71 else description[:68] + "..."
                desc_padding = " " * (71 - len(desc_line))
                self.console.print(f"│ │ [dim]{desc_line}[/dim]{desc_padding} │ │")
                self.console.print("│ ╰" + "─" * 73 + "╯ │")
            
            self.console.print("╰" + "─" * 77 + "╯")
            
        else:
            # Generic tool call
            if args:
                # Try to show the most relevant argument
                key_arg = None
                if 'workflow_type' in args:
                    # Special handling for workflow functions that might not be caught above
                    workflow_type = args['workflow_type']
                    description = args.get('description', '')
                    if description:
                        key_arg = f"workflow_type='{workflow_type}', description='{description[:30]}...'" if len(description) > 30 else f"workflow_type='{workflow_type}', description='{description}'"
                    else:
                        key_arg = f"workflow_type='{workflow_type}'"
                elif 'file_path' in args:
                    key_arg = f"file_path='{args['file_path']}'"
                elif 'pattern' in args:
                    key_arg = f"pattern='{args['pattern']}'"
                elif 'query' in args:
                    key_arg = f"query='{args['query'][:50]}...'" if len(str(args['query'])) > 50 else f"query='{args['query']}'"
                elif 'code' in args:
                    # Display code for run_python and run_r tools
                    code_lines = str(args['code']).strip().split('\n')
                    if len(code_lines) == 1 and len(code_lines[0]) <= 60:
                        key_arg = f"code='{code_lines[0]}'"
                    elif len(code_lines) <= 3 and all(len(line) <= 50 for line in code_lines):
                        code_preview = '; '.join(line.strip() for line in code_lines)
                        key_arg = f"code='{code_preview[:70]}...'" if len(code_preview) > 70 else f"code='{code_preview}'"
                    else:
                        first_line = code_lines[0][:50]
                        key_arg = f"code='{first_line}... ({len(code_lines)} lines)'"
                
                if key_arg:
                    self.console.print(f"⏺ [bold]{tool_name}[/bold]({key_arg})")
                else:
                    self.console.print(f"⏺ [bold]{tool_name}[/bold](...)")
            else:
                self.console.print(f"⏺ [bold]{tool_name}[/bold]()")
        
        self.console.print()  # Add space after tool call
        
    def print_tool_result(self, tool_name: str, result: dict):
        """Print tool result in Claude Code style with diff support"""
        
        # Mark that tool execution is complete
        self._tools_executing = False
        # Clear current tool name since execution is done
        self._current_tool_name = None
        
        # Record tool result in conversation history with full result data
        result_content = ""
        terminal_display = ""
        
        if isinstance(result, dict):
            # Store the full result dict for proper formatting
            if 'stdout' in result:
                result_content = result['stdout']
            elif 'output' in result:
                result_content = result['output']
            elif 'result' in result:
                result_content = str(result['result'])
            else:
                result_content = str(result)
            
            # Capture the actual terminal display format
            if tool_name in ['run_python_code', 'run_julia_code', 'run_r_code', 'run_command', 'run_command_in_shell', 'bash']:
                # For code execution, preserve the full output structure
                terminal_display = str(result)
        else:
            result_content = str(result)
        
        metadata = {"tool_name": tool_name}
        if terminal_display:
            metadata["terminal_display"] = terminal_display
        metadata["full_result"] = result  # Store the complete result for formatting
        
        # Also capture what would appear in the terminal output box
        if isinstance(result, dict) and 'output' in result:
            output = result['output']
        elif isinstance(result, dict) and 'result' in result:
            output = result['result']
        else:
            output = str(result)

        if tool_name in ['run_python_code', 'run_julia_code', 'run_r_code']:
            try:
                import ast
                parsed_output = ast.literal_eval(output)
                if isinstance(parsed_output, dict) and 'stdout' in parsed_output.keys():
                    output = parsed_output['stdout']
            except:
                pass
        
        if output and output.strip():
            metadata["actual_terminal_output"] = output
        
        # Check for interpreter restart notification
        if isinstance(result, dict) and result.get("interpreter_restarted"):
            restart_reason = result.get("restart_reason", "Unknown reason")
            self.console.print(f"\n[yellow]⚠️  Python interpreter was automatically restarted due to: {restart_reason}[/yellow]")
            self.console.print(f"[dim]All previous variables and imports have been lost. You may need to re-import libraries.[/dim]\n")
        
        # Check for interpreter crash
        if isinstance(result, dict) and result.get("interpreter_crashed"):
            self.console.print(f"\n[red]💥 Python interpreter crashed and could not be restarted automatically.[/red]")
            self.console.print(f"[dim]Use [bold]/restart[/bold] command to manually reset the Python environment.[/dim]\n")
        
        self.add_to_conversation("tool_result", result_content, metadata)
        
        # Special handling for toolsets that print their own output - skip normal output box
        skip_tools = ['edit', 'write', 'read', 'file', 'glob', 'grep', 'ls', 'notebook', 'update_todo_status',
                     'add_todo', 'mark_task_done', 'complete_current_todo', 'work_on_next_todo']
        if any(tool in tool_name.lower() for tool in skip_tools) and isinstance(result, dict):
            if result.get('success'):
                # For successful operations, don't show any output box
                # The content was already printed by the toolset
                return
            

        # Show tool output in Claude Code style
        if isinstance(result, dict) and 'output' in result:
            output = result['output']
        elif isinstance(result, dict) and 'result' in result:
            output = result['result']
        else:
            output = str(result)

        if tool_name in ['run_python_code', 'run_julia_code', 'run_r_code']:
            import ast
            output = ast.literal_eval(output)
            if isinstance(output, dict) and 'stdout' in output.keys():
                output = output['stdout']

        if output and output.strip():
            # Check if this is a bash command output (should be multi-line)
            # vs other tool outputs (should be single line)
            is_bash_output = tool_name.lower() in ['run_command', 'run_command_in_shell', 'bash']
            
            if is_bash_output:
                # Multi-line display for bash command outputs
                # Handle escaped characters in output
                processed_output = output.replace('\\n', '\n').replace('\\t', '\t')
                lines = processed_output.strip().split('\n')
                max_width = 79
                content_width = max_width - 4  # Account for borders and padding
                
                # Wrap long lines in the output
                wrapped_lines = []
                for line in lines:
                    if len(line) <= content_width:
                        wrapped_lines.append(line)
                    else:
                        # Wrap long lines at word boundaries when possible
                        while line:
                            if len(line) <= content_width:
                                wrapped_lines.append(line)
                                break
                            
                            # Find a good break point
                            break_point = content_width
                            space_idx = line[:content_width].rfind(' ')
                            if space_idx > content_width * 0.6:  # Only break at space if it's not too early
                                break_point = space_idx + 1
                            
                            wrapped_lines.append(line[:break_point].rstrip())
                            line = line[break_point:].lstrip()
                
                # Limit display lines (show first 15 + last 15 if > 30 lines)
                max_display_lines = 30
                if len(wrapped_lines) <= max_display_lines:
                    display_lines = wrapped_lines
                else:
                    first_lines = wrapped_lines[:15]
                    last_lines = wrapped_lines[-15:]
                    hidden_count = len(wrapped_lines) - 30
                    display_lines = first_lines + [f"... ({hidden_count} more lines) ..."] + last_lines
                
                self.console.print("╭" + "─" * (max_width - 2) + "╮")
                self.console.print("│ [bold]Output[/bold]" + " " * (max_width - 9) + "│")
                self.console.print("├" + "─" * (max_width - 2) + "┤")
                
                for line in display_lines:
                    # Pad the line to fill the box width
                    padding = content_width - len(line)
                    self.console.print(f"│ {line}" + " " * padding + " │")
                
                self.console.print("╰" + "─" * (max_width - 2) + "╯")
                self.console.print()  # Add space after output
            else:
                # Single line display for other tool outputs (like ATAC workflows)
                max_width = 79
                content_width = max_width - 4  # Account for borders and padding
                
                # Truncate very long outputs to single line
                if len(output) > content_width:
                    truncated_output = output[:content_width-3] + "..."
                else:
                    truncated_output = output
                
                self.console.print("╭" + "─" * (max_width - 2) + "╮")
                self.console.print("│ [bold]Output[/bold]" + " " * (max_width - 9) + "│")
                self.console.print("├" + "─" * (max_width - 2) + "┤")
                
                # Pad the line to fill the box width
                padding = content_width - len(truncated_output)
                self.console.print(f"│ {truncated_output}" + " " * padding + " │")
                
                self.console.print("╰" + "─" * (max_width - 2) + "╯")
                self.console.print()  # Add space after output

    async def print_message(self):
        """Enhanced message handler with Claude Code style formatting"""
        try:
            while True:
                try:
                    message = await self.agent.events_queue.get()
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    continue
                    
                # Handle tool calls with Claude Code style
                if tool_calls := message.get("tool_calls"):
                    # Estimate tokens for tool calls message
                    tool_call_content = json.dumps(tool_calls)
                    # Update token estimate if we have access to the parent REPL instance
                    if hasattr(self, '_parent_repl') and hasattr(self._parent_repl, 'estimated_output_tokens'):
                        additional_tokens = self._parent_repl._estimate_tokens(tool_call_content)
                        self._parent_repl.estimated_output_tokens += additional_tokens
                    
                    for call in tool_calls:
                        tool_name = call.get('function', {}).get('name')
                        if tool_name:
                            try:
                                args = json.loads(call.get('function', {}).get('arguments', '{}'))
                            except:
                                args = {}
                            self.print_tool_call(tool_name, args)
                    continue
                    
                # Handle tool responses with enhanced formatting
                elif message.get("role") == "tool":
                    tool_name = message.get("tool_name", "")
                    content = message.get("content", "")
                    
                    # Show tool results in Claude Code style
                    try:
                        # Try to parse as JSON for structured results
                        result = json.loads(content)
                        self.print_tool_result(tool_name, result)
                    except:
                        # Fallback for plain text results
                        if content.strip():
                            # Create a simple output display for non-JSON results
                            self.print_tool_result(tool_name, {"output": content})
                    continue
                    
                # Skip assistant messages - we handle them in main loop via content_buffer
                if message.get("role") == "assistant":
                    continue
                
                # Only print other message types (like system messages, if any)
                print_agent_message_modern_style(
                    self.agent.name, 
                    message, 
                    self.console,
                    show_tool_details=False
                )
        except Exception as e:
            # Silently handle critical errors in print_message
            pass