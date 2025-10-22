import re
from django.db.models import Q
from .models import AnalyzedString

##GPT
def NLP(query: str):
    query = query.lower()
    filters = {
        "is_palindrome": None,
        "word_count": None,
        "min_length": None,
        "max_length": None,
        "contains_character": None,
    }

    # --- PALINDROME DETECTION ---
    if "palindrome" in query or "palindromic" in query:
        if "non" in query or "not" in query:
            filters["is_palindrome"] = False
        else:
            filters["is_palindrome"] = True

    # --- WORD COUNT DETECTION ---
    number_words = {
        "one": 1,
        "single": 1,
        "two": 2,
        "double": 2,
        "three": 3,
        "triple": 3,
        "four": 4,
        "five": 5,
        "six": 6,
        "seven": 7,
        "eight": 8,
        "nine": 9,
        "ten": 10,
    }

    for word, num in number_words.items():
        if re.search(rf"\b{word}\b", query) and "word" in query:
            filters["word_count"] = num
            break

    match = re.search(r"(\d+)\s*(?:word|words)", query)
    if match:
        filters["word_count"] = int(match.group(1))

    # --- LENGTH DETECTION ---
    # "longer than N characters" → min_length = N + 1
    if match := re.search(r"longer than (\d+)", query):
        filters["min_length"] = int(match.group(1)) + 1

    # "shorter than N characters" → max_length = N - 1
    if match := re.search(r"shorter than (\d+)", query):
        filters["max_length"] = int(match.group(1)) - 1

    # "exactly N characters"
    if match := re.search(r"exactly (\d+) characters?", query):
        filters["min_length"] = filters["max_length"] = int(match.group(1))

    # "between N and M characters"
    if match := re.search(r"between (\d+) and (\d+) characters?", query):
        filters["min_length"], filters["max_length"] = int(match.group(1)), int(
            match.group(2)
        )

    # --- CONTAINS CHARACTER ---
    # Example: "contain the letter z" or "containing the character z"
    if match := re.search(
        r"(?:contain(?:s|ing)?(?: the)? (?:letter|character)? )([a-z])", query
    ):
        filters["contains_character"] = match.group(1)

    # handle "vowel" references heuristically
    if "vowel" in query:
        filters["contains_character"] = "a"  # heuristic, first vowel

    # handle common "consonant" references
    if "consonant" in query:
        filters["contains_character"] = "b"  # heuristic, first consonant

    # --- NEGATIONS ---
    # e.g. "strings not containing the letter z"
    if "not contain" in query or "without" in query:
        filters["contains_character"] = None  # exclude that filter

    # remove unset (None) values
    return {k: v for k, v in filters.items() if v is not None}


def get_filtered_queryset(filters: dict):
    #filters = NLP(description)
    query = Q()  # start with an empty query object

    if filters.get("is_palindrome") is not None:
        query &= Q(is_palindrome=filters["is_palindrome"])

    if filters.get("min_length") is not None:
        query &= Q(length__gte=filters["min_length"])

    if filters.get("max_length") is not None:
        query &= Q(length__lte=filters["max_length"])

    if filters.get("word_count") is not None:
        query &= Q(word_count=filters["word_count"])

    if filters.get("word_count_min") is not None:
        query &= Q(word_count__gte=filters["word_count_min"])

    if filters.get("word_count_max") is not None:
        query &= Q(word_count__lte=filters["word_count_max"])

    if filters.get("contains_character") is not None:
        query &= Q(original_string__icontains=filters["contains_character"])

    return AnalyzedString.objects.filter(query)
