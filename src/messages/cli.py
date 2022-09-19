"""Handles all interactions between using this package as a CLI tool.

What this command line tool should be able to do:
1. List top ten people that user has chatted with most.
2. Search through all messages.
3. Search through specific message for text.
4. Get total number of conversations had
"""

from datetime import datetime
import sys
from typing import Optional

import click
from messages.messages_db_client import MessagesDbClient
from messages.messages_db_manager import MessagesDbManager
from messages.printer import Printer

client = MessagesDbClient()
manager = MessagesDbManager()


@click.group()
def cli() -> None:
    """Main entry point for command line."""
    if len(sys.argv) == 1:
        cli.main(["--help"])


@cli.command(no_args_is_help=True)
@click.option(
    "-t",
    "--total-number",
    "total_number",
    is_flag=True,
    default=False,
    help="List the number of distinct conversations.",
)
def convos(total_number: Optional[bool]) -> None:
    """Subcommand to analyze messages."""
    if total_number:
        num_conversations = manager.total_distinct_convos()
        click.echo(f"Total number of distinct conversations: {num_conversations}")


@cli.command(no_args_is_help=True)
@click.option(
    "-t",
    "--top-n-contacts",
    "top_n_contacts",
    type=int,
    help="List top n people that user has chatted with.",
)
@click.option(
    "-l",
    "--list",
    "should_list",
    is_flag=True,
    default=False,
    help="List all contacts.",
)
def contacts(
    top_n_contacts: Optional[int],
    should_list: Optional[bool],
) -> None:
    """Subcommand to aggregate contact information."""
    if len(sys.argv) == 1:
        cli.main(["--help"])
    if top_n_contacts:
        total_results = manager.total_messages_by_contact_or_number_sorted(
            top_n_contacts
        )
        Printer.print_total_messages_data(total_results)
        return

    if should_list:
        contact_results = manager.all_contacts()
        Printer.print_all_contacts(contact_results)
        return


@cli.command(no_args_is_help=True)
@click.argument("search_text")
@click.option(
    "-c",
    "--contact",
    "contact",
    type=str,
    help="The name of the contact to search.",
)
@click.option(
    "-n",
    "--number",
    "number",
    type=str,
    help="The number of the contact to search.",
)
@click.option(
    "-l",
    "--limit-number",
    "limit_number",
    type=int,
    help="The amount to limit the results by.",
)
@click.option(
    "-b",
    "--before-number",
    "before_number",
    type=int,
    help="Coming soon... The amount of texts to show before the matching result.",
)
@click.option(
    "-a",
    "--after-number",
    "after_number",
    type=int,
    help="Coming soon...The amount of texts to show after the matching result.",
)
def search(
    search_text: str,
    contact: Optional[str],
    number: Optional[str],
    limit_number: Optional[int],
    before_number: Optional[int],
    after_number: Optional[int],
) -> None:
    """Subcommand to search messages by name, contact, and/or text."""
    click.echo(
        f"Searching contact: {contact} or number: {number} with text: {search_text}"
    )
    if contact and number:
        click.echo(
            f"Both contact ({contact}) and number ({number}) cannot be specified at the same time. Please only specify one."
        )
        return

    if contact:
        results = manager.search_messages_by_text(
            search_text,
            search_name=contact,
            limit_number=limit_number,
            before_number=before_number,
            after_number=after_number,
        )
        Printer.print_search_data(results)
        return

    if number:
        results = manager.search_messages_by_text(
            search_text,
            search_number=number,
            limit_number=limit_number,
            before_number=before_number,
            after_number=after_number,
        )
        Printer.print_search_data(results)
        return

    # If no number, no contact, and no date, then we'll just search over all messages for the search_text
    results = manager.search_messages_by_text(search_text)
    Printer.print_search_data(results)


@cli.command(no_args_is_help=True)
@click.option(
    "-c",
    "--contact",
    "contact",
    type=str,
    help="The name of the contact to search.",
)
@click.option(
    "-n",
    "--number",
    "number",
    type=str,
    help="The number of the contact to search.",
)
@click.option(
    "-d",
    "--date",
    "tgt_date",
    type=str,
    help="The date to retrieve all messages. Enter as YYYY-MM-DD",
)
@click.option(
    "-l",
    "--limit-number",
    "limit_number",
    type=int,
    help="The amount to limit the results by.",
)
def get(
    contact: Optional[str],
    number: Optional[str],
    tgt_date: Optional[str],
    limit_number: Optional[int],
) -> None:
    """Subcommand to get all messages for a certain name or contact. You need to specify either a number or a contact.

    This will also analyze sentiment for all dumped messages, and aggregate the total conversations
    sentiment on a score from -1.00 (negative) to 1.00 (positive).

    That being said, don't place too much value on that. It's just using VADER not some more complex OpenAI logic."""
    if not contact and not number and not tgt_date:
        click.echo(
            "You must specify a contact name, contact number, or date to dump messages for."
        )
        return

    tgt_date_obj: Optional[datetime] = None
    if tgt_date:
        tgt_date_obj = datetime.strptime(tgt_date, "%Y-%m-%d")
    results, aggregated = manager.get_messages(
        get_name=contact,
        get_number=number,
        get_date=tgt_date_obj,
        limit_number=limit_number,
    )
    Printer.print_get_data(results)
    Printer.print_aggregate_sentiment(aggregated)


@cli.command(no_args_is_help=True)
@click.option(
    "-c",
    "--contact",
    "contact",
    type=str,
    help="The name of the contact to search.",
)
@click.option(
    "-n",
    "--number",
    "number",
    type=str,
    help="The number of the contact to search.",
)
@click.option(
    "-l",
    "--limit-number",
    "limit_number",
    type=int,
    help="The amount to limit the results by. If empty, will scan full history.",
)
def generate(
    contact: Optional[str],
    number: Optional[str],
    limit_number: Optional[int],
) -> None:
    """NOT COMPLETE YET.

    Subcommand to generate a training file used for GPT3 to fine-tune a model for more flavored
    chatbots in the natural voice of friends/families/anyone in your contacts. This is an expensive endpoint.

    This endpoint will first generate a data dump of all conversations with the specific name or contact. In order to handle multiple messages being sent back to back, those will be aggregated in one to have a call and response type behavior.

    The generated file in JSONL format, which is like the folllowing type:
    {"prompt": "<prompt text>", "completion": "<ideal generated text>"}
    {"prompt": "<prompt text>", "completion": "<ideal generated text>"}
    {"prompt": "<prompt text>", "completion": "<ideal generated text>"}

    will then get fed to OpenAI which will then get processed.
    """
    if not contact and not number:
        click.echo(
            "You must specify a contact name or a contact number to dump messages for."
        )
        return

    if contact:
        results, aggregated = manager.get_messages(
            get_name=contact, limit_number=limit_number
        )
        Printer.print_get_data(results)
        Printer.print_aggregate_sentiment(aggregated)
        return

    results, aggregated = manager.get_messages(
        get_number=number, limit_number=limit_number
    )
    Printer.print_get_data(results)
    Printer.print_aggregate_sentiment(aggregated)
