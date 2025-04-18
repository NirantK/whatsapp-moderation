from typing import Tuple

import pandas as pd
from loguru import logger


class WhatsAppGroupAnalysis:
    """Class for analyzing WhatsApp group chat data."""

    def __init__(self, df: pd.DataFrame) -> None:
        """Initialize with a DataFrame containing message data.

        Args:
            df: DataFrame with 'Datetime' and 'Sender' columns
        """
        self.df = df
        # Convert the 'Datetime' column to a datetime object
        self.df["Datetime"] = pd.to_datetime(self.df["Datetime"])
        logger.info(f"Initialized WhatsAppGroupAnalysis with {len(df)} messages")

    def get_current_users(self) -> Tuple[pd.DataFrame, int]:
        """Get the current users in the group.

        Returns:
            Tuple of (DataFrame with current users, count of current users)
        """
        # Identifying patterns for joining, being added, and leaving or being removed
        joining_pattern = self.df["Message"].str.contains("joined using this group|added", case=False, na=False)
        leaving_pattern = self.df["Message"].str.contains("left|removed", case=False, na=False)
        # Extracting users who have joined or been added
        joined_users = self.df[joining_pattern]["Sender"].unique()
        # Extracting users who have left or been removed
        left_users = self.df[leaving_pattern]["Sender"].unique()
        # Finding current users by excluding those who have left or been removed
        current_users = [user for user in joined_users if user not in left_users]
        # Creating a DataFrame with current users
        current_users_df = pd.DataFrame(current_users, columns=["User"])
        current_users_count = len(current_users)
        logger.info(f"Found {current_users_count} current users")
        return current_users_df, current_users_count

    def get_message_count_in_window(self, window_days: int = 60) -> pd.DataFrame:
        """Get the message count for each user in a time window.

        Args:
            window_days: Number of days to look back, defaults to 60

        Returns:
            DataFrame with message counts per user in the window
        """
        # Get the maximum date in the DataFrame
        max_date = self.df["Datetime"].max()
        # Calculate the start date based on the window_days parameter
        start_date = max_date - pd.Timedelta(days=window_days)
        # Filter messages within the given window
        messages_in_window = self.df[self.df["Datetime"] > start_date]
        # Count messages per user
        message_count_in_window = messages_in_window["Sender"].value_counts().reset_index()
        message_count_in_window.columns = ["User", "Message_Count_In_Window"]
        logger.info(f"Message counts calculated for {len(message_count_in_window)} users in {window_days} day window")
        return message_count_in_window

    def get_inactive_users(self, exclude_contacts: bool = False) -> pd.DataFrame:
        """Get users who have been inactive.

        Args:
            exclude_contacts: Whether to exclude contacts (users with names starting with '~'), defaults to False

        Returns:
            DataFrame with inactive users and their statistics
        """
        # Get users with zero messages
        users_with_zero_messages = self.get_users_with_zero_messages()
        # Filter users whose usernames start with a tilde ("~")
        if exclude_contacts:
            inactive_users = users_with_zero_messages[users_with_zero_messages["User"].str.startswith("~")]
        else:
            inactive_users = users_with_zero_messages
        # Get users with joining date
        users_with_joining_date = self.get_users_with_joining_date()
        # Merge inactive users with joining dates
        inactive_users_with_joining_date = pd.merge(inactive_users, users_with_joining_date, on="User", how="left")
        # Get the cutoff date for the last 60 days
        max_date = self.df["Datetime"].max()
        cutoff_date = max_date - pd.Timedelta(days=60)
        # Filter users who joined more than 60 days ago
        filtered_inactive_users = inactive_users_with_joining_date[
            inactive_users_with_joining_date["Joining_Date"] < cutoff_date
        ]
        # Count total messages sent by each user since the beginning
        total_message_count = self.df["Sender"].value_counts().reset_index()
        total_message_count.columns = ["User", "Total_Messages_Sent"]
        # Merge with total messages sent
        filtered_inactive_users_with_messages = pd.merge(
            filtered_inactive_users, total_message_count, on="User", how="left"
        ).fillna(0)
        # Find the most recent message date for each user
        most_recent_message_date = self.df.groupby("Sender")["Datetime"].max().reset_index()
        most_recent_message_date.columns = ["User", "Most_Recent_Message_Date"]
        # Merge with the most recent message date
        filtered_inactive_users_with_messages = pd.merge(
            filtered_inactive_users_with_messages, most_recent_message_date, on="User", how="left"
        )
        # Calculate days since last message
        filtered_inactive_users_with_messages["Days_Since_Last_Message"] = (
            max_date - filtered_inactive_users_with_messages["Most_Recent_Message_Date"]
        ).dt.days
        return filtered_inactive_users_with_messages

    def get_users_with_zero_messages(self) -> pd.DataFrame:
        """Get users who have sent zero messages in the last 60 days.

        Returns:
            DataFrame with users who have sent zero messages
        """
        # Get the maximum date in the DataFrame
        max_date = self.df["Datetime"].max()
        # Calculate the start date for the last 60 days
        start_date = max_date - pd.Timedelta(days=60)
        # Get all users who have sent messages
        users_with_messages = self.df[self.df["Datetime"] > start_date]["Sender"].unique()
        # Get all users who have joined the group
        joining_pattern = self.df["Message"].str.contains("joined using this group|added", case=False, na=False)
        all_users = self.df[joining_pattern]["Sender"].unique()
        # Find users who have not sent any messages
        users_with_zero_messages = [user for user in all_users if user not in users_with_messages]
        # Create a DataFrame with users who have sent zero messages
        users_with_zero_messages_df = pd.DataFrame(users_with_zero_messages, columns=["User"])
        return users_with_zero_messages_df

    def get_users_with_joining_date(self) -> pd.DataFrame:
        """Get the joining date for each user.

        Returns:
            DataFrame with users and their joining dates
        """
        # Identifying patterns for joining or being added
        joining_pattern = self.df["Message"].str.contains("joined using this group|added", case=False, na=False)
        # Get the joining messages
        joining_messages = self.df[joining_pattern]
        # Extract the joining date for each user
        users_with_joining_date = joining_messages[["Datetime", "Sender"]].copy()
        users_with_joining_date.columns = ["Joining_Date", "User"]
        return users_with_joining_date

    def calculate_activity_score(
        self,
        inactive_users_df: pd.DataFrame,
        decay_days: int = 90,
        reference_messages: int = 5,
    ) -> pd.DataFrame:
        """Calculate an activity score for inactive users.

        Args:
            inactive_users_df: DataFrame with inactive users
            decay_days: Number of days for score to decay to zero, defaults to 90
            reference_messages: Number of messages that would give a score of 1.0, defaults to 5

        Returns:
            DataFrame with activity scores for inactive users
        """
        # Calculate base score (normalized by reference_messages)
        inactive_users_df["Base_Score"] = inactive_users_df["Total_Messages_Sent"] / reference_messages
        # Calculate decay factor
        inactive_users_df["Decay_Factor"] = inactive_users_df["Days_Since_Last_Message"] / decay_days
        # Calculate activity score with exponential decay
        inactive_users_df["Activity_Score"] = inactive_users_df["Base_Score"] * pd.np.exp(
            -inactive_users_df["Decay_Factor"]
        )
        # Sort by activity score (ascending)
        inactive_users_df = inactive_users_df.sort_values("Activity_Score")
        return inactive_users_df 