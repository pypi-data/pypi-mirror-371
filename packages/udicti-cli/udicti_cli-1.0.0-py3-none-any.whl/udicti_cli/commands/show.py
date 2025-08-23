# File: packages/cli/udicti_cli/commands/show.py

"""
This module defines the `show` command, which fetches and displays a
list of all registered developers from the shared database.
"""
import typer
from rich.console import Console
from rich.table import Table

# Import the firebase utility module to interact with Firestore
from udicti_cli.commands import firebase

# Initialize a rich console object for printing
console = Console()

# Create a Typer application for the show command
show_app = typer.Typer()


@show_app.command("devs")
def show_developers():
    """
    Fetches and displays a table of all developers registered in the community.
    Includes their name, email, GitHub username, interests, and skills.
    """
    console.print("[bold cyan]Fetching UDICTI developers from the cloud...[/bold cyan]")
    try:
        # Retrieve the list of developers from Firestore via the firebase utility
        developers = firebase.get_developers()

        if not developers:
            console.print(
                "[dim]No developers registered yet. Use `udicti join` to be the first![/dim]"
            )
            return

        # Create a Rich Table to display the developer data
        table = Table(
            title="[bold white]Current UDICTI Devs[/bold white]",
            show_header=True,
            header_style="bold magenta",
            show_lines=True,  # Adds lines to visually separate rows and columns
        )
        # Define the columns for the table
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Email", style="dim", no_wrap=True)
        table.add_column("GitHub", style="bold yellow", no_wrap=True)
        table.add_column(
            "Skills", style="italic green", no_wrap=False
        )  # Skills might be long, so no_wrap=False
        table.add_column(
            "Interests", style="italic blue", no_wrap=False
        )  # Interests might be long, so no_wrap=False

        # Populate the table with data from the fetched developers
        for dev in developers:
            # Format lists of interests and skills into comma-separated strings for display
            interests_display = (
                ", ".join(dev.get("interests", [])) if dev.get("interests") else "N/A"
            )
            skills_display = (
                ", ".join(dev.get("skills", [])) if dev.get("skills") else "N/A"
            )

            table.add_row(
                dev.get("name", "N/A"),  # Use .get() for safety against missing keys
                dev.get("email", "N/A"),
                dev.get("github", "N/A"),
                skills_display,
                interests_display,
            )

        # Print the fully constructed table to the console
        console.print(table)
    except Exception as e:
        # Catch and report any errors that occur during the process
        console.print(
            f"[bold red]An error occurred while fetching the list: {e}[/bold red]"
        )
