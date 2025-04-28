import re
from typing import List
import spacy

# Load spaCy model
nlp = spacy.load("en_core_web_sm")


def split_into_sentences(text: str) -> List[str]:
    """
    Split text into sentences while preserving newlines and special formatting.

    Args:
        text (str): Input text to be split

    Returns:
        List[str]: List of sentences with preserved formatting
    """
    # Split text into lines first to preserve newline patterns
    lines = text.split("\n")
    sentences = []

    # Special patterns to treat as sentence boundaries
    special_starts = [
        r"^\d+\.",  # Numbered lists (e.g., "1.", "2.")
        r"^[-\*\+]\s",  # Bullet points
        r"^#+\s",  # Markdown headers
        r"^>\s",  # Blockquotes
    ]

    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            # Add newline marker to previous sentence if it exists
            if sentences:
                sentences[-1] = sentences[-1] + "\n"
            continue

        # Check if line starts with special pattern
        is_special_start = any(re.match(pattern, line) for pattern in special_starts)
        if is_special_start:
            sentences.append(line)
            # Add newline if this isn't the last line and next line is empty
            if i < len(lines) - 1 and not lines[i + 1].strip():
                sentences[-1] = sentences[-1] + "\n"
            continue

        # Use spaCy for regular text sentence splitting
        doc = nlp(line)
        line_sentences = [sent.text.strip() for sent in doc.sents]

        # Add sentences
        for j, sent in enumerate(line_sentences):
            if sent:
                sentences.append(sent)
                # Add newline if this is the last sentence of the line
                # and if next line is empty
                if (
                    j == len(line_sentences) - 1
                    and i < len(lines) - 1
                    and not lines[i + 1].strip()
                ):
                    sentences[-1] = sentences[-1] + "\n"

    if lines[-1]:
        sentences[-1] = sentences[-1].strip()

    return sentences


def reconstruct_text(sentences: List[str]) -> str:
    """
    Reconstruct original text from sentences.

    Args:
        sentences (List[str]): List of sentences

    Returns:
        str: Reconstructed text
    """
    reconstructed = []
    current_paragraph = []

    for sent in sentences:
        has_newline = sent.endswith("\n")
        # clean_sent = sent.rstrip("\n")

        # Handle special formatting
        if any(sent.startswith(char) for char in ["#", ">", "-", "*", "+"]) or re.match(
            r"^\d+\.", sent
        ):
            # Flush current paragraph if any
            if current_paragraph:
                reconstructed.append(" ".join(current_paragraph))
                current_paragraph = []
            reconstructed.append(sent + "\n")
            if has_newline:
                reconstructed.append("")  # Add empty line after special formatting
        else:
            # Add to current paragraph
            current_paragraph.append(sent)
            if has_newline:
                reconstructed.append(" ".join(current_paragraph))
                current_paragraph = []

    # Flush any remaining paragraph
    if current_paragraph:
        reconstructed.append(" ".join(current_paragraph))

    # Join with newlines and clean up multiple consecutive empty lines
    result = "".join(reconstructed)
    # result = re.sub(r"\n\n+", "\n\n", result)
    return result
