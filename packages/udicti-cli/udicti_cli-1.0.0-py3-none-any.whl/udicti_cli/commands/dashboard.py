# File: packages/cli/udicti_cli/commands/dashboard.py

"""
This module defines the `dashboard` command, providing insights into
personal GitHub contributions and UDICTI organization activity.
"""
import typer
import httpx
import asyncio
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.columns import Columns
import datetime

# Import utilities - Updated imports
from .github_auth import load_github_token, clear_github_token  # Updated function names
from . import firebase

console = Console()
dashboard_app = typer.Typer()

GITHUB_API_BASE_URL = "https://api.github.com"
UDICTI_ORG_NAME = "udicti"


async def _make_github_api_request(endpoint: str, token: str, params: dict = None):
    """Helper to make authenticated GitHub API requests."""
    headers = {
        "Authorization": f"token {token}",  # OAuth tokens use same format
        "Accept": "application/vnd.github.v3+json",
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{GITHUB_API_BASE_URL}/{endpoint}",
            headers=headers,
            params=params,
            timeout=20,
        )
        response.raise_for_status()
        return response.json()


# File: packages/cli/udicti_cli/commands/dashboard.py


async def _personal_dashboard_async():
    """Async implementation of personal dashboard with accurate data."""
    token = load_github_token()
    if not token:
        console.print(
            Panel(
                "[bold yellow]GitHub Login Required![/bold yellow]\n\n"
                "Please run [bold green]udicti github-auth login[/bold green] to authenticate with GitHub.",
                title="[bold yellow]Action Required[/bold yellow]",
                border_style="yellow",
                padding=(1, 2),
            )
        )
        raise typer.Exit(code=1)

    console.print("[bold cyan]📊 Analyzing your developer activity...[/bold cyan]")

    try:
        # 1. Get authenticated user's profile
        user_data = await _make_github_api_request("user", token)
        username = user_data.get("login")
        public_repos = user_data.get("public_repos", 0)
        followers = user_data.get("followers", 0)
        following = user_data.get("following", 0)

        # 2. Get UDICTI profile info
        udicti_name = username
        udicti_interests = []
        udicti_skills = []

        try:
            from ..main import FIREBASE_CONFIG

            firebase.init_firebase(FIREBASE_CONFIG)

            registered_developers = firebase.get_developers()
            for dev in registered_developers:
                if dev.get("github", "").lower() == username.lower():
                    udicti_name = dev.get("name", username)
                    udicti_interests = dev.get("interests", [])
                    udicti_skills = dev.get("skills", [])
                    break
        except Exception as e:
            console.print(f"[dim red]⚠️  Could not fetch UDICTI profile: {e}[/dim red]")

        # 3. Get comprehensive repository data (more accurate than events)
        repos = await _make_github_api_request(
            f"users/{username}/repos",
            token,
            params={"type": "all", "per_page": 100, "sort": "updated"},
        )

        # 4. Get contribution statistics (last year)
        today = datetime.datetime.now(datetime.timezone.utc)
        one_year_ago = today - datetime.timedelta(days=365)

        # Analyze repositories for accurate stats
        total_commits = 0
        languages_used = {}
        recent_activity = []
        active_repos = 0

        for repo in repos:
            repo_updated = datetime.datetime.fromisoformat(
                repo.get("updated_at").replace("Z", "+00:00")
            )

            # Count active repos (updated in last 6 months)
            if repo_updated >= (today - datetime.timedelta(days=180)):
                active_repos += 1

            # Get languages for each repo
            try:
                repo_languages = await _make_github_api_request(
                    f"repos/{username}/{repo['name']}/languages", token
                )
                for lang, bytes_count in repo_languages.items():
                    languages_used[lang] = languages_used.get(lang, 0) + bytes_count
            except Exception:
                pass  # Skip if can't access repo languages

            # Get commit count for recent repos
            if repo_updated >= one_year_ago and not repo.get("fork", False):
                try:
                    commits = await _make_github_api_request(
                        f"repos/{username}/{repo['name']}/commits",
                        token,
                        params={
                            "author": username,
                            "since": one_year_ago.isoformat(),
                            "per_page": 100,
                        },
                    )
                    total_commits += len(commits)

                    # Track recent activity
                    for commit in commits[:5]:  # Last 5 commits from this repo
                        commit_date = datetime.datetime.fromisoformat(
                            commit["commit"]["author"]["date"].replace("Z", "+00:00")
                        )
                        recent_activity.append(
                            {
                                "repo": repo["name"],
                                "message": (
                                    commit["commit"]["message"][:50] + "..."
                                    if len(commit["commit"]["message"]) > 50
                                    else commit["commit"]["message"]
                                ),
                                "date": commit_date,
                            }
                        )
                except Exception:
                    pass  # Skip if can't access commits

        # Sort recent activity by date
        recent_activity.sort(key=lambda x: x["date"], reverse=True)
        recent_activity = recent_activity[:10]  # Keep only last 10 commits

        # 5. Calculate top languages (by bytes of code)
        total_bytes = sum(languages_used.values())
        top_languages = []
        if total_bytes > 0:
            sorted_languages = sorted(
                languages_used.items(), key=lambda x: x[1], reverse=True
            )
            for lang, bytes_count in sorted_languages[:5]:
                percentage = (bytes_count / total_bytes) * 100
                top_languages.append((lang, percentage))

        # 6. Create improved UI with accurate data

        # Profile Overview Panel

        profile_content = Text.from_markup(
            f"[bold green]👋 Hello, [bold white]{udicti_name}[/bold white]![/bold green]\n\n"
            f"[dim]GitHub:[/dim] [bold cyan]@{username}[/bold cyan] [dim] [/dim]\n"
            f"[dim]Repositories:[/dim] [bold white]{public_repos}[/bold white] public • [bold white]{active_repos}[/bold white] recently active\n"
            f"[dim]Network:[/dim] [bold white]{followers}[/bold white] followers • [bold white]{following}[/bold white] following\n\n"
            f"[dim]UDICTI Interests:[/dim] [italic blue]{', '.join(udicti_interests) if udicti_interests else 'Not specified'}[/italic blue]\n"
            f"[dim]Skills:[/dim] [italic green]{', '.join(udicti_skills) if udicti_skills else 'Not specified'}[/italic green]"
        )

        profile_panel = Panel(
            profile_content,
            title="[bold white]📊 Developer Profile[/bold white]",
            border_style="blue",
            padding=(1, 2),
        )

        # Activity Stats Panel
        activity_content = Text.from_markup(
            f"[bold magenta]📈 Activity Overview (Last Year):[/bold magenta]\n\n"
            f"[dim]Total Commits:[/dim] [bold white]{total_commits}[/bold white]\n"
            f"[dim]Active Repositories:[/dim] [bold white]{active_repos}[/bold white]\n"
            f"[dim]Languages Used:[/dim] [bold white]{len(languages_used)}[/bold white]\n"
            f"[dim]Avg Commits/Month:[/dim] [bold white]{total_commits // 12}[/bold white]"
        )

        activity_panel = Panel(
            activity_content,
            title="[bold white]📊 Activity Stats[/bold white]",
            border_style="green",
            padding=(1, 2),
        )

        # Language Distribution Panel
        if top_languages:
            lang_lines = ["[bold yellow]🔥 Top Programming Languages:[/bold yellow]\n"]
            max_bar_length = 25

            for lang, percentage in top_languages:
                bar_length = int((percentage / 100) * max_bar_length)
                bar = "█" * bar_length
                lang_lines.append(
                    f"[dim]{lang:12}[/dim] [cyan]{bar}[/cyan] [bold white]{percentage:.1f}%[/bold white]"
                )

            languages_content = Text.from_markup("\n".join(lang_lines))
        else:
            languages_content = Text.from_markup(
                "[dim]No language data available[/dim]"
            )

        languages_panel = Panel(
            languages_content,
            title="[bold white]💻 Language Usage[/bold white]",
            border_style="yellow",
            padding=(1, 2),
        )

        # Recent Activity Panel
        if recent_activity:
            activity_lines = ["[bold cyan]⚡ Recent Commits:[/bold cyan]\n"]
            for activity in recent_activity[:8]:
                days_ago = (today - activity["date"]).days
                time_str = f"{days_ago}d ago" if days_ago > 0 else "today"
                activity_lines.append(
                    f"[dim]{activity['repo']}[/dim] • {activity['message']} [dim]({time_str})[/dim]"
                )

            recent_content = Text.from_markup("\n".join(activity_lines))
        else:
            recent_content = Text.from_markup("[dim]No recent activity found[/dim]")

        recent_panel = Panel(
            recent_content,
            title="[bold white]🚀 Recent Work[/bold white]",
            border_style="cyan",
            padding=(1, 2),
        )

        # Display all panels
        console.print(profile_panel)

        # Two column layout for stats
        columns = Columns([activity_panel, languages_panel], expand=True)
        console.print(columns)

        console.print(recent_panel)

        # Add some actionable insights
        insights = []
        if total_commits < 50:
            insights.append(
                "💡 Try to commit more regularly - aim for small, frequent commits!"
            )
        if len(languages_used) < 3:
            insights.append(
                "🌟 Consider exploring new programming languages to broaden your skills!"
            )
        if active_repos < 3:
            insights.append("🚀 Start more projects or contribute to existing ones!")

        if insights:
            insights_content = Text.from_markup("\n".join(insights))
            insights_panel = Panel(
                insights_content,
                title="[bold white]💭 Growth Suggestions[/bold white]",
                border_style="magenta",
                padding=(1, 2),
            )
            console.print(insights_panel)

    except httpx.HTTPStatusError as e:
        console.print(
            f"[bold red]❌ Error accessing GitHub API: {e.response.status_code}[/bold red]"
        )
        console.print(
            "[yellow]💡 Tip:[/yellow] Your token might be invalid. Try [bold green]udicti github-auth login[/bold green] again."
        )
        clear_github_token()
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[bold red]❌ An unexpected error occurred: {e}[/bold red]")
        raise typer.Exit(code=1)


@dashboard_app.command("me")
def personal_dashboard():
    """
    Displays your personal GitHub contribution dashboard.
    Requires GitHub authentication via `udicti github-auth login`.
    """
    asyncio.run(_personal_dashboard_async())
