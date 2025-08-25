# cursword

Simple functions to move by words in a string.
- Useful for word-based cursors.
- Use Unicode character classification to detect word boundaries.

## Installation

```bash
pip install cursword
```

## Quick Start

```python
from cursword import get_next_word_end_position, get_previous_word_start_position

text = "Hello world, how are you?"

# Find the end of the first word starting from position 0
next_pos = get_next_word_end_position(text, 0)
print(f"First word ends at position {next_pos}: '{text[:next_pos]}'")
# Output: First word ends at position 5: 'Hello'

# Find the start of the last word from the end
prev_pos = get_previous_word_start_position(text, len(text))
print(f"Last word starts at position {prev_pos}: '{text[prev_pos:]}'")
# Output: Last word starts at position 24: '?'
```

## API Reference

### `get_next_word_end_position(text: str, start: int) -> int`

Returns the position of the end of the current or next word in the given text.

**Parameters:**
- `text` (str): The text to search in
- `start` (int): The position to start searching from

**Returns:**
- `int`: The position after the end of the current/next word, or `len(text)` if no word is found

**Example:**
```python
from cursword import get_next_word_end_position

text = "abc def ghi"
pos = get_next_word_end_position(text, 0)  # Returns 3 (end of "abc")
pos = get_next_word_end_position(text, pos)  # Returns 7 (end of "def")
```

### `get_previous_word_start_position(text: str, start: int) -> int`

Returns the position of the start of the previous word in the given text.

**Parameters:**
- `text` (str): The text to search in
- `start` (int): The position to start searching from

**Returns:**
- `int`: The position of the start of the previous word, or `0` if no word is found

**Example:**
```python
from cursword import get_previous_word_start_position

text = "abc def ghi"
pos = get_previous_word_start_position(text, len(text))  # Returns 8 (start of "ghi")
pos = get_previous_word_start_position(text, pos)  # Returns 4 (start of "def")
```

## How It Works

The library categorizes characters into different types:

- **Word characters**: Letters, numbers, and underscores
- **Punctuation**: Various punctuation marks and mathematical symbols
- **Currency**: Currency symbols
- **Space**: Whitespace characters
- **Other**: All other characters (including CJK ideographs)

Word boundaries are detected when transitioning between different character categories,
allowing for intelligent navigation through mixed content.

## Known limitations

- **CJK Text**: Chinese, Japanese, and Korean characters are currently treated as single blocks
  rather than individual word units.

## Development

```bash
# Best suited for uv
uv sync

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=cursword --cov-report=html --cov-report=term-missing

# Lint code
uv run ruff check

# Format code
uv run ruff format
```
