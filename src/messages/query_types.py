"""Contains all the types that we return from our query object."""

from dataclasses import dataclass
from typing import Optional

from messages.sentiment_classifier import OverallSentiment

# pylint: disable=missing-class-docstring


@dataclass
class TotalCountType:
    message_number: str
    message_count: int
    full_name: Optional[str] = None


@dataclass
class AllContactType:
    contact_number: str
    contact_name: Optional[str] = None


@dataclass
class AllMessageType:
    message_date: str
    message_text: Optional[str]
    is_from_me: bool
    message_number: str
    full_name: Optional[str] = None


@dataclass
class SearchType:
    message_date: str
    message_text: Optional[str]
    is_from_me: bool
    message_number: str
    full_name: Optional[str] = None


@dataclass
class GetAllMessageType:
    message_date: str
    message_text: Optional[str]
    is_from_me: bool
    message_number: str
    full_name: Optional[str] = None


@dataclass
class BaseMessageWithSentimentType:
    message_date: str
    message_text: Optional[str]
    is_from_me: bool
    message_number: str
    sentiment: OverallSentiment
    full_name: Optional[str] = None


@dataclass
class AggregateSentimentStats:
    compound: float
    sentiment: OverallSentiment


GetAllMessageWithSentimentType = BaseMessageWithSentimentType
SearchWithSentimentType = BaseMessageWithSentimentType
