# File: packages/cli/udicti_cli/commands/welcome.py

"""
Welcome module for displaying the UDICTI CLI banner and introduction.
"""

import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich_gradient import Gradient

# Create the welcome command app
app = typer.Typer(help="Display welcome messages and CLI information.")
console = Console()

# Different banner sizes for different terminal widths
UDICTI_BANNER_FULL = """
  ░██     ░██     ░██ ░███████   ░██████  ░██████  ░██████████ ░██████
    ░██   ░██     ░██ ░██   ░██    ░██   ░██   ░██     ░██       ░██  
     ░██  ░██     ░██ ░██    ░██   ░██  ░██            ░██       ░██  
    ░██   ░██     ░██ ░██    ░██   ░██  ░██            ░██       ░██  
   ░██    ░██     ░██ ░██    ░██   ░██  ░██            ░██       ░██  
  ░██     ░██     ░██ ░██   ░██    ░██   ░██   ░██     ░██       ░██  
           ░██████    ░███████   ░██████  ░██████      ░██     ░██████
"""

UDICTI_BANNER_MEDIUM = """
 ██╗   ██╗██████╗ ██╗ ██████╗████████╗██╗
 ██║   ██║██╔══██╗██║██╔════╝╚══██╔══╝██║
 ██║   ██║██║  ██║██║██║        ██║   ██║
 ██║   ██║██║  ██║██║██║        ██║   ██║
 ╚██████╔╝██████╔╝██║╚██████╗   ██║   ██║
  ╚═════╝ ╚═════╝ ╚═╝ ╚═════╝   ╚═╝   ╚═╝
"""

UDICTI_BANNER_SMALL = """
 █╗ █╗██████╗ ██╗ ██████╗████████╗██╗
 ██╗██║██╔══██╗██║██╔════╝╚══██╔══╝██║
 ██║██║██║  ██║██║██║        ██║   ██║
 ██║██║██████╔╝██║╚██████╗   ██║   ██║
 ╚═╝╚═╝╚═════╝ ╚═╝ ╚═════╝   ╚═╝   ╚═╝
"""

UDICTI_BANNER_TINY = """
╔═══════════════╗
║   U D I C T I ║
╚═══════════════╝
"""


def get_responsive_banner():
    """Return appropriate banner based on terminal width"""
    terminal_width = console.size.width

    if terminal_width >= 80:
        return UDICTI_BANNER_FULL
    elif terminal_width >= 60:
        return UDICTI_BANNER_MEDIUM
    elif terminal_width >= 40:
        return UDICTI_BANNER_SMALL
    else:
        return UDICTI_BANNER_TINY


@app.command("")
def show_welcome():
    """
    Display the UDICTI CLI welcome banner and getting started information.
    """
    # Get responsive banner
    banner = get_responsive_banner()

    gradient_banner = Gradient(
        banner,
        rainbow=False,
        colors=[
            "#87ceeb",
            "#0864af",
            "#1264a7",
            "#043463",
        ],  # Light blue → UDICTI Blue → Dark blue
    )

    main_message = Text.from_markup(
        "\n[bold green]Welcome to the UDICTI Developer CLI![/bold green]\n"
        "Your Developer Analytics & Workflow Toolkit for UDICTI\n\n"
        "🚀 [bold cyan]Quick Start Commands:[/bold cyan]\n"
        "• [#0864af]udicti github-auth login[/#0864af] - Authenticate with GitHub\n"
        "• [#0864af]udicti join[/#0864af] - Join the UDICTI developer community\n"
        "• [#0864af]udicti show devs[/#0864af] - View registered developers\n"
        "• [#0864af]udicti --help[/#0864af] - See all available commands\n\n"
        "[#f6b418]💡 Tip:[/#f6b418] Start with GitHub authentication if you're new!\n"
    )

    console.print(gradient_banner)
    console.print(main_message)


@app.callback(invoke_without_command=True)
def welcome_callback(ctx: typer.Context):
    """
    Default callback that shows welcome when just 'udicti welcome' is called.
    """
    if ctx.invoked_subcommand is None:
        show_welcome()
