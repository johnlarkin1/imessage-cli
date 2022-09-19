"""This manager class differs from the client in a couple key ways. The client is largely just meant to retrieve the data.
    This will add additional features including sentiment analysis, correct casting to specific types, etc."""

from datetime import datetime
from typing import (
    List,
    Optional,
    Tuple,
)
from messages.messages_db_client import MessagesDbClient
from messages.model_generator import ModelGenerator, PromptCompletionPair
from messages.sentiment_classifier import (
    OverallSentiment,
    SentimentAnalysisModel,
    SentimentResult,
)

from messages.query_types import (
    AggregateSentimentStats,
    AllContactType,
    GetAllMessageType,
    GetAllMessageWithSentimentType,
    SearchWithSentimentType,
    TotalCountType,
    AllMessageType,
    SearchType,
)


def if_none_return_empty(maybe_empty: Optional[str]) -> str:
    """See name"""
    return "" if maybe_empty is None else maybe_empty


class MessagesDbManager:
    """Manager for the messages db."""

    def __init__(self) -> None:
        self.client = MessagesDbClient()
        self.sentiment_model = SentimentAnalysisModel()
        self.chatbot_model_generator = ModelGenerator(self.client)

    def total_distinct_convos(self) -> int:
        """Returns the number of distinct iMessage conversations"""
        return self.client.total_distinct_convos()

    def total_messages_by_contact_or_number_sorted(
        self, limit_number: Optional[int] = None
    ) -> List[TotalCountType]:
        """Returns the total number of messages per each contact"""
        return [
            TotalCountType(*x)
            for x in self.client.total_messages_by_contact_or_number_sorted(
                limit_number
            )
        ]

    def all_contacts(self) -> List[AllContactType]:
        """Returns a list of all contacts."""
        return [AllContactType(*x) for x in self.client.all_contacts()]

    def all_messages_sorted(
        self, limit_number: Optional[int] = None
    ) -> List[AllMessageType]:
        """Returns all messages sorted based in chronological order.
        This will be an expensive underlying query."""
        return [
            AllMessageType(*x) for x in self.client.all_messages_sorted(limit_number)
        ]

    def search_messages_by_text(
        self,
        search_text: str,
        search_number: Optional[str] = None,
        search_name: Optional[str] = None,
        search_date: Optional[datetime] = None,
        limit_number: Optional[int] = None,
        before_number: Optional[int] = None,
        after_number: Optional[int] = None,
    ) -> List[SearchWithSentimentType]:
        """Returns all message content filtered on a certain string.
        If you choose to pass in a phone number or a name, we will search on that as well"""
        results = [
            SearchType(*x)
            for x in self.client.search_messages_by_text(
                search_text,
                search_number,
                search_name,
                search_date,
                limit_number,
                before_number=before_number,
                after_number=after_number,
            )
        ]

        results_with_sentiment: List[SearchWithSentimentType] = []
        for result in results:
            results_with_sentiment.append(
                SearchWithSentimentType(
                    result.message_date,
                    if_none_return_empty(result.message_text),
                    result.is_from_me,
                    result.message_number,
                    self.sentiment_model.get_overall_sentiment_from_message(
                        result.message_text
                    ),
                    result.full_name,
                )
            )

        return results_with_sentiment

    def get_messages(
        self,
        get_number: Optional[str] = None,
        get_name: Optional[str] = None,
        get_date: Optional[datetime] = None,
        limit_number: Optional[int] = None,
    ) -> Tuple[List[GetAllMessageWithSentimentType], AggregateSentimentStats]:
        """Dumps all messages for a given name or number."""
        results = [
            GetAllMessageType(*x)
            for x in self.client.get_messages(
                get_number,
                get_name,
                get_date,
                limit_number,
            )
        ]

        results_with_sentiment: List[GetAllMessageWithSentimentType] = []
        running_compound_score = 0.0
        for result in results:
            score: SentimentResult = self.sentiment_model.analyze_message(
                result.message_text
            )
            running_compound_score += score.compound
            results_with_sentiment.append(
                GetAllMessageWithSentimentType(
                    result.message_date,
                    if_none_return_empty(result.message_text),
                    result.is_from_me,
                    result.message_number,
                    self.sentiment_model.get_overall_sentiment(score),
                    result.full_name,
                )
            )

        if len(results) == 0:
            aggregate_stats = AggregateSentimentStats(0.0, OverallSentiment.UNKNOWN)
            return (results_with_sentiment, aggregate_stats)

        averaged_compound_score = running_compound_score / len(results)
        overall_sentiment = self.sentiment_model.get_sentiment_from_scalar(
            averaged_compound_score
        )
        aggregate_stats = AggregateSentimentStats(
            averaged_compound_score, overall_sentiment
        )

        return (results_with_sentiment, aggregate_stats)

    def generate_prompt_completion(
        self,
        search_number: Optional[str] = None,
        search_name: Optional[str] = None,
    ) -> List[PromptCompletionPair]:
        """Generates the prompt completion pairing for GPT3"""
        # Ok so I thought a bit about the right way to do this.
        #
        # I think that it's going to be easier to have more accurate grouping logic in Python
        # as opposed to performing a more advanced SQL query.

        # So for aggregating messages, we really just want to aggregate if it's within the
        # same hour and if it's from the same user.

        # We're going to build up a list of tuples with each thing roughly looking like:
        # {"prompt": "<prompt text>", "completion": "<ideal generated text>"}

        results_to_save = self.chatbot_model_generator.generate_prompt_completion(
            search_number, search_name
        )
        if search_name:
            self.chatbot_model_generator.save_results_to_file(
                results_to_save, search_name
            )
        elif search_number:
            self.chatbot_model_generator.save_results_to_file(
                results_to_save, search_number
            )
        else:
            self.chatbot_model_generator.save_results_to_file(results_to_save)
        return results_to_save


if __name__ == "__main__":
    x = MessagesDbManager()
    results = x.generate_prompt_completion("5134901945")
