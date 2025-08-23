# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Blackcat Informatics® Inc.

"""DevSummary AI: AI-Driven Git Repository Analysis and Narrative Generation.

This script analyzes a Git repository over a specified timeframe, uses a tiered
set of Google Gemini models to summarize the development activity, and generates
two key artifacts:
1. A narrative summary in NEWS.md for stakeholders.
2. A structured list of changes in CHANGELOG.txt, following the
   "Keep a Changelog" standard.
"""

import asyncio
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from pathlib import Path
import tomllib
from typing import Final

from git import GitCommandError
from git import NoSuchPathError
from git import Repo
from google import genai
from rich.console import Console
import typer

from git_ai_reporter.analysis.git_analyzer import GitAnalyzer
from git_ai_reporter.analysis.git_analyzer import GitAnalyzerConfig
from git_ai_reporter.cache import CacheManager
from git_ai_reporter.config import Settings
from git_ai_reporter.orchestration import AnalysisOrchestrator
from git_ai_reporter.services.gemini import GeminiClient
from git_ai_reporter.services.gemini import GeminiClientConfig
from git_ai_reporter.services.gemini import GeminiClientError
from git_ai_reporter.writing.artifact_writer import ArtifactWriter

CONSOLE: Final = Console()

# Constants for history generation detection
MIN_NEWS_CONTENT_LENGTH: Final = 100
MIN_NEWS_LINE_COUNT: Final = 5
APP: Final = typer.Typer()


# --- Helper Functions for CLI Setup ---
def _setup(
    repo_path: str, settings: Settings, cache_dir: str, no_cache: bool, debug: bool
) -> tuple[AnalysisOrchestrator, Repo]:
    """Initializes and returns the main AnalysisOrchestrator and Repo object.

    This function acts as the composition root, creating and wiring together all
    the necessary service objects for the application.

    Args:
        repo_path: The path to the Git repository.
        settings: The application settings object.
        cache_dir: The directory to store cache files.
        no_cache: A flag to bypass caching.
        debug: A flag to enable debug mode.

    Returns:
        A tuple containing an initialized AnalysisOrchestrator instance and the Repo object.

    Raises:
        typer.Exit: If initialization fails due to a missing API key or invalid repo path.
    """
    try:
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not set in environment or .env file.")

        gemini_config = GeminiClientConfig(
            model_tier1=settings.MODEL_TIER_1,
            model_tier2=settings.MODEL_TIER_2,
            model_tier3=settings.MODEL_TIER_3,
            input_token_limit_tier1=settings.GEMINI_INPUT_TOKEN_LIMIT_TIER1,
            input_token_limit_tier2=settings.GEMINI_INPUT_TOKEN_LIMIT_TIER2,
            input_token_limit_tier3=settings.GEMINI_INPUT_TOKEN_LIMIT_TIER3,
            max_tokens_tier1=settings.MAX_TOKENS_TIER_1,
            max_tokens_tier2=settings.MAX_TOKENS_TIER_2,
            max_tokens_tier3=settings.MAX_TOKENS_TIER_3,
            temperature=settings.TEMPERATURE,
            api_timeout=settings.GEMINI_API_TIMEOUT,
            debug=debug,
        )
        gemini_client = GeminiClient(genai.Client(api_key=settings.GEMINI_API_KEY), gemini_config)
        try:
            repo = Repo(repo_path, search_parent_directories=True)
        except (GitCommandError, NoSuchPathError) as e:
            raise FileNotFoundError(f"Not a valid git repository: {repo_path}") from e

        repo_path_obj = Path(repo.working_dir)
        cache_path = repo_path_obj / cache_dir
        cache_manager = CacheManager(cache_path)

        git_analyzer = GitAnalyzer(
            repo,
            GitAnalyzerConfig(
                trivial_commit_types=settings.TRIVIAL_COMMIT_TYPES,
                trivial_file_patterns=settings.TRIVIAL_FILE_PATTERNS,
                git_command_timeout=settings.GIT_COMMAND_TIMEOUT,
                debug=debug,
            ),
        )
        artifact_writer = ArtifactWriter(
            news_file=str(repo_path_obj / settings.NEWS_FILE),
            changelog_file=str(repo_path_obj / settings.CHANGELOG_FILE),
            daily_updates_file=str(repo_path_obj / settings.DAILY_UPDATES_FILE),
            console=CONSOLE,
        )
        return (
            AnalysisOrchestrator(
                git_analyzer=git_analyzer,
                gemini_client=gemini_client,
                cache_manager=cache_manager,
                artifact_writer=artifact_writer,
                console=CONSOLE,
                no_cache=no_cache,
                max_concurrent_tasks=settings.MAX_CONCURRENT_GIT_COMMANDS,
                debug=debug,
            ),
            repo,
        )
    except (ValueError, FileNotFoundError) as e:
        CONSOLE.print(str(e), style="bold red")
        raise typer.Exit(code=1) from e


def _load_settings(config_file: str | None) -> Settings:
    """Loads settings from a TOML file, falling back to defaults."""
    if not config_file:
        return Settings()

    config_path = Path(config_file)
    if not config_path.is_file():
        CONSOLE.print(f"Config file not found: {config_file}", style="bold red")
        raise typer.Exit(code=1)
    with config_path.open("rb") as f:
        toml_config = tomllib.load(f)
    return Settings(**toml_config)


