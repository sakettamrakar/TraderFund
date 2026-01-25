"""
##############################################################################
## RESEARCH ONLY - NOT FOR LIVE TRADING
##############################################################################
Event Classifier

Tags news into high-level event categories.
Tags are DESCRIPTIVE only, not trade triggers.
##############################################################################
"""

from dataclasses import dataclass
from typing import List, Set
from enum import Enum
import re


class EventTag(str, Enum):
    """High-level event categories."""
    EARNINGS = "earnings"
    REGULATION = "regulation"
    LITIGATION = "litigation"
    MACRO = "macro"
    MANAGEMENT = "management"
    CORPORATE_ACTION = "corporate_action"
    SECTOR = "sector"
    UNKNOWN = "unknown"


# Keyword patterns for each category
EVENT_PATTERNS = {
    EventTag.EARNINGS: {
        "earnings", "revenue", "profit", "eps", "quarterly", "annual",
        "guidance", "forecast", "results", "beat", "miss", "q1", "q2", "q3", "q4",
    },
    EventTag.REGULATION: {
        "regulation", "regulatory", "sebi", "rbi", "compliance", "policy",
        "government", "ministry", "law", "legal", "approval", "license",
    },
    EventTag.LITIGATION: {
        "lawsuit", "litigation", "court", "case", "fraud", "investigation",
        "penalty", "fine", "settlement", "arbitration", "dispute",
    },
    EventTag.MACRO: {
        "inflation", "interest", "rate", "gdp", "economy", "recession",
        "fed", "central bank", "monetary", "fiscal", "unemployment",
    },
    EventTag.MANAGEMENT: {
        "ceo", "cfo", "director", "board", "management", "resign", "appoint",
        "executive", "leadership", "founder", "chairman",
    },
    EventTag.CORPORATE_ACTION: {
        "merger", "acquisition", "buyback", "dividend", "split", "bonus",
        "ipo", "listing", "delist", "takeover", "spinoff",
    },
    EventTag.SECTOR: {
        "industry", "sector", "peers", "competition", "market share",
        "competitor", "consolidation",
    },
}


def classify_events(text: str) -> List[EventTag]:
    """Classify text into event categories.

    Returns all matching categories, not just one.
    This is purely DESCRIPTIVE tagging.

    Args:
        text: Text to classify.

    Returns:
        List of matching EventTags.
    """
    if not text:
        return [EventTag.UNKNOWN]

    words = set(re.findall(r"\b\w+\b", text.lower()))
    matched_tags = []

    for tag, keywords in EVENT_PATTERNS.items():
        if words & keywords:
            matched_tags.append(tag)

    return matched_tags if matched_tags else [EventTag.UNKNOWN]


def get_primary_event(text: str) -> EventTag:
    """Get the most likely event category.

    Args:
        text: Text to classify.

    Returns:
        Single most relevant EventTag.
    """
    if not text:
        return EventTag.UNKNOWN

    words = set(re.findall(r"\b\w+\b", text.lower()))
    best_tag = EventTag.UNKNOWN
    best_score = 0

    for tag, keywords in EVENT_PATTERNS.items():
        score = len(words & keywords)
        if score > best_score:
            best_score = score
            best_tag = tag

    return best_tag


def extract_topics(text: str, top_n: int = 5) -> List[str]:
    """Extract most common content words as topics.

    This is a simple frequency-based approach.

    Args:
        text: Text to analyze.
        top_n: Number of topics to return.

    Returns:
        List of topic words.
    """
    if not text:
        return []

    # Common stopwords to exclude
    stopwords = {
        "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did", "will", "would", "could",
        "should", "may", "might", "must", "shall", "can", "need", "dare",
        "to", "of", "in", "for", "on", "with", "at", "by", "from", "as",
        "into", "through", "during", "before", "after", "above", "below",
        "between", "under", "again", "further", "then", "once", "here",
        "there", "when", "where", "why", "how", "all", "each", "few", "more",
        "most", "other", "some", "such", "no", "nor", "not", "only", "own",
        "same", "so", "than", "too", "very", "just", "and", "but", "if", "or",
        "because", "as", "until", "while", "this", "that", "these", "those",
        "it", "its", "he", "she", "they", "them", "his", "her", "their",
    }

    words = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())
    word_counts = {}

    for word in words:
        if word not in stopwords:
            word_counts[word] = word_counts.get(word, 0) + 1

    sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
    return [word for word, count in sorted_words[:top_n]]
