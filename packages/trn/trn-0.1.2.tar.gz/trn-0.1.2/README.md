# trn

A CLI tool for translating text using LLMs.

## Features

- Multiple input sources: command line arguments, stdin, clipboard, URLs, or files
- Supports LLMs from OpenAI, Anthropic, and Google Gemini
- Configurable via command line arguments or environment variables

## Installation

If you have [uv](https://docs.astral.sh/uv/) installed, you don't need to install the
package—just use `uvx trn`. You can also install it normally:

```bash
uv tool install trn
# or
pip install trn
```

## Usage

First, [set the key](https://llm.datasette.io/en/stable/help.html#llm-keys-help) for your LLM
provider. Example for Google Gemini:

    uvx --with llm-gemini llm keys set gemini

Second, specify your target language via the `TRN_TO_LANGUAGE` environment variable or `-t` argument.
The `-t` argument takes priority when both are set.

Third, provide text to translate in one of these ways:

- command line arguments
- standard input
- clipboard

The tool checks for arguments first, then standard input, then the clipboard.

You can also translate web pages or local PDF/image files by providing a URL or file path.

### Basic Usage

```bash
# Translate from clipboard to default language
trn

# Translate command line text
trn -t french Hello world

# Translate from stdin
echo "Hello world" | trn -t german

# Translate a file
trn -t italian document.txt

# Translate from URL
trn -t japanese https://example.com/article
```

### Configuration

Set environment variables for convenience:

    export TRN_TO_LANGUAGE=spanish
    # optionally:
    export TRN_MODEL=gpt-4o-mini

### Options

- `-t, --to-language`: Target language (required)
- `-m, --model`: LLM model to use (default: gpt-4o-mini)
- `--prompt`: Custom translation prompt
- `-v, --verbose`: Enable verbose output
- `-d, --debug`: Enable debug output

### Advanced Examples

```bash
# Use different model
trn -t spanish -m claude-3-haiku "Good morning"

# Custom prompt
trn -t french --prompt "Translate to formal French" "How are you?"

# Translate web article
trn -t german https://news.example.com/article
```

## Requirements

- Python 3.12+
- LLM API keys configured
