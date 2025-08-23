# Commit Companion

[![PyPI version](https://img.shields.io/pypi/v/commit-companion.svg)](https://pypi.org/project/commit-companion/)
[![GitHub release](https://img.shields.io/github/v/release/nelson-zack/commit-companion)](https://github.com/nelson-zack/commit-companion/releases)

[![Downloads](https://static.pepy.tech/badge/commit-companion)](https://pepy.tech/project/commit-companion)
[![Python Version](https://img.shields.io/pypi/pyversions/commit_companion)](https://pypi.org/project/commit-companion/)

[![License](https://img.shields.io/github/license/nelson-zack/commit-companion)](LICENSE)

**AI-powered Git commit assistant that summarizes staged changes using GPT.**  
Save time, stay in flow, and write better commit messages — automatically.

---

## Features

- Uses GPT to summarize your staged diffs into clear commit messages
- Supports [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/)
- Tone customization (`neutral`, `casual`, `formal`, `funny`, etc.)
- Git hook integration via `prepare-commit-msg`
- Supports environment variables for default `TYPE` and `TONE`
- Optional auto mode to skip confirmation (for non-interactive use)

---

## Quick Start

### 1. Install via pip (recommended):

```bash
pip install commit-companion
```

Or, to install from source:

```bash
git clone https://github.com/nelson-zack/commit-companion.git
cd commit-companion
pip install .
```

### 2. Add your OpenAI API key:

Commit Companion requires access to the OpenAI API. You can provide your key in one of two ways:

#### Option 1: `.env` file (for local use)

```bash
OPENAI_API_KEY=sk-...
```

#### Option 2: Environment variable (for global use)

Add to your shell config (`~/.zshrc`, `~/.bashrc`, etc):

```bash
export OPENAI_API_KEY="sk-..."
```

Then run:

```bash
source ~/.zshrc   # or ~/.bashrc
```

### 3. Install CLI tool locally:

```bash
pip install --editable .
```

## Requirements

- Python 3.8 or later
- An OpenAI API key (required for GPT functionality)

## Usage

### CLI (manual):

```bash
commit-companion suggest --tone casual --type feat
```

Will output something like:

```bash
feat: add basic functionality to README.md
```

Example usage:

```bash
git add <file>
commit-companion suggest --tone casual --type feat
git commit -m "your message here"
git push
```

### Git Hook (auto):

Install the Git hook with:

```bash
commit-companion install-hook
```

This creates a .git/hooks/prepare-commit-msg script that auto-generates commit messages using GPT.
By default, it uses --tone neutral and --type feat.

#### Once installed, your flow becomes:

```bash
git add <file>      # Stage your changes
git commit          # Commit Companion will auto-suggest the message
git push            # Push to remote
```

#### Customize per commit:

Override tone or type like this:

```bash
TYPE=fix git commit
TONE=funny git commit
TYPE=fix TONE=funny git commit
```

Uninstall the hook:

```bash
commit-companion uninstall-hook
```

### Optional: Global Installation

To use commit-companion from any repo without activating a virtual environment:

#### 1. Install globally:

```bash
pip install .
```

#### 2. Add your OpenAI key to your shell config (~/.zshrc or ~/.bashrc):

```bash
export OPENAI_API_KEY="sk-..."
```

#### 3. Ensure your Python bin path is on your system PATH:

```bash
export PATH="$PATH:/Library/Frameworks/Python.framework/Versions/3.12/bin"
```

#### 4. Reload your shell:

```bash
source ~/.zshrc   # or ~/.bashrc
```

#### 5. Use it anywhere:

```bash
commit-companion install-hook
```

## Roadmap Ideas

- Config file support (.commitcompanion.json)
- VS Code extension
- Web version / hosted API
- ✅ PyPI distribution (available via `pip install commit-companion`)

## Why Use This?

Writing commit messages breaks flow. Commit Companion helps you:

- Stay focused on your code
- Standardize commits with no effort
- Impress your teammates with clear, consistent commit messages

## License

MIT License.

## Contributing

Contributions, suggestions, and issue reports are welcome! To get started:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/my-feature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin feature/my-feature`)
5. Open a pull request

## Links

- 📦 [PyPI Package](https://pypi.org/project/commit-companion/)
- 🛠 [GitHub Repository](https://github.com/nelson-zack/commit-companion)
- 📝 [Release Notes](https://github.com/nelson-zack/commit-companion/releases)
