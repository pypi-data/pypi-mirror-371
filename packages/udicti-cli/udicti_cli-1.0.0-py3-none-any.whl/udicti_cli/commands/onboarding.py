# File: packages/cli/udicti_cli/commands/onboarding.py

"""
This module defines the commands for new user onboarding, such as the `join` command.
It handles user input, GitHub authentication, and registration with Firebase.
"""
import typer
import requests
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.text import Text

# Import Firebase and GitHub auth utilities
from . import firebase
from .github_auth import load_github_pat

# Initialize a rich console object for printing
console = Console()

# Create a Typer application for the onboarding commands
onboarding_app = typer.Typer()


def get_github_user_info(pat: str) -> dict:
    """
    Fetches user information from GitHub using the Personal Access Token.

    Returns:
        dict: GitHub user info including name, email, and username
    """
    headers = {
        "Authorization": f"token {pat}",
        "Accept": "application/vnd.github.v3+json",
    }

    try:
        # Get user profile
        user_response = requests.get("https://api.github.com/user", headers=headers)
        user_response.raise_for_status()
        user_data = user_response.json()

        # Get user emails
        emails_response = requests.get(
            "https://api.github.com/user/emails", headers=headers
        )
        emails_response.raise_for_status()
        emails_data = emails_response.json()

        # Find primary email
        primary_email = next(
            (email["email"] for email in emails_data if email["primary"]), None
        )

        return {
            "name": user_data.get("name") or user_data.get("login"),
            "email": primary_email,
            "github": user_data.get("login"),
            "avatar_url": user_data.get("avatar_url"),
        }
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]Error fetching GitHub info: {e}[/bold red]")
        return None


@onboarding_app.command("join")
def join_community():
    """
    Joins the UDICTI community using GitHub authentication and Firebase registration.
    """
    console.print(
        "[bold dodger_blue3]🚀 Welcome to the UDICTI Dev Team! Let's get you signed up.[/bold dodger_blue3]"
    )

    # Step 1: Check for GitHub PAT
    pat = load_github_pat()
    if not pat:
        console.print(
            Panel(
                "[bold yellow]⚠️  GitHub authentication required![/bold yellow]\n\n"
                "Oops!, Before joining, you need to authenticate with GitHub.\n"
                "Please run: [bold green]udicti github-auth login[/bold green]\n"
                "Then come back and run: [bold green]udicti join[/bold green]",
                title="[bold white]Authentication Required[/bold white]",
                border_style="yellow",
                padding=(1, 2),
            )
        )
        raise typer.Exit(1)

    # Step 2: Fetch GitHub user info
    console.print("[dim]🔍 Fetching your GitHub profile...[/dim]")
    github_info = get_github_user_info(pat)

    if not github_info:
        console.print(
            "[bold red] Failed to fetch GitHub profile. Please check your PAT.[/bold red]"
        )
        raise typer.Exit(1)

    # Step 3: Confirm GitHub info and get additional details
    console.print(
        Panel(
            f"[bold #0864af] GitHub profile found![/bold #0864af]\n\n"
            f"Name: [dodger_blue3]{github_info['name']}[/dodger_blue3]\n"
            f"Email: [dodger_blue3]{github_info['email']}[/dodger_blue3]\n"
            f"GitHub: [dodger_blue3]{github_info['github']}[/dodger_blue3]",
            title="[bold white]Your GitHub Profile[/bold white]",
            border_style="#f6b418",
            padding=(1, 2),
        )
    )

    # Allow user to override if needed
    if not Confirm.ask("Is this information correct?", default=True):
        github_info["name"] = Prompt.ask(
            "Enter your full name", default=github_info["name"]
        )
        github_info["email"] = Prompt.ask(
            "Enter your UDSM email", default=github_info["email"]
        )
        github_info["github"] = Prompt.ask(
            "Enter your GitHub username", default=github_info["github"]
        )

    # Get additional info
    console.print(
        "\n[bold dodger_blue3] Let's get some additional information:[/bold dodger_blue3]"
    )

    interests_input = Prompt.ask(
        "What are your programming interests? (comma-separated)", default=""
    )
    interests = [
        interest.strip() for interest in interests_input.split(",") if interest.strip()
    ]

    skills_input = Prompt.ask(
        "What programming languages/technologies do you know? (comma-separated)",
        default="",
    )
    skills = [skill.strip() for skill in skills_input.split(",") if skill.strip()]

    # Step 4: Initialize Firebase and save to database
    try:
        console.print("[dim] Saving to UDICTI database...[/dim]")

        # Initialize Firebase (you'll need to import FIREBASE_CONFIG from main.py)
        from ..main import FIREBASE_CONFIG

        firebase.init_firebase(FIREBASE_CONFIG)

        # Add developer to database
        firebase.add_developer(
            name=github_info["name"],
            email=github_info["email"],
            github=github_info["github"],
            interests=interests,
            skills=skills,
        )

        console.print("[bold green] Successfully registered with UDICTI![/bold green]")

    except Exception as e:
        console.print(f"[bold red] Error saving to database: {e}[/bold red]")
        raise typer.Exit(1)

    # Step 5: Show welcome message and existing developers
    welcome_message = f"""
    [bold green]🎉 Welcome to the UDICTI Dev Team, [bold dodger_blue3]{github_info['name']}[/bold dodger_blue3]![/bold green]
    
    Your information has been saved to our developer roster.
    You're now part of the UDICTI community!
    
    Here are your fellow developers:
    """

    console.print(
        Panel(
            Text.from_markup(welcome_message),
            title="[bold white] Welcome to UDICTI[/bold white]",
            border_style="#f6b418",
            padding=(1, 2),
        )
    )

    # Step 6: Display all registered developers from Firebase
    try:
        developers = firebase.get_developers()

        if developers:
            table = Table(
                title="[bold white] UDICTI Developer Roster[/bold white]",
                show_header=True,
                header_style="bold magenta",
            )
            table.add_column("Name", style="dodger_blue3", no_wrap=True)
            table.add_column("GitHub", style="yellow", no_wrap=True)
            table.add_column("Skills", style="dim", max_width=30)

            for dev in developers:
                skills_display = ", ".join(
                    dev.get("skills", [])[:3]
                )  # Show first 3 skills
                if len(dev.get("skills", [])) > 3:
                    skills_display += "..."

                table.add_row(
                    dev["name"],
                    f"@{dev['github']}",
                    skills_display or "No skills listed",
                )

            console.print(table)
        else:
            console.print(
                "[dim]No other developers registered yet. You're the first![/dim]"
            )

    except Exception as e:
        console.print(f"[dim]Could not fetch developer list: {e}[/dim]")

    console.print(
        "\n[bold dodger_blue3]🚀 Ready to start building amazing things with UDICTI![/bold dodger_blue3]"
    )
