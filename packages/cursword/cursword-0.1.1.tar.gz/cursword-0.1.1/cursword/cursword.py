import unicodedata

UNICODE_MATH_CATEGORY = "Sm"
UNICODE_MODIFIED_CATEGORY = "Sk"


def _is_word(c: str) -> bool:
    return c.isalnum() or c == "_"


def _is_punc(c: str) -> bool:
    uc = unicodedata.category(c)
    return uc.startswith("P") or uc in (
        UNICODE_MATH_CATEGORY,
        UNICODE_MODIFIED_CATEGORY,
    )


def _is_currency(c: str) -> bool:
    uc = unicodedata.category(c)
    return uc == "Sc"


CAT_NONE = -1
CAT_SPACE = 0
CAT_WORD = 1
CAT_PUNC = 2
CAT_CURR = 3
CAT_OTHER = 4


def _get_category(c: str) -> int:
    if c == " ":
        return CAT_SPACE
    elif _is_word(c):
        return CAT_WORD
    elif _is_punc(c):
        return CAT_PUNC
    elif _is_currency(c):
        return CAT_CURR
    else:
        return CAT_OTHER


def get_previous_word_start_position(text: str, start: int) -> int:
    """
    Find **the start of** previous word in given text.
    :param text: given text
    :param start: position from when to start search.
        If a word starts at this position, it will be ignored.
    :return: start position of previous word, or 0 if no word found.
    """

    # Always move to start - 1
    start = start - 1

    start = min(max(0, start), len(text) - 1)
    cat = CAT_NONE
    for i in range(start, -1, -1):
        local_cat = _get_category(text[i])
        if cat == CAT_NONE:
            if local_cat != CAT_SPACE:
                cat = local_cat
        elif local_cat != cat:
            return i + 1
    else:
        return 0


def get_next_word_end_position(text: str, start: int) -> int:
    """
    Find **the end of** current or next word in given text.
    :param text: given text
    :param start: position from when to start search.
        If a word starts at this position, find the end of this word.
    :return: position of first character after current of next word,
        so that `position - 1` is the actual end of current or next word.
    """

    start = min(max(0, start), max(0, len(text) - 1))
    cat = CAT_NONE
    for i in range(start, len(text)):
        local_cat = _get_category(text[i])
        if cat == CAT_NONE:
            if local_cat != CAT_SPACE:
                cat = local_cat
        elif local_cat != cat:
            return i
    else:
        return len(text)
