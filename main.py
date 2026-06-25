##################################################
#          (Main) Orchestration PIPELINE         #
##################################################
import sys
import io
# Force UTF-8 output so rich box-drawing chars work on Windows terminals
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
else:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import random
import os
import time

# ── Rich imports ──────────────────────────────────────────────────────────────
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.columns import Columns
from rich.rule import Rule
from rich.spinner import Spinner
from rich.live import Live
from rich.align import Align
from rich.prompt import Prompt
from rich import box
from rich.markup import escape

# ── Project imports ───────────────────────────────────────────────────────────
from db_Config import init_database, query_local_db
from networkDiagnostics import is_online
from chatbot_csv_handler import load_dataset, get_chatbot_response, load_short_forms
from API_Fallback import ask_openai, ask_gemini
from document_qa import ask_llm, extract_text_from_pdf, extract_text_from_docx

# ── Setup ─────────────────────────────────────────────────────────────────────
console = Console()
BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, 'data')
DATASET  = load_dataset(os.path.join(DATA_DIR, 'chatbot_dataset.csv'))
SHORT_FORMS = load_short_forms(os.path.join(DATA_DIR, 'short_qa.csv'))

BRAND_COLOR   = "bright_cyan"
BOT_COLOR     = "cyan"
USER_COLOR    = "bright_green"
SOURCE_COLORS = {
    "Database":  "yellow",
    "Dataset":   "bright_blue",
    "Gemini":    "magenta",
    "Doc Q&A":   "bright_yellow",
    "System":    "red",
}

FAREWELLS = [
    "Goodbye!",
    "See you soon!",
    "Later, Master!",
    "Got it boss, logging off.",
]

# ── Helpers ───────────────────────────────────────────────────────────────────

def print_header():
    """Render the branded splash header."""
    console.clear()

    title = Text()
    title.append("  CampusEdu", style="bold bright_cyan")
    title.append(" Smart Chatbot", style="bold white")
    title.append("  v2.0", style="bold cyan")

    subtitle = Text()
    subtitle.append("\n  Powered by ", style="dim white")
    subtitle.append("Local Knowledge Base", style="bold bright_cyan")
    subtitle.append(" + ", style="dim white")
    subtitle.append("Gemini", style="bold magenta")

    console.print(Panel(
        Align.center(title + subtitle),
        border_style="bright_cyan",
        box=box.DOUBLE_EDGE,
        padding=(1, 6),
    ))


def print_help_table():
    """Print command reference table."""
    table = Table(
        title="[bold bright_cyan]Available Commands[/]",
        box=box.ROUNDED,
        border_style="cyan",
        show_header=True,
        header_style="bold white",
        padding=(0, 2),
    )
    table.add_column("Command", style="bright_cyan", no_wrap=True)
    table.add_column("Description", style="white")

    table.add_row("/doc <filename>", "Load a PDF or DOCX for Q&A")
    table.add_row("<filename>.pdf",  "Auto-detect & load PDF")
    table.add_row("<filename>.docx", "Auto-detect & load DOCX")
    table.add_row("/clear",          "Unload active document")
    table.add_row("/help",           "Show this help table")
    table.add_row("exit / quit / bye","End the session")

    console.print(table)
    console.print()


def print_rule(label: str = ""):
    console.print(Rule(label, style="dim cyan"))


def bot_bubble(message: str, source: str = ""):
    """Render a bot response as a styled panel."""
    color  = SOURCE_COLORS.get(source, BOT_COLOR)
    header = f"[bold {color}]>> Bot"
    if source:
        header += f"  [dim]({source})[/dim]"
    header += "[/]"

    console.print(Panel(
        Text(message, style="white"),
        title=header,
        title_align="left",
        border_style=color,
        box=box.ROUNDED,
        padding=(0, 2),
    ))


def user_bubble(message: str):
    """Render a user message as a right-aligned styled text."""
    text = Text()
    text.append("You › ", style=f"bold {USER_COLOR}")
    text.append(message, style="bright_white")
    console.print(Align.right(text))
    console.print()


def thinking_spinner(label: str = "Thinking…"):
    """Return a Live context that shows an animated spinner."""
    return Live(
        Spinner("dots2", text=f"[dim cyan]{label}[/dim cyan]"),
        console=console,
        refresh_per_second=12,
        transient=True,
    )


