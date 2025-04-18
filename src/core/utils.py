import re
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple, Union

import pandas as pd
from loguru import logger


def parse_chat_line(line: str) -> Optional[Tuple[datetime, str, str]]:
    """Parse a single line from a WhatsApp chat export.

    Args:
        line: A line from the chat export

    Returns:
        Tuple of (datetime, sender, message) if successful, None otherwise
    """
    patterns = [
        r"\[(.*?)\] (.*?): (.*)",  # Default pattern
        r"\[(.*?)\] ~\u202f(.*?): (.*)",  # Pattern with ~ and non-breaking space
        r"(\d{2}/\d{2}/\d{4}, \d{2}:\d{2}) - (.*)",  # Pattern for system messages
    ]

    for pattern in patterns:
        match = re.match(pattern, line)
        if match:
            if len(match.groups()) == 3:
                date_time_str, sender, message = match.groups()
            elif len(match.groups()) == 2:
                date_time_str, message = match.groups()
                sender = "System"
            try:
                date_time = datetime.strptime(date_time_str, "%Y-%m-%d, %H:%M:%S")
            except ValueError:
                try:
                    date_time = datetime.strptime(date_time_str, "%d/%m/%y, %I:%M:%S\u202f%p")
                except ValueError:
                    try:
                        date_time = datetime.strptime(date_time_str, "%d/%m/%Y, %H:%M")
                    except ValueError:
                        continue
            return date_time, sender.strip(), message.strip()
    return None


def parse_chat(file_path: Union[str, Path]) -> pd.DataFrame:
    """Parse a WhatsApp chat log into a DataFrame.

    Args:
        file_path: Path to the chat log file

    Returns:
        DataFrame containing the parsed chat with columns 'Sender', 'Datetime', 'Message'
    """
    parsed_data = []
    with open(file_path, "r") as file:
        for _, line in enumerate(file):
            parsed_line = parse_chat_line(line)
            if parsed_line:
                parsed_data.append(parsed_line)

    # Creating a DataFrame
    df = pd.DataFrame(parsed_data, columns=["Datetime", "Sender", "Message"])
    return df


def cleanup(df: pd.DataFrame) -> pd.DataFrame:
    """Clean up the DataFrame by removing system messages and duplicates.

    Args:
        df: DataFrame containing message data

    Returns:
        Cleaned DataFrame
    """
    df = df.drop_duplicates(subset=["Datetime", "Sender", "Message"])
    df = df.sort_values(by="Datetime")

    # Remove system messages
    system_messages = [
        "deleted this message",
        "message was deleted",
        "changed the subject to",
        "changed the group description",
        "reset this group's invite link",
        "changed this group's icon",
        "changed the subject from",
        "changed this group's settings",
    ]

    for message in system_messages:
        df = df[~df["Message"].str.contains(message)]

    logger.info(f"Cleaned DataFrame has {len(df)} messages")
    return df


def chat_to_df(
    file_path: Path,
    previous_df_path: Optional[Path] = None,
    group_name: Optional[str] = None,
) -> pd.DataFrame:
    """Convert a WhatsApp chat export to a DataFrame.

    Args:
        file_path: Path to the chat export file
        previous_df_path: Optional path to a previous DataFrame to merge with
        group_name: Optional name of the group to add as a column

    Returns:
        DataFrame containing the chat data
    """
    file_path = Path(file_path)
    assert file_path.exists(), f"File not found: {file_path}"

    df = parse_chat(file_path=file_path)
    df = cleanup(df)

    if previous_df_path:
        previous_df = pd.read_csv(previous_df_path, sep="|")
        previous_df["Datetime"] = pd.to_datetime(previous_df["Datetime"])
        df = pd.concat([df, previous_df], ignore_index=True)
        df = cleanup(df)

    if group_name:
        logger.info(f"Adding group name {group_name} to the chat")
        df["Group"] = group_name
    return df 