from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

import click
from messages.messages_db_client import MessagesDbClient
from messages.query_types import GetAllMessageType
from messages.utils import cleanse_message


@dataclass
class PromptCompletionPair:
    prompt: str = ""
    completion: str = ""

    def __str__(self) -> str:
        return f'{{"prompt": "{self.prompt}", "completion": "{self.completion}"}}'


def minutes_between(date1: datetime, date2: datetime) -> int:
    seconds_in_day = 24 * 60 * 60
    difference = date2 - date1
    diff_min = divmod(
        abs(difference.days) * seconds_in_day + abs(difference.seconds), 60
    )[0]
    return diff_min


class ModelGenerator:
    def __init__(self, client: Optional[MessagesDbClient] = None) -> None:
        self.client = client if client is not None else MessagesDbClient()

    def _should_aggregate_two_messages(
        self, previous_message: GetAllMessageType, next_message: GetAllMessageType
    ) -> bool:
        # if the next message is outside of the time window, and still from sender, we'll break
        breaking_time_window = 30  # min
        previous_msg_date = datetime.strptime(
            previous_message.message_date, "%Y-%m-%d %H:%M:%S"
        )
        next_msg_date = datetime.strptime(
            previous_message.message_date, "%Y-%m-%d %H:%M:%S"
        )

        is_change_of_sender = previous_message.is_from_me != next_message.is_from_me
        if is_change_of_sender:
            return False

        if minutes_between(previous_msg_date, next_msg_date) >= breaking_time_window:
            return False

        return True

    def generate_and_build_model(self) -> None:
        """
        1. Prepare the training dataset
        2. Train a new fine-tuned model
        3. Use the new fine-tuned model
        """
        pass

    def generate_prompt_completion(
        self,
        search_number: Optional[str] = None,
        search_name: Optional[str] = None,
    ) -> List[PromptCompletionPair]:
        """Generates a list of {prompt: <txt>, completion: <txt>}.
        The prompts will all be messages that the user has sent. The completion will be what the model / number getting queried should respond with."""
        # Ok so I thought a bit about the right way to do this.
        #
        # I think that it's going to be easier to have more accurate grouping logic in Python
        # as opposed to performing a more advanced SQL query.
        messages = [
            GetAllMessageType(*x)
            for x in self.client.get_messages(
                search_number,
                search_name,
            )
        ]

        # So for aggregating messages, we really just want to aggregate if it's within the
        # same hour and if it's from the same user.

        # We're going to build up a list of tuples with each thing roughly looking like:
        # {"prompt": "<prompt text>", "completion": "<ideal generated text>"}

        finalized_results_to_save: List[PromptCompletionPair] = []
        running_completion_pair = PromptCompletionPair()
        last_message: Optional[GetAllMessageType] = None
        for message in messages:
            is_sender = message.is_from_me
            should_we_aggregate = False
            message_text = cleanse_message(message.message_text, cleanse_emojis=True)

            if last_message is not None:
                should_we_aggregate = self._should_aggregate_two_messages(
                    last_message, message
                )

            if should_we_aggregate:
                if is_sender:
                    print(
                        f"Aggregating for sender with prompt: {running_completion_pair.prompt}and adding text: {message_text}"
                    )
                    running_completion_pair.prompt += f"{message_text}. "
                else:
                    print(
                        f"Aggregating for receiver with prompt: {running_completion_pair.completion} and adding text: {message_text}"
                    )
                    running_completion_pair.completion += f"{message_text}. "
            else:
                # If we shouldn't aggregate, we can just normally set the fields
                if is_sender:
                    running_completion_pair.prompt = message_text
                else:
                    running_completion_pair.completion = message_text

                if (
                    running_completion_pair.prompt != ""
                    and running_completion_pair.completion != ""
                ):
                    finalized_results_to_save.append(running_completion_pair)
                    running_completion_pair = PromptCompletionPair()

            last_message = message

        return finalized_results_to_save

    def save_results_to_file(
        self,
        prompt_completions: List[PromptCompletionPair],
        model_identifier: str = "model_identifier",
    ) -> None:
        file_base = f"{model_identifier}"
        now = datetime.now()
        now_str = now.strftime("%m_%d_%Y_%H_%M_%S")
        filename = f"{file_base}.{now_str}.jsonl"
        with open(filename, "w") as f:
            for prompt in prompt_completions:
                f.write(str(prompt))
                f.write("\n")

        click.echo(f"Generated jsonl prompt-completion for model at: {filename}")


if __name__ == "__main__":
    x = PromptCompletionPair("test_prompt", "test_completion")
    print(x)
