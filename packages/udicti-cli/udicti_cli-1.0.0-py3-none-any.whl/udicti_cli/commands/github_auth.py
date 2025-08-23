# File: packages/cli/udicti_cli/commands/github_auth.py

import json
import time
import webbrowser
from pathlib import Path
import os
import stat
import typer
import requests
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

# GitHub OAuth App credentials (you'll need to create a GitHub App)
GITHUB_CLIENT_ID = "Iv23liYBZbvclFcmuOd6"  # Replace with your GitHub App client ID

# Path to store the OAuth token securely
AUTH_DIR = Path(typer.get_app_dir("udicti-cli", roaming=True)) / "auth"
GITHUB_TOKEN_FILE = AUTH_DIR / "github_token.json"


def save_github_token(access_token: str):
    """
    Saves the GitHub OAuth token to a file with restricted permissions.
    """
    AUTH_DIR.mkdir(parents=True, exist_ok=True)
    try:
        with open(GITHUB_TOKEN_FILE, "w") as f:
            json.dump({"access_token": access_token}, f)
        # Set file permissions to owner read/write only
        os.chmod(GITHUB_TOKEN_FILE, stat.S_IRUSR | stat.S_IWUSR)
    except IOError as e:
        console.print(f"[bold red]Error saving GitHub token: {e}[/bold red]")


def load_github_token() -> str | None:
    """
    Loads the GitHub OAuth token from the secure file.
    Returns None if the file doesn't exist or is unreadable.
    """
    if not GITHUB_TOKEN_FILE.exists():
        return None
    try:
        with open(GITHUB_TOKEN_FILE, "r") as f:
            data = json.load(f)
            return data.get("access_token")
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def clear_github_token():
    """
    Deletes the locally stored GitHub token.
    """
    if GITHUB_TOKEN_FILE.exists():
        os.remove(GITHUB_TOKEN_FILE)


def start_device_flow():
    """
    Initiates the GitHub OAuth Device Flow.
    Returns device_code, user_code, verification_uri, and interval.
    """
    response = requests.post(
        "https://github.com/login/device/code",
        data={"client_id": GITHUB_CLIENT_ID, "scope": "read:user user:email"},
        headers={"Accept": "application/json"},
    )

    if response.status_code != 200:
        raise Exception(f"Failed to start device flow: {response.text}")

    return response.json()


def poll_for_token(device_code: str, interval: int):
    """
    Polls GitHub for the access token after user authorization.
    """
    while True:
        response = requests.post(
            "https://github.com/login/oauth/access_token",
            data={
                "client_id": GITHUB_CLIENT_ID,
                "device_code": device_code,
                "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
            },
            headers={"Accept": "application/json"},
        )

        data = response.json()

        if "access_token" in data:
            return data["access_token"]
        elif data.get("error") == "authorization_pending":
            time.sleep(interval)
            continue
        elif data.get("error") == "slow_down":
            interval += 5
            time.sleep(interval)
            continue
        elif data.get("error") in ["expired_token", "access_denied"]:
            raise Exception(f"Authorization {data['error']}")
        else:
            raise Exception(f"Unexpected error: {data}")


github_auth_app = typer.Typer()


@github_auth_app.command("login")
def github_login_command():
    """
    Authenticates with GitHub using OAuth Device Flow.
    """
    console.print("[bold blue3] Starting GitHub authentication...[/bold blue3]")

    try:
        # Step 1: Start device flow
        device_data = start_device_flow()
        device_code = device_data["device_code"]
        user_code = device_data["user_code"]
        verification_uri = device_data["verification_uri"]
        interval = device_data.get("interval", 5)
        expires_in = device_data.get("expires_in", 900)

        # Step 2: Display instructions to user
        auth_panel = Panel(
            f"[bold green]📱 Complete GitHub Authentication[/bold green]\n\n"
            f"1. Your browser will open to: [link]{verification_uri}[/link]\n"
            f"2. Enter this code when prompted: [bold yellow]{user_code}[/bold yellow]\n"
            f"3. Authorize 'UDICTI CLI' to access your GitHub account\n\n"
            f"[dim]Code expires in {expires_in // 60} minutes[/dim]",
            title="[bold white]🔑 GitHub Authentication[/bold white]",
            border_style="#f6b418",
            padding=(1, 2),
        )
        console.print(auth_panel)

        # Step 3: Open browser automatically
        if Confirm.ask("Open browser automatically?", default=True):
            webbrowser.open(verification_uri)

        # Step 4: Poll for token with progress indicator
        console.print("\n[dim]⏳ Waiting for authorization...[/dim]")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True,
        ) as progress:
            task = progress.add_task("Waiting for GitHub authorization...", total=None)

            try:
                access_token = poll_for_token(device_code, interval)
                progress.update(task, description=" Authorization successful!")

                # Step 5: Save token
                save_github_token(access_token)

                console.print(
                    "\n[bold green] GitHub authentication successful![/bold green]"
                )
                console.print("[dim]You can now use GitHub-integrated features.[/dim]")

            except Exception as e:
                progress.stop()
                console.print(f"\n[bold red] Authentication failed: {e}[/bold red]")
                raise typer.Exit(1)

    except Exception as e:
        console.print(f"[bold red] Error during authentication: {e}[/bold red]")
        raise typer.Exit(1)


@github_auth_app.command("logout")
def github_logout_command():
    """
    Clears the locally stored GitHub token.
    """
    clear_github_token()
    console.print("[bold green] Logged out of GitHub.[/bold green]")


@github_auth_app.command("status")
def github_status_command():
    """
    Checks if a GitHub token is configured and validates it.
    """
    token = load_github_token()
    if not token:
        console.print(
            Panel(
                "[bold yellow] No GitHub authentication found.[/bold yellow]\n"
                "[italic dim]Use [bold green]udicti github-auth login[/bold green] to authenticate.[/italic dim]",
                title="[bold white]GitHub Status[/bold white]",
                border_style="yellow",
            )
        )
        return

    # Validate token by making a test API call
    try:
        response = requests.get(
            "https://api.github.com/user",
            headers={
                "Authorization": f"token {token}",
                "Accept": "application/vnd.github.v3+json",
            },
        )

        if response.status_code == 200:
            user_data = response.json()
            console.print(
                Panel(
                    f"[bold green] GitHub authentication active![/bold green]\n\n"
                    f"Authenticated as: [cyan]{user_data.get('name', 'N/A')} (@{user_data.get('login')})[/cyan]\n"
                    f"[dim]Ready to use GitHub-integrated features.[/dim]",
                    title="[bold white]GitHub Status[/bold white]",
                    border_style="green",
                )
            )
        else:
            console.print(
                Panel(
                    "[bold red] GitHub token is invalid or expired.[/bold red]\n"
                    "[italic dim]Use [bold green]udicti github-auth login[/bold green] to re-authenticate.[/italic dim]",
                    title="[bold white]GitHub Status[/bold white]",
                    border_style="red",
                )
            )
            clear_github_token()

    except Exception as e:
        console.print(f"[bold red] Error checking GitHub status: {e}[/bold red]")


# Update the load function name for consistency
def load_github_pat():
    """Alias for backward compatibility"""
    return load_github_token()
