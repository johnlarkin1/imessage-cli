"""This is a helper class to analyze sentiment of various text messages."""

from dataclasses import dataclass
from enum import (
    auto,
    Enum,
)
from typing import Optional
from nltk.sentiment import SentimentIntensityAnalyzer


@dataclass
class SentimentResult:
    """Dataclass for sentiment type."""

    neg: float
    neu: float
    pos: float
    compound: float

    @classmethod
    def empty(cls) -> "SentimentResult":
        return SentimentResult(0, 0, 0, 0)


class OverallSentiment(Enum):
    """Enum for summary of ."""

    UNKNOWN = auto()
    POSITIVE = auto()
    NEGATIVE = auto()
    NEUTRAL = auto()

    def __str__(self) -> str:
        return str(self.name).lower()


class SentimentAnalysisModel:
    """Model to analyze message content for sentiment. Uses VADER (Valence Aware Dictionary for Sentiment Reasoning).

    VADER is 'best suited for language used in social media, like short sentences with some slang and abbreviations.'

    It is intelligent enough to understand the basic context (for example, did not love would result in a negative
    compound score). It understands emphasis of capitalization and punctuation.
    """

    def __init__(self) -> None:
        self.model = SentimentIntensityAnalyzer()

    def analyze_message(self, message: Optional[str]) -> SentimentResult:
        """Analyzes a message and returns a numeric value showing scores.

        The compound score is computed by summing the valence scores of each word in the lexicon,
        adjusted according to the rules, and then normalized to be between -1 (most extreme negative)
        and +1 (most extreme positive).
        This is the most useful metric if you want a single unidimensional measure of sentiment for a given sentence.
        Calling it a 'normalized, weighted composite score' is accurate.
        It is also useful for researchers who would like to set standardized thresholds for classifying sentences
        as either positive, neutral, or negative.
        Typical threshold values (used in the literature cited on this page) are:
        positive sentiment: compound score >= 0.05
        neutral sentiment: (compound score > -0.05) and (compound score < 0.05)
        negative sentiment: compound score <= -0.05
        """
        if not message:
            return SentimentResult.empty()
        scores = self.model.polarity_scores(message)
        return SentimentResult(
            scores["neg"], scores["neu"], scores["pos"], scores["compound"]
        )

    @classmethod
    def get_overall_sentiment(cls, score: SentimentResult) -> OverallSentiment:
        """Returns an overall OverallSentiment enum based on the SentimentResult"""
        return cls.get_sentiment_from_scalar(score.compound)

    @classmethod
    def get_sentiment_from_scalar(cls, compound: float) -> OverallSentiment:
        if compound >= 0.05:
            return OverallSentiment.POSITIVE
        if compound > -0.05:
            return OverallSentiment.NEUTRAL
        return OverallSentiment.NEGATIVE

    def get_overall_sentiment_from_message(
        self, message: Optional[str]
    ) -> OverallSentiment:
        if message is None:
            return OverallSentiment.UNKNOWN
        scores = self.analyze_message(message)
        return self.get_overall_sentiment(scores)


if __name__ == "__main__":
    model = SentimentIntensityAnalyzer()
    text = "This was a great movie"
    scores = model.polarity_scores(text)
    print(f"Text: {text} Scores: {scores}")

    text = "This was a great movie!!"
    scores = model.polarity_scores(text)
    print(f"Text: {text} Scores: {scores}")

    text = "This was a GREAT movie!!"
    scores = model.polarity_scores(text)
    print(f"Text: {text} Scores: {scores}")

    text = "This was NOT a great movie"
    scores = model.polarity_scores(text)
    print(f"Text: {text} Scores: {scores}")