def _determine_date_range(
    weeks: int, start_date_str: str | None, end_date_str: str | None
) -> tuple[datetime, datetime]:
    """Determines the start and end date for the analysis."""
    end_date = (
        datetime.strptime(end_date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        if end_date_str
        else datetime.now(timezone.utc)
    )
    start_date = (
        datetime.strptime(start_date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        if start_date_str
        else end_date - timedelta(weeks=weeks)
    )
    return start_date, end_date


def _should_generate_full_history(repo_path: str, settings: Settings) -> bool:
    """Determines if we should generate the full repository history.

    Returns True if NEWS.md doesn't exist or is empty/trivial.

    Args:
        repo_path: Path to the repository.
        settings: Application settings.

    Returns:
        True if full history should be generated.
    """
    news_file = Path(repo_path) / settings.NEWS_FILE

    # If file doesn't exist, generate full history
    if not news_file.exists():
        return True

    # If file is empty or very small (just header), generate full history
    try:
        content = news_file.read_text(encoding="utf-8").strip()
        # Consider it empty if it's just the header or very minimal content
        if len(content) < MIN_NEWS_CONTENT_LENGTH or content.count("\n") < MIN_NEWS_LINE_COUNT:
            return True
    except (OSError, UnicodeDecodeError):
        # If we can't read it, regenerate to be safe
        return True

    return False


def _get_full_repo_date_range(git_analyzer: GitAnalyzer) -> tuple[datetime, datetime]:
    """Gets the full date range for the repository from first commit to now.

    Args:
        git_analyzer: The git analyzer instance.

    Returns:
        Tuple of (start_date, end_date) covering the full repository history.
    """
    end_date = datetime.now(timezone.utc)

    # Get the first commit date
    if first_commit_date := git_analyzer.get_first_commit_date():
        # Start from the beginning of the week containing the first commit
        start_date = first_commit_date.replace(tzinfo=timezone.utc)
        # Round down to start of week (Monday)
        days_since_monday = start_date.weekday()
        start_date = start_date - timedelta(days=days_since_monday)
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        # Fallback to 1 year if we can't determine first commit
        start_date = end_date - timedelta(weeks=52)

    return start_date, end_date


# --- Main Application Logic ---
@APP.command()
def main(  # pylint: disable=too-many-arguments, too-many-positional-arguments
    repo_path: str = typer.Option(".", "--repo-path", help="Path to the Git repository."),
    weeks: int = typer.Option(4, "--weeks", help="Number of past weeks to analyze."),
    start_date_str: str | None = typer.Option(
        None, "--start-date", help="Start date in YYYY-MM-DD format. Overrides --weeks."
    ),
    end_date_str: str | None = typer.Option(
        None, "--end-date", help="End date in YYYY-MM-DD format. Defaults to now."
    ),
    config_file: str | None = typer.Option(
        None, "--config-file", help="Path to a TOML configuration file."
    ),
    cache_dir: str = typer.Option(
        ".git-report-cache", "--cache-dir", help="Path to the cache directory."
    ),
    no_cache: bool = typer.Option(
        False, "--no-cache", help="Ignore existing cache and re-analyze everything."
    ),
    debug: bool = typer.Option(
        False,
        "--debug",
        help="Enable debug mode with verbose logging and no progress bars.",
    ),
) -> None:
    """Generates AI-powered development summaries for a Git repository.

    This command analyzes a Git repository over a specified timeframe, uses Google's
    Gemini models to understand the changes, and then generates two key artifacts:
    a narrative summary in NEWS.md and a structured changelog in CHANGELOG.txt.

    Args:
        repo_path: The file path to the local Git repository.
        weeks: The number of past weeks to analyze. This is overridden by
               --start-date.
        start_date_str: The start date for the analysis range (YYYY-MM-DD).
        end_date_str: The end date for the analysis range (YYYY-MM-DD).
        config_file: Optional path to a TOML configuration file to override
                     default and environment variable settings.
        cache_dir: The directory to store cache files.
        no_cache: If True, ignore existing cache and re-analyze.
        debug: If True, enable verbose logging and disable progress bars.
    """
    settings = _load_settings(config_file)
    orchestrator, repo = _setup(repo_path, settings, cache_dir, no_cache, debug)
    try:
        # Check if we should generate full history (when NEWS.md is missing/empty)
        if not start_date_str and _should_generate_full_history(repo_path, settings):
            CONSOLE.print(
                "NEWS.md not found or empty - generating full repository history", style="yellow"
            )
            start_date, end_date = _get_full_repo_date_range(orchestrator.git_analyzer)
            CONSOLE.print(
                f"Analyzing full repository history from {start_date.date()} to {end_date.date()}"
            )
        else:
            start_date, end_date = _determine_date_range(weeks, start_date_str, end_date_str)

        asyncio.run(orchestrator.run(start_date, end_date))
    except GeminiClientError as e:
        CONSOLE.print(f"\n[bold red]A fatal error occurred during analysis:[/bold red]\n{e}")
        raise typer.Exit(code=1) from e
    finally:
        # Ensure the repo object is closed to release all resources and child processes.
        repo.close()


if __name__ == "__main__":
    APP()
