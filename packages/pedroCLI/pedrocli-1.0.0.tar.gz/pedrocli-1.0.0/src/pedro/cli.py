#!/usr/bin/env python3
"""
Pedro CLI - Simplified version without ASCII animation
"""

import os
import sys
import time
import json
from typing import List
import shutil
from pathlib import Path

from rich.console import Console
from rich.text import Text
from rich.live import Live
from rich.spinner import Spinner
from rich.style import Style
from rich.align import Align
from rich.panel import Panel

from prompt_toolkit import prompt
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter

from pedro.api_client import (
    chat_send, load_conversation, save_conversation, append_message, RateLimitException, CONV_DIR
)

# Initialize console with proper settings
console = Console(force_terminal=True, color_system="auto")

# Configuration
CURRENT_CONV = "default"
SYSTEM_ROLE = "system"

# Fixed color styles
USER_COLOR = "cyan"
PEDRO_COLOR = "magenta"
SYSTEM_COLOR = "bright_black"
ERROR_COLOR = "red"
INFO_COLOR = "blue"

# Stats file path
STATS_FILE = os.path.join(os.path.expanduser("~"), ".pedro_stats.json")

class StatsManager:
    """Manages persistent conversation statistics"""
    
    def __init__(self):
        self.stats_file = STATS_FILE
        self.stats = self.load_stats()
    
    def load_stats(self):
        """Load statistics from JSON file"""
        try:
            if os.path.exists(self.stats_file):
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # Initialize default stats
                return {
                    "total_conversations": 0,
                    "total_messages": 0,
                    "total_tokens": 0,
                    "conversation_stats": {},
                    "first_run": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "last_run": time.strftime("%Y-%m-%d %H:%M:%S")
                }
        except (json.JSONDecodeError, IOError):
            # Return default stats if file is corrupted
            return {
                "total_conversations": 0,
                "total_messages": 0,
                "total_tokens": 0,
                "conversation_stats": {},
                "first_run": time.strftime("%Y-%m-%d %H:%M:%S"),
                "last_run": time.strftime("%Y-%m-%d %H:%M:%S")
            }
    
    def save_stats(self):
        """Save statistics to JSON file"""
        try:
            self.stats["last_run"] = time.strftime("%Y-%m-%d %H:%M:%S")
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(self.stats, f, indent=2, ensure_ascii=False)
        except IOError as e:
            console.print(f"[red]Warning: Could not save stats: {e}[/]")
    
    def update_conversation_stats(self, conversation_name, messages_count, tokens_count):
        """Update stats for a specific conversation"""
        if conversation_name not in self.stats["conversation_stats"]:
            self.stats["conversation_stats"][conversation_name] = {
                "created": time.strftime("%Y-%m-%d %H:%M:%S"),
                "messages": 0,
                "tokens": 0,
                "last_updated": time.strftime("%Y-%m-%d %H:%M:%S")
            }
        
        conv_stats = self.stats["conversation_stats"][conversation_name]
        conv_stats["messages"] += messages_count
        conv_stats["tokens"] += tokens_count
        conv_stats["last_updated"] = time.strftime("%Y-%m-%d %H:%M:%S")
        
        # Update global stats
        self.stats["total_messages"] += messages_count
        self.stats["total_tokens"] += tokens_count
        
        self.save_stats()
    
    def new_conversation(self, conversation_name):
        """Record a new conversation"""
        self.stats["total_conversations"] += 1
        self.save_stats()
    
    def get_stats(self):
        """Get current statistics"""
        return self.stats
    
    def display_stats(self):
        """Display formatted statistics"""
        stats = self.get_stats()
        
        console.print(f"[bold magenta]📊 Pedro Statistics[/bold magenta]")
        console.print(f"{'='*40}")
        console.print(f"Total Conversations: {stats['total_conversations']}")
        console.print(f"Total Messages: {stats['total_messages']}")
        console.print(f"Total Tokens: {stats['total_tokens']:,}")
        console.print(f"First Run: {stats['first_run']}")
        console.print(f"Last Run: {stats['last_run']}")
        
        if stats['conversation_stats']:
            console.print(f"\n[bold cyan]Conversations:[/bold cyan]")
            for name, conv_stats in stats['conversation_stats'].items():
                console.print(f"  {name}: {conv_stats['messages']} messages, {conv_stats['tokens']:,} tokens")
        else:
            console.print("\n[dim]No conversations yet[/dim]")

