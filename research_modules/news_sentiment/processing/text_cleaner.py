"""
##############################################################################
## RESEARCH ONLY - NOT FOR LIVE TRADING
##############################################################################
Text Cleaner

Basic text normalization for sentiment analysis.
##############################################################################
"""

import re
from typing import Optional


def clean_html(text: str) -> str:
    """Remove HTML tags from text.

    Args:
        text: Raw text possibly containing HTML.

    Returns:
        Text with HTML tags removed.
    """
    # Remove HTML tags
    clean = re.sub(r"<[^>]+>", " ", text)
    # Remove HTML entities
    clean = re.sub(r"&[a-zA-Z]+;", " ", clean)
    return clean


def normalize_whitespace(text: str) -> str:
    """Collapse multiple whitespace into single spaces.

    Args:
        text: Input text.

    Returns:
        Normalized text.
    """
    return " ".join(text.split())


def remove_urls(text: str) -> str:
    """Remove URLs from text.

    Args:
        text: Input text.

    Returns:
        Text without URLs.
    """
    return re.sub(r"https?://\S+", "", text)


def clean_text(
    text: str,
    remove_html: bool = True,
    remove_links: bool = True,
    normalize_ws: bool = True,
) -> str:
    """Full text cleaning pipeline.

    Args:
        text: Raw text.
        remove_html: Whether to strip HTML tags.
        remove_links: Whether to remove URLs.
        normalize_ws: Whether to normalize whitespace.

    Returns:
        Cleaned text.
    """
    if not text:
        return ""

    result = text

    if remove_html:
        result = clean_html(result)

    if remove_links:
        result = remove_urls(result)

    if normalize_ws:
        result = normalize_whitespace(result)

    return result.strip()


def extract_sentences(text: str) -> list:
    """Split text into sentences.

    Args:
        text: Input text.

    Returns:
        List of sentences.
    """
    # Simple sentence splitting
    sentences = re.split(r"[.!?]+", text)
    return [s.strip() for s in sentences if s.strip()]
