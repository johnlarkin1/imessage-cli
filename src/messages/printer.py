"""Handles printing to stdout. This should be deprecated for some better tool at some point."""

from typing import (
    Any,
    List,
    Union,
)

import os
import click
from messages.query_types import (
    AggregateSentimentStats,
    AllContactType,
    GetAllMessageWithSentimentType,
    SearchWithSentimentType,
    TotalCountType,
)
from messages.utils import cleanse_message, maybe_mask_name, maybe_mask_phone_number, maybe_scramble_string

MASK_PII_DATA = bool(os.getenv("MASK_PII_DATA", None))
MASK_MESSAGE_TEXT = bool(os.getenv("MASK_MESSAGE_TEXT", None))

class Printer:
    """Handles printing returned data results from sqlite."""

    @staticmethod
    def split_text_shorter(text: str, column_start_pos: int, column_length: int) -> str:
        """We want to pad every line with the column start and then have new lines when we've hit the right length"""
        # How many lines will we need?
        num_lines = len(text) // column_length
        line_builder = ""
        for idx in range(num_lines + 1):
            init_padding = " " * column_start_pos if idx != 0 else ""
            offset = column_length
            line_content = text[idx * offset : (idx + 1) * offset]
            rest_of_line_padding = " " * (column_length - len(line_content))
            line_builder += init_padding + line_content + rest_of_line_padding + "|\n"

        line_builder = line_builder[
            :-2
        ]  # take off last two things these will get put on later
        return line_builder

    @staticmethod
    def show_title(*kwargs: Any) -> None:
        """Shows the title for a given list of args."""
        title = ""
        for potential_column_tuple in kwargs:
            if isinstance(potential_column_tuple, tuple):
                column_name, column_spacing = potential_column_tuple
                title += f"{column_name:^{column_spacing}}| "
            else:
                column_name = potential_column_tuple
                title += f"{column_name} | "

        # Get rid of final |
        title = title[:-2]
        click.echo(title)
        click.echo("-" * len(title))

    @staticmethod
    def print_total_messages_data(results: List[TotalCountType]) -> None:
        """Prints message data. (Rank, Name/Number, Message Count)"""
        column1 = "Rank"
        column2 = "Name / Number"
        column2_spacing = 50
        column3 = "Message Count"
        Printer.show_title(column1, (column2, column2_spacing), column3)
        for idx, result in enumerate(results):
            contact_number = maybe_mask_phone_number(result.message_number, MASK_PII_DATA)
            contact_msg_count = result.message_count
            contact_name = result.full_name if result.full_name is not None else ""
            contact_name = maybe_mask_name(contact_name, MASK_PII_DATA)
            if result.full_name:
                click.echo(
                    f"{idx+1:^5}| {contact_name + ' (' + contact_number + ')':^{column2_spacing}}| {contact_msg_count:^{len(column3)},}"
                )
            else:
                click.echo(
                    f"{idx+1:<5}. {contact_number:^{column2_spacing}}|{contact_msg_count:^{len(column3)},}"
                )

    @staticmethod
    def print_generic_message_data(
        results: Union[
            List[SearchWithSentimentType], List[GetAllMessageWithSentimentType]
        ]
    ) -> None:
        """Prints search data. (Idx, Date, Name/Number, Message, Sent/Received)"""
        # pylint: disable=too-many-locals
        column1 = "Idx"
        column1_spacing = 5
        column2 = "Date"
        column2_spacing = 20
        column3 = "Name / Number"
        column3_spacing = 40
        column4 = "Message"
        column4_spacing = 75
        column5 = "Sentiment"
        column5_spacing = 10
        column6 = "Sent (1) / Received (0)"
        column6_spacing = len(column5)
        Printer.show_title(
            (column1, column1_spacing),
            (column2, column2_spacing),
            (column3, column3_spacing),
            (column4, column4_spacing),
            (column5, column5_spacing),
            (column6, column6_spacing),
        )
        for idx, result in enumerate(results):
            message_date = result.message_date
            message_text: str = (
                result.message_text if result.message_text is not None else ""
            )
            sent_by = result.is_from_me
            number = maybe_mask_phone_number(result.message_number, MASK_PII_DATA)
            sentiment = result.sentiment
            name = result.full_name if result.full_name is not None else ""
            name = maybe_mask_name(name, MASK_PII_DATA)

            # Clean message_text or \n or \r\n
            message_text = cleanse_message(message_text)
            message_text = maybe_scramble_string(message_text, MASK_MESSAGE_TEXT)

            if len(message_text) > column4_spacing:
                # Try to fit everything on screen
                all_col_spacing = column1_spacing + column2_spacing + column3_spacing
                all_col_spacing += 6
                message_text = Printer.split_text_shorter(
                    message_text, all_col_spacing, column4_spacing
                )

            click.echo(
                f"{idx+1:^{column1_spacing}}| "
                + f"{message_date:^{column2_spacing}}| "
                + f"{name + ' (' + number + ')':^{column3_spacing}}| "
                + f"{message_text:<{column4_spacing}}| "
                + f"{sentiment:^{column5_spacing}}| "
                + f"{sent_by:^{column6_spacing}}"
            )

    @staticmethod
    def print_search_data(results: List[SearchWithSentimentType]) -> None:
        """Print search data"""
        Printer.print_generic_message_data(results)

    @staticmethod
    def print_get_data(results: List[GetAllMessageWithSentimentType]) -> None:
        """Print get data"""
        Printer.print_generic_message_data(results)

    @staticmethod
    def print_all_contacts(results: List[AllContactType]) -> None:
        """Print all contact info"""
        column1 = "Idx"
        column1_spacing = 5
        column2 = "Number"
        column2_spacing = 20
        column3 = "Name"
        column3_spacing = 50
        Printer.show_title(
            (column1, column1_spacing),
            (column2, column2_spacing),
            (column3, column3_spacing),
        )
        for idx, result in enumerate(results):
            click.echo(
                f"{idx+1:^{column1_spacing}}| "
                + f"{result.contact_number:^{column2_spacing}}"
                + f"{result.contact_name:^{column3_spacing}}"
            )

    @staticmethod
    def print_aggregate_sentiment(aggregated: AggregateSentimentStats) -> None:
        """Print aggregate sentiment"""
        divider = "="
        divider_length = 50
        click.echo(divider * divider_length)
        click.echo(
            f"Overall sentiment: {aggregated.sentiment} with a compound VADER score of {aggregated.compound}"
        )
        click.echo(divider * divider_length)


if __name__ == "__main__":
    Printer.show_title("test1", "test2", "test3")
    Printer.show_title("test1", ("test2", 50), "test3", "test4")
    Printer.show_title("test1", "test2", ("test3", 50), "test4")
    Printer.print_search_data([])