# Chat completer
COMMANDS = [
    '/help', '/new', '/exit', '/history', '/system', 
    '/save', '/load', '/clear', '/stats', '/model', 
    '/theme', '/config', '/rename', '/delete', '/list', '/gecowave'
]
command_completer = WordCompleter(COMMANDS, ignore_case=True)

class OptimizedStreamingChatUI:
    """Chat interface with optimized streaming that preserves text"""
    
    def __init__(self):
        self.console = console
        self.current_conv = CURRENT_CONV
        self.history = InMemoryHistory()
        self.stats_manager = StatsManager()
        self._setup_terminal()
    
    def _setup_terminal(self):
        """Setup terminal"""
        os.system('cls' if os.name == 'nt' else 'clear')
        self.term_width, self.term_height = shutil.get_terminal_size()
    
    def play_startup_animation(self):
        """Startup animation with PEDRO logo and progress bar (3.5 seconds)"""
        duration = 3.5  # 3.5 seconds
        
        # Colori per l'animazione gradiente
        colors = ["magenta", "cyan", "yellow", "green", "blue", "red"]
        
        # Logo PEDRO ASCII art semplificato
        logo_lines = [
            "█████   ██████  █████   █████   ████ ",
            "██  ██  ██      ██  ██  ██  ██  ██  ██",
            "█████   █████   ██  ██  █████   ██  ██",
            "██      ██      ██  ██  ██ ██   ██  ██",
            "██      ██████  █████   ██  ██   ████ ",
            "                                       "
        ]

        try:
            with Live(
                console=self.console,
                refresh_per_second=15,  # Aumentato per fluidità
                transient=False,        # Mantiene il contenuto visibile
                auto_refresh=True       # Refresh automatico
            ) as live:
                start_time = time.time()
                
                while True:
                    elapsed = time.time() - start_time
                    
                    if elapsed >= duration:
                        break
                    
                    # Calcola percentuale di completamento (0-100%)
                    percent = min(100, (elapsed / duration) * 100)
                    
                    # Crea l'effetto gradiente per il logo
                    color_idx = int(elapsed * 3) % len(colors)
                    color = colors[color_idx]
                    
                    # Costruisci il logo colorato
                    logo_colored = []
                    for i, line in enumerate(logo_lines):
                        line_color = colors[(color_idx + i) % len(colors)]
                        logo_colored.append(f"[{line_color} bold]{line}[/]")
                    
                    # Crea la barra di progresso
                    bar_width = 40
                    filled_width = int((percent / 100) * bar_width)
                    
                    bar = "█" * filled_width + "░" * (bar_width - filled_width)
                    
                    # Spinner animato
                    spinner_chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
                    spinner = spinner_chars[int(elapsed * 10) % len(spinner_chars)]
                    
                    # Costruisci il display completo
                    display_parts = [
                        "",
                        *logo_colored,
                        "",
                        f"[{color} bold]Pedro AI Assistant v1.0.0[/]",
                        f"[{color}]Initializing...[/]",
                        "",
                        f"{spinner} [{color}]{spinner}[/] [{color}]{spinner}[/]",
                        "",
                        f"[{color}]{bar}[/]",
                        f"[{color} bold]{percent:.1f}%[/]",
                        ""
                    ]
                    
                    # Crea il pannello centrato
                    content_panel = Panel.fit(
                        "\n".join(display_parts),
                        border_style=color,
                        title="[bold white]Pedro AI[/]"
                    )
                    
                    # Centra verticalmente e orizzontalmente
                    centered_content = Align.center(content_panel, vertical="middle")
                    live.update(centered_content)
                    time.sleep(0.05)  # ~20 FPS per fluidità ottimale
                
                # Messaggio finale breve
                final_display = Text.from_markup(
                    f"\n[{colors[2]} bold]✓ Pedro è pronto![/]\n"
                )
                live.update(final_display)
                time.sleep(0.5)
                
        except KeyboardInterrupt:
            pass
        except Exception as e:
            # Fallback se l'animazione fallisce
            self.console.print("[yellow]Animazione non disponibile, avvio normale...[/]")
            time.sleep(0.5)
    
    def print_header(self):
        """Print animated 3D ASCII header with centering"""
        import time
        
        # Header content with 3D styling
        title_lines = [
            "╔══════════════════════════════════════════════════════╗",
            "║                      PEDRO CLI                       ║",
            "║               v1.0.0 • dimmi chi ami                 ║",
            "╚══════════════════════════════════════════════════════╝",
            "                                                        ",
        ]
        
        # Color palette
        colors = ["bright_cyan", "bright_magenta", "bright_yellow"]
        
        try:
            # Fast animation: reveal complete lines
            with Live(
                console=self.console,
                refresh_per_second=60,
                transient=False,
                auto_refresh=False
            ) as live:
                
                # Build complete header progressively
                displayed_lines = []
                
                for i, line in enumerate(title_lines):
                    # Color coding for different sections
                    if i < 6:  # PEDRO title
                        color = "bright_cyan"
                    elif i < 8:  # PEDRO AI
                        color = "bright_magenta"
                    else:  # Version info
                        color = "bright_yellow"
                    
                    # Build colored line
                    colored_line = ""
                    for char in line:
                        if char in ['█', '║', '╔', '╗', '╠', '╣', '╚', '╝', '═']:
                            colored_line += f"[{color}]{char}[/]"
                        elif char in ['✨']:
                            colored_line += f"[bright_yellow]{char}[/]"
                        else:
                            colored_line += f"[white]{char}[/]"
                    
                    displayed_lines.append(colored_line)
                    
                    # Show all lines built so far, centered
                    full_header = "\n".join(displayed_lines)
                    centered_header = Align.center(Text.from_markup(full_header))
                    live.update(centered_header)
                    live.refresh()
                    
                    # Ultra-fast delay between lines
                    time.sleep(0.05)
                
                # Quick final glow (0.2s total)
                for color in ["bright_cyan", "bright_magenta", "bright_yellow"]:
                    final_lines = []
                    for j, line in enumerate(title_lines):
                        if j < 6:
                            line_color = color
                        elif j < 8:
                            line_color = "bright_magenta"
                        else:
                            line_color = "bright_yellow"
                        
                        colored_line = ""
                        for char in line:
                            if char in ['█', '║', '╔', '╗', '╠', '╣', '╚', '╝', '═']:
                                colored_line += f"[{line_color}]{char}[/]"
                            elif char in ['✨']:
                                colored_line += f"[bright_yellow]{char}[/]"
                            else:
                                colored_line += f"[white]{char}[/]"
                        final_lines.append(colored_line)
                    
                    final_text = "\n".join(final_lines)
                    centered_final = Align.center(Text.from_markup(final_text))
                    live.update(centered_final)
                    live.refresh()
                    time.sleep(0.07)
                
        except (KeyboardInterrupt, Exception):
            # Static fallback - centered
            for line in title_lines:
                if "PEDRO AI" in line:
                    self.console.print(Align.center(f"[bright_magenta]{line}[/]"))
                elif "v1.0.0" in line:
                    self.console.print(Align.center(f"[bright_yellow]{line}[/]"))
                else:
                    self.console.print(Align.center(f"[bright_cyan]{line}[/]"))
    
    def display_message(self, role: str, content: str):
        """Display message with proper formatting"""
        if role == "user":
            self.console.print(f"[{USER_COLOR}]you:[/] {content}")
        elif role == "assistant":
            self.console.print(f"[{PEDRO_COLOR}]pedro:[/] {content}")
        elif role == "system":
            self.console.print(f"[{SYSTEM_COLOR}]{content}[/]")
    
    def display_messages(self, messages: List[dict]):
        """Display conversation history"""
        for msg in messages:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            if content.strip():
                self.display_message(role, content)
    
    def stream_response(self, full_text: str, delay: float = 0.005):
        """Stream response text with cursor, optimized for speed and persistence"""
        if not full_text:
            return
            
        prefix = f"[{PEDRO_COLOR}]pedro:[/] "
        cursor_char = "▋"
        
        streamed_text = ""
        
        # Calculate optimal delay based on text length
        text_length = len(full_text)
        if text_length > 500:
            delay = 0.03  # Ancora più veloce per testi molto lunghi
        elif text_length > 100:
            delay = 0.1  # Più veloce per testi lunghi
        else:
            delay = 0.3  # Default per testi più corti
        
        try:
            # Use Live without transient to keep text
            with Live(
                console=self.console,
                refresh_per_second=15,  # Ridotto per evitare sovraccarico
                transient=False,  # Mantiene il contenuto visibile
                auto_refresh=False  # Controlliamo manualmente il refresh
            ) as live:
                chunk_size = 10  # Processa i caratteri in gruppi più grandi
                for i in range(0, len(full_text), chunk_size):
                    chunk = full_text[i:i+chunk_size]
                    streamed_text += chunk
                    
                    # Aggiorna meno frequentemente
                    if i % 30 == 0 or i + chunk_size >= len(full_text):
                        cursor_visible = (i % 30 == 0)
                        cursor = cursor_char if cursor_visible else ""
                        
                        live.update(Text.from_markup(prefix + streamed_text + cursor))
                        live.refresh()
                    
                    # Usa un delay più breve per evitare blocchi
                    if i % 50 == 0:  # Aggiungi controllo interruzione periodico
                        time.sleep(delay)
                
                # Aggiornamento finale senza cursore
                live.update(Text.from_markup(prefix + streamed_text))
                live.refresh()
        except KeyboardInterrupt:
            # Gestisci l'interruzione da tastiera
            self.console.print(f"\n[{PEDRO_COLOR}]pedro:[/] {streamed_text}")
            self.console.print("\n[bold yellow]Streaming interrotto.[/bold yellow]")
            return
        except Exception as e:
            # In caso di errore, stampa comunque il testo completo
            self.console.print(f"[{PEDRO_COLOR}]pedro:[/] {full_text}")
            # Stampa l'errore solo in modalità debug
            # self.console.print(f"[red]Error in streaming: {e}[/]", stderr=True)
        
        # Aggiungi una riga vuota dopo che il contesto Live termina
        self.console.print()

    
    def print_help(self):
        """Print help with all available commands"""
        help_text = """
[bold magenta]Available Commands:[/bold magenta]

[bold cyan]Basic Commands:[/bold cyan]
  /help    show this help message
  /new     start new conversation
  /exit    exit pedro
  /clear   clear screen and show current conversation
  /history show current conversation history

[bold cyan]System Commands:[/bold cyan]
  /system  set system prompt (usage: /system <message>)
  /config  show current configuration
  /model   show AI model information
  /stats   show conversation statistics

[bold cyan]Conversation Management:[/bold cyan]
  /save    save conversation (usage: /save <name>)
  /load    load conversation (usage: /load <name>)
  /list    list saved conversations
  /rename  rename conversation (usage: /rename <old> <new>)
  /delete  delete conversation (usage: /delete <name>)

[bold cyan]Interface:[/bold cyan]
  /theme   toggle color theme (light/dark)
"""
        self.console.print(help_text)
    
    def show_rate_limit(self, block_until: float):
        """Show rate limit with cool animations"""
        remaining = max(0, int(block_until - time.time()))
        total_time = remaining
        
        # Colori per l'animazione
        colors = ["red", "yellow", "green", "blue", "magenta", "cyan"]
        
        # Caratteri per la barra di progresso
        bar_chars = "▓░"
        
        # Messaggi casuali per intrattenere l'utente
        messages = [
                "sei una merda e scrivi troppo ti vuoi calmare",
                "BASTA",
                "NO",
                "@pedrotetraedobot: inculati"
        ]
        
        import random
        message = random.choice(messages)
        
        self.console.print(f"\n[bold red]{message}[/]\n")
        
        try:
            # Ridotto refresh_per_second da 5 a 2 per ridurre il carico sull'executor
            with Live(
                console=self.console,
                refresh_per_second=2,
                transient=True
            ) as live:
                start_time = time.time()
                
                while remaining > 0:
                    # Calcola il tempo rimanente
                    remaining = max(0, int(block_until - time.time()))
                    elapsed = time.time() - start_time
                    
                    # Calcola la percentuale di completamento
                    percent_done = min(1.0, elapsed / total_time) if total_time > 0 else 1.0
                    bar_width = 30  # Larghezza della barra di progresso
                    filled_width = int(bar_width * percent_done)
                    
                    # Crea la barra di progresso colorata
                    color_idx = int(elapsed * 3) % len(colors)
                    color = colors[color_idx]
                    
                    # Crea un'animazione pulsante
                    pulse = int(elapsed * 4) % 2 == 0
                    style = "bold" if pulse else ""
                    
                    # Crea la barra di progresso
                    bar = f"[{color} {style}]{bar_chars[0] * filled_width}{bar_chars[1] * (bar_width - filled_width)}[/]" 
                    
                    # Aggiungi un effetto di spinner
                    spinner_chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
                    spinner = spinner_chars[int(elapsed * 10) % len(spinner_chars)]
                    
                    # Formatta il tempo rimanente
                    time_text = f"[bold white]{remaining}s[/]"
                    
                    # Assembla il display completo
                    display = Text.from_markup(f"\n{spinner} [bold {color}]Rate limit[/] {time_text}\n\n{bar} {int(percent_done*100)}%\n")
                    
                    live.update(display)
                    
                    # Aumentato il tempo di sleep per ridurre il carico
                    time.sleep(0.2)
                    
                    # Esci dal ciclo se il tempo è scaduto
                    if remaining <= 0:
                        break
                    
                try:
                    # Messaggio finale
                    final_message = Text.from_markup("\n[bold green]✓ Pronto! Puoi continuare a chattare con Pedro![/]\n")
                    live.update(final_message)
                    time.sleep(0.5)  # Ridotto ulteriormente il tempo di visualizzazione del messaggio finale
                except Exception:
                    # Ignora eventuali errori durante l'aggiornamento finale
                    pass
        except KeyboardInterrupt:
            # Permetti all'utente di interrompere l'attesa
            self.console.print("\n[bold yellow]Attesa interrotta. Prova a inviare un messaggio più tardi.[/bold yellow]\n")
            return
        except Exception as e:
            # In caso di errore, mostra un messaggio semplice
            self.console.print(f"\n[bold red]Rate limit attivo per {remaining} secondi.[/bold red]\n")
    
    def clear_screen(self, show_header=True):
        """Clear screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
        self._setup_terminal()
        if show_header:
            self.print_header()
    
    def gecowave_animation(self):
        """Interactive Gecowave animation - Press Ctrl+C to exit"""
        import webbrowser
        
        # Extended color palette for vibrant effects
        colors = ["red", "magenta", "cyan", "yellow", "green", "blue", "bright_red", "bright_cyan", "bright_yellow"]
        
        # Gecowave ASCII art
        gecowave_lines = [
    " ██████  ███████   ██████   ██████  ██     ██    ███    ██     ██ ███████      ████████  ██████  ██████  ",
    "██       ██       ██    ██ ██    ██ ██     ██   ██ ██   ██     ██ ██              ██    ██    ██ ██   ██ ",
    "██  ███  ██████   ██       ██    ██ ██  █  ██  ██   ██   ██   ██  ██████          ██    ██    ██ ██████  ",
    "██    ██ ██       ██       ██    ██ ██ ███ ██ ████████    ██ ██   ██              ██    ██    ██ ██       ",
    "██    ██ ██       ██    ██ ██    ██ ██ ███ ██ ██     ██    ███    ██        █     ██    ██    ██ ██       ",
    " ██████  ███████   ██████   ██████   ██   ██  ██     ██     █     ███████   █     ██     ██████  ██      "
]

        try:
            with Live(
                console=self.console,
                refresh_per_second=15,
                transient=False,
                auto_refresh=True
            ) as live:
                
                start_time = time.time()
                
                while True:
                    elapsed = time.time() - start_time
                    
                    # Create dynamic color cycling effect
                    color_offset = int(elapsed * 6) % len(colors)
                    
                    # Build animated logo with wave effect
                    animated_lines = []
                    for i, line in enumerate(gecowave_lines):
                        line_color = colors[(color_offset + i) % len(colors)]
                        animated_lines.append(f"[{line_color} bold]{line}[/]")
                    
                    # Add pulsing border effect
                    border_color = colors[int(elapsed * 4) % len(colors)]
                    
                    # Build display with clickable URL
                    display_parts = [
                        "",
                        *animated_lines,
                        "",
                        f"[{colors[(color_offset + 2) % len(colors)]} bold][link=https://gecowave.top/riba/]la riba non è d'accordo con questa affermazione.[/link][/{colors[(color_offset + 2) % len(colors)]} bold]",
                        "",
                        f"[{colors[(color_offset + 3) % len(colors)]}]🔗 [link=https://gecowave.top]Visit Gecowave[/link] [/{colors[(color_offset + 3) % len(colors)]}]",
                        "",
                        f"[{colors[(color_offset + 4) % len(colors)]} bold]CONTROLS:[/{colors[(color_offset + 4) % len(colors)]} bold]",
                        f"[{colors[(color_offset + 5) % len(colors)]}]🔗 Press Ctrl+C to exit[/{colors[(color_offset + 5) % len(colors)]}]",
                        f"[{colors[(color_offset + 6) % len(colors)]}]🔗 Press 'o' to open URL in browser[/{colors[(color_offset + 6) % len(colors)]}]",
                        f"[{colors[(color_offset + 7) % len(colors)]}]🔗 Colors change automatically[/{colors[(color_offset + 7) % len(colors)]}]",
                        "",
                        f"[{colors[(color_offset + 1) % len(colors)]} dim]Click anywhere on the ASCII art to visit Gecowave![/{colors[(color_offset + 1) % len(colors)]} dim]",
                        ""
                    ]
                    
                    # Create centered panel
                    content_panel = Panel.fit(
                        "\n".join(display_parts),
                        border_style=border_color,
                        title=f"[{border_color} bold]✨ GECOWAVE ANIMATION ✨[/{border_color} bold]",
                        subtitle=f"[{colors[(color_offset + 1) % len(colors)]}]Interactive Mode[/{colors[(color_offset + 1) % len(colors)]}]"
                    )
                    
                    centered_content = Align.center(content_panel, vertical="middle")
                    live.update(centered_content)
                    
                    try:
                        time.sleep(0.2)
                    except KeyboardInterrupt:
                        break
                
        except KeyboardInterrupt:
            self.console.print("\n[green]Animation stopped.[/]")
        except Exception as e:
            self.console.print(f"[yellow]Animation error: {e}[/yellow]")
            self.console.print("[yellow]Press Enter to continue...[/yellow]")
            input()

    def get_user_input(self) -> str:
        """Get user input"""
        try:
            user_input = prompt(
                "> ",
                history=self.history,
                auto_suggest=AutoSuggestFromHistory(),
                completer=command_completer,
                complete_while_typing=True
            )
            return user_input.strip()
        except (KeyboardInterrupt, EOFError):
            return "/exit"
    
    def run(self):
        """Main chat loop"""
        self.clear_screen(show_header=False)  # Pulisce lo schermo
        self.play_startup_animation()         # Mostra l'animazione
        self.clear_screen()                   # Pulisce e mostra l'header
        
        # Always start with a new chat
        save_conversation([], self.current_conv)
        self.console.print("[dim]Type /help for commands, /exit to quit[/dim]")
        
        while True:
            try:
                # Get user input
                user_input = self.get_user_input()
                
                if not user_input:
                    continue
                
                # Handle commands
                if user_input.startswith("/"):
                    parts = user_input.split(" ", 1)
                    cmd = parts[0].lower()
                    arg = parts[1].strip() if len(parts) > 1 else ""
                    
                    if cmd == "/help":
                        self.print_help()
                    elif cmd == "/exit":
                        self.console.print("goodbye")
                        break
                    elif cmd == "/new":
                        save_conversation([], self.current_conv)
                        self.clear_screen()
                        self.console.print("new conversation")
                    elif cmd == "/clear":
                        self.clear_screen()
                        messages = load_conversation(self.current_conv)
                        if messages:
                            self.display_messages(messages)
                    elif cmd == "/history":
                        messages = load_conversation(self.current_conv)
                        self.display_messages(messages)
                    elif cmd == "/system":
                        if not arg:
                            self.console.print("usage: /system <message>")
                        else:
                            messages = load_conversation(self.current_conv)
                            messages = [m for m in messages if m.get("role") != SYSTEM_ROLE]
                            messages.insert(0, {"role": SYSTEM_ROLE, "content": arg})
                            save_conversation(messages, self.current_conv)
                            self.console.print("system updated")
                    elif cmd == "/save":
                        if not arg:
                            self.console.print("usage: /save <name>")
                        else:
                            messages = load_conversation(self.current_conv)
                            save_conversation(messages, arg)
                            self.console.print(f"saved as '{arg}'")
                    elif cmd == "/load":
                        if not arg:
                            self.console.print("usage: /load <name>")
                        else:
                            try:
                                messages = load_conversation(arg)
                                save_conversation(messages, self.current_conv)
                                self.clear_screen()
                                self.display_messages(messages)
                            except FileNotFoundError:
                                self.console.print(f"[red]conversation '{arg}' not found[/]")
                    elif cmd == "/stats":
                        messages = load_conversation(self.current_conv)
                        total_messages = len(messages)
                        user_messages = len([m for m in messages if m.get("role") == "user"])
                        assistant_messages = len([m for m in messages if m.get("role") == "assistant"])
                        total_chars = sum(len(m.get("content", "")) for m in messages)
                        
                        stats_text = f"""