def doc_status_panel(name: str):
    console.print(Panel(
        f"[bold bright_yellow]>> Active Document:[/] [white]{escape(name)}[/white]\n"
        "[dim]All questions answered from this document. Type [bold]/clear[/bold] to exit doc mode.[/dim]",
        border_style="bright_yellow",
        box=box.SIMPLE_HEAVY,
        padding=(0, 2),
    ))


# ── Core response logic ───────────────────────────────────────────────────────

def chatbot_response(user_input: str):
    """Returns (response_text, source_label)."""

    # 1. Local DB
    db_answer = query_local_db(user_input)
    if db_answer:
        return db_answer, "Database"

    # 2. CSV dataset
    dataset_response = get_chatbot_response(user_input, DATASET, SHORT_FORMS)
    if dataset_response:
        return dataset_response, "Dataset"

    # 3. Online / Gemini
    if not is_online():
        return "Network connection is unavailable. Cannot perform online search.", "System"

    answer = ask_gemini(user_input)
    return answer, "Gemini"


# ── Main loop ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    init_database()
    print_header()
    print_help_table()
    print_rule("Session Started")

    active_doc_text = None
    active_doc_name = None

    while True:
        try:
            # ── Prompt ──
            console.print()
            if active_doc_name:
                prompt_label = f"[bold bright_yellow]📄 [{escape(active_doc_name)}] You[/] [dim]›[/dim] "
            else:
                prompt_label = f"[bold {USER_COLOR}]You[/] [dim]›[/dim] "

            user_query = console.input(prompt_label).strip()

            # ── Guards ──
            if not user_query:
                continue

            if user_query.lower() in ("exit", "quit", "bye"):
                console.print()
                console.print(Panel(
                    f"[bold bright_cyan]{random.choice(FAREWELLS)}[/]",
                    border_style="bright_cyan",
                    box=box.ROUNDED,
                    padding=(0, 4),
                ))
                print_rule("Session Ended")
                break

            # ── Commands ──
            if user_query.lower() == "/help":
                print_help_table()
                continue

            if user_query.lower() == "/clear":
                active_doc_text = None
                active_doc_name = None
                bot_bubble("Document context cleared. Switched back to normal search mode.", "System")
                continue

            # ── Doc loading ──
            if user_query.startswith("/doc ") or user_query.lower().endswith((".pdf", ".docx")):
                file_path = user_query[5:].strip() if user_query.startswith("/doc ") else user_query

                if not os.path.exists(file_path):
                    bot_bubble(f"File not found: '{file_path}'", "System")
                    continue

                ext = os.path.splitext(file_path)[1].lower()
                with thinking_spinner("Reading document…"):
                    try:
                        if ext == ".pdf":
                            active_doc_text = extract_text_from_pdf(file_path)
                        elif ext == ".docx":
                            active_doc_text = extract_text_from_docx(file_path)
                        else:
                            bot_bubble("Unsupported format. Please use .pdf or .docx", "System")
                            continue
                    except Exception as e:
                        bot_bubble(f"Error reading file: {e}", "System")
                        continue

                if active_doc_text and active_doc_text.strip():
                    active_doc_name = os.path.basename(file_path)
                    console.print()
                    doc_status_panel(active_doc_name)
                else:
                    bot_bubble("Could not extract text from the file.", "System")
                    active_doc_text = None
                continue

            # ── Echo user message ──
            user_bubble(user_query)

            # ── Doc Q&A mode ──
            if active_doc_text:
                prompt = (
                    f"Based on the following document context, please answer the question.\n\n"
                    f"Document Context ({active_doc_name}):\n{active_doc_text}\n\n"
                    f"Question: {user_query}\n\nAnswer:"
                )
                with thinking_spinner("Reading document & generating answer…"):
                    response = ask_llm(prompt)
                bot_bubble(response, "Doc Q&A")

            # ── Normal mode ──
            else:
                with thinking_spinner():
                    response, source = chatbot_response(user_query)
                bot_bubble(response, source)

        except (KeyboardInterrupt, EOFError):
            console.print()
            print_rule("Session Interrupted")
            break
