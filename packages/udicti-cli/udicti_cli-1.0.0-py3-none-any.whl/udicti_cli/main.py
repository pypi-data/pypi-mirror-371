# File: packages/cli/udicti_cli/main.py

"""
This is the main entry point for the udicti cli application.
It serves as the central router, importing all command modules and
making them accessible to the user via the `typer` framework.
"""
import typer
from rich.console import Console
import os
import json

# Import all command modules
from udicti_cli.commands import welcome
from udicti_cli.commands import onboarding
from udicti_cli.commands import show
from udicti_cli.commands import github_auth
from udicti_cli.commands import dashboard
from udicti_cli.commands import firebase


console = Console()


# Create the main Typer application object
app = typer.Typer(
    help="UDICTI CLI a modern and simple developers analytics and workflow tool to be used by devs, odds are this tool will be used to simplfy workflows and faster speed for your projects"
)


firebase_config_json = os.environ.get("FIREBASE_CONFIG_JSON")
if not firebase_config_json:
    console.print(
        "[bold red]FIREBASE_CONFIG_JSON environment variable not set.[/bold red]"
    )
    raise typer.Exit(1)

try:
    FIREBASE_CONFIG = json.loads(firebase_config_json)
except json.JSONDecodeError:
    console.print(
        "[bold red]Invalid JSON in FIREBASE_CONFIG_JSON environment variable.[/bold red]"
    )
    raise typer.Exit(1)


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """
    The main callback for the CLI. Displays a welcome message and banner if no
    subcommand is specified. It also initializes the Firebase connection,
    which is essential for commands interacting with the database.
    """
    try:
        # Initialize Firebase SDK. This needs to happen once for the application.
        firebase.init_firebase(FIREBASE_CONFIG)
    except Exception as e:
        console.print(f"[bold red]Error initializing Firebase: {e}[/bold red]")
        console.print(
            "[yellow]💡 Tip:[/yellow] Ensure your `FIREBASE_CONFIG_JSON` environment variable is correctly set up."
        )
        raise typer.Exit(
            code=1
        )  # Exit if Firebase cannot be initialized as it's a critical dependency

    # If no subcommand was provided by the user, display the welcome banner.
    if ctx.invoked_subcommand is None:
        welcome.show_welcome()


app.add_typer(welcome.app, name="welcome")
app.add_typer(onboarding.onboarding_app)
app.add_typer(show.show_app, name="show")
app.add_typer(github_auth.github_auth_app, name="github-auth")
app.add_typer(dashboard.dashboard_app, name="dashboard")

# This block ensures that the Typer application runs when the script is executed directly.
if __name__ == "__main__":
    app()