[bold cyan]Conversation Statistics[/bold cyan]
Total messages: {total_messages}
User messages: {user_messages}
Assistant messages: {assistant_messages}
Total characters: {total_chars}
"""
                        self.console.print(stats_text)
                    elif cmd == "/model":
                        self.console.print("[bold cyan]AI Model Information[/bold cyan]")
                        self.console.print("Model: Pedro AI Assistant v1.0.0")
                        self.console.print("Provider: Custom API")
                    elif cmd == "/config":
                        self.console.print("[bold cyan]Current Configuration[/bold cyan]")
                        self.console.print(f"Current conversation: {self.current_conv}")
                        self.console.print(f"Terminal size: {self.term_width}x{self.term_height}")
                    elif cmd == "/list":
                        from pathlib import Path
                        conversations = [f.stem for f in Path(CONV_DIR).glob("*.json")]
                        if conversations:
                            self.console.print("[bold cyan]Saved Conversations:[/bold cyan]")
                            for conv in sorted(conversations):
                                self.console.print(f"  • {conv}")
                        else:
                            self.console.print("[yellow]No saved conversations found[/]")
                    elif cmd == "/rename":
                        if not arg or len(arg.split()) != 2:
                            self.console.print("usage: /rename <old_name> <new_name>")
                        else:
                            old_name, new_name = arg.split()
                            try:
                                messages = load_conversation(old_name)
                                save_conversation(messages, new_name)
                                # Optional: delete old file
                                old_file = Path(CONV_DIR) / f"{old_name}.json"
                                if old_file.exists():
                                    old_file.unlink()
                                self.console.print(f"[green]Renamed '{old_name}' to '{new_name}'[/]")
                            except FileNotFoundError:
                                self.console.print(f"[red]conversation '{old_name}' not found[/]")
                    elif cmd == "/delete":
                        if not arg:
                            self.console.print("usage: /delete <name>")
                        else:
                            from pathlib import Path
                            file_path = Path(CONV_DIR) / f"{arg}.json"
                            if file_path.exists():
                                file_path.unlink()
                                self.console.print(f"[green]Deleted conversation '{arg}'[/]")
                            else:
                                self.console.print(f"[red]conversation '{arg}' not found[/]")
                    elif cmd == "/theme":
                        self.console.print("[yellow]Theme switching not implemented yet[/]")
                    elif cmd == "/gecowave":
                        self.clear_screen()
                        self.gecowave_animation()
                        self.clear_screen()
                        self.console.print("[dim]Gecowave animation completed! Type /help for commands[/dim]")
                    else:
                        self.console.print(f"[red]unknown command: {cmd}[/]")
                else:
                    # Handle chat message
                    messages = load_conversation(self.current_conv)
                    messages.append({"role": "user", "content": user_input})
                    
                    # Show loading with timeout indicator
                    start_time = time.time()
                    with Live(
                        Spinner("dots", text="pedro is thinking..."),
                        console=self.console,
                        refresh_per_second=4,
                        transient=True
                    ) as live:
                        try:
                            # Aggiorna l'animazione mentre aspetta
                            for i in range(30):  # Massimo 30 secondi di attesa
                                if i > 0 and i % 5 == 0:  # Ogni 5 secondi
                                    live.update(Spinner("dots", text=f"pedro is thinking... ({i}s)"))
                                
                                # Prova a ottenere la risposta con un timeout breve
                                try:
                                    response = chat_send(messages)
                                    break  # Esci dal ciclo se la risposta è arrivata
                                except RateLimitException as e:
                                    live.stop()
                                    self.show_rate_limit(e.block_until)
                                    response = None
                                    break
                                except Exception as e:
                                    # Se l'errore non è di timeout, esci dal ciclo
                                    if "timeout" not in str(e).lower():
                                        live.stop()
                                        self.console.print(f"[red]error: {e}[/]")
                                        response = None
                                        break
                                
                                # Breve pausa prima di riprovare
                                time.sleep(1)
                            
                            # Se siamo usciti dal ciclo senza risposta, mostra un errore
                            if response is None and i >= 29:
                                live.stop()
                                self.console.print("[red]Timeout: La richiesta ha impiegato troppo tempo.[/]")
                                continue
                        except KeyboardInterrupt:
                            live.stop()
                            self.console.print("\n[bold yellow]Richiesta interrotta.[/bold yellow]")
                            continue
                        except Exception as e:
                            live.stop()
                            from rich.text import Text
                            error_text = Text("error: ", style="red")
                            error_text.append(str(e))
                            self.console.print(error_text)
                            continue
                    
                    # Stream response
                    self.stream_response(response)
                    
                    # Save response
                    messages.append({"role": "assistant", "content": response})
                    save_conversation(messages, self.current_conv)
                    
            except KeyboardInterrupt:
                self.console.print("\ngoodbye")
                break
            except Exception as e:
                self.console.print(f"[red]error: {e}[/]")

def main():
    """Main entry point"""
    try:
        app = OptimizedStreamingChatUI()
        app.run()
    except KeyboardInterrupt:
        console.print("goodbye")
        sys.exit(0)

if __name__ == "__main__":
    main()