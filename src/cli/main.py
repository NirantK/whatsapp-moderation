import sys
from pathlib import Path
from typing import Optional

import click
import pandas as pd
from loguru import logger

from src.core.analysis import WhatsAppGroupAnalysis
from src.core.utils import chat_to_df


@click.group()
def cli():
    """WhatsApp group chat analysis tool."""
    pass


@cli.command()
@click.argument("input_path", type=click.Path(exists=True, path_type=Path))
@click.option("--output", "-o", type=click.Path(path_type=Path), help="Output file path")
@click.option("--window-days", "-w", default=60, help="Window in days to consider for inactivity")
@click.option(
    "--exclude-contacts/--include-contacts",
    default=False,
    help="Exclude contacts (users with ~)",
)
def analyze_single(input_path: Path, output: Optional[Path], window_days: int, exclude_contacts: bool):
    """Analyze a single WhatsApp chat export."""
    logger.info(f"Analyzing single chat: {input_path}")
    df = chat_to_df(input_path)
    analysis = WhatsAppGroupAnalysis(df)
    inactive_users = analysis.get_inactive_users(exclude_contacts=exclude_contacts)
    message_counts = analysis.get_message_count_in_window(window_days=window_days)
    result = pd.merge(inactive_users, message_counts, on="User", how="left")
    if output:
        result.to_csv(output, sep="|", index=False)
        logger.info(f"Results saved to {output}")
    else:
        print(result.to_string())


@cli.command()
@click.argument(
    "input_dir",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
)
@click.option("--output", "-o", type=click.Path(path_type=Path), help="Output file path")
@click.option("--window-days", "-w", default=60, help="Window in days to consider for inactivity")
@click.option(
    "--exclude-contacts/--include-contacts",
    default=False,
    help="Exclude contacts (users with ~)",
)
def analyze_multiple(input_dir: Path, output: Optional[Path], window_days: int, exclude_contacts: bool):
    """Analyze multiple WhatsApp chat exports in a directory."""
    logger.info(f"Analyzing multiple chats in directory: {input_dir}")
    all_results = []
    for file_path in input_dir.glob("*.txt"):
        logger.info(f"Processing {file_path}")
        df = chat_to_df(file_path, group_name=file_path.stem)
        analysis = WhatsAppGroupAnalysis(df)
        inactive_users = analysis.get_inactive_users(exclude_contacts=exclude_contacts)
        message_counts = analysis.get_message_count_in_window(window_days=window_days)
        result = pd.merge(inactive_users, message_counts, on="User", how="left")
        all_results.append(result)
    combined_results = pd.concat(all_results, ignore_index=True)
    if output:
        combined_results.to_csv(output, sep="|", index=False)
        logger.info(f"Results saved to {output}")
    else:
        print(combined_results.to_string())


@cli.command()
@click.argument("input_path", type=click.Path(exists=True, path_type=Path))
@click.option("--output", "-o", type=click.Path(path_type=Path), help="Output file path")
@click.option("--window-days", "-w", default=60, help="Window in days to consider for inactivity")
@click.option(
    "--exclude-contacts/--include-contacts",
    default=False,
    help="Exclude contacts (users with ~)",
)
@click.option("--decay-days", "-d", default=90, help="Number of days for score to decay to zero")
@click.option(
    "--reference-messages",
    "-r",
    default=5,
    help="Number of messages that would give a score of 1.0",
)
def score_inactive(
    input_path: Path,
    output: Optional[Path],
    window_days: int,
    exclude_contacts: bool,
    decay_days: int,
    reference_messages: int,
):
    """Calculate activity scores for inactive users."""
    logger.info(f"Calculating activity scores for {input_path}")
    df = chat_to_df(input_path)
    analysis = WhatsAppGroupAnalysis(df)
    inactive_users = analysis.get_inactive_users(exclude_contacts=exclude_contacts)
    scored_users = analysis.calculate_activity_score(
        inactive_users,
        decay_days=decay_days,
        reference_messages=reference_messages,
    )
    if output:
        scored_users.to_csv(output, sep="|", index=False)
        logger.info(f"Results saved to {output}")
    else:
        print(scored_users.to_string())


if __name__ == "__main__":
    cli() 