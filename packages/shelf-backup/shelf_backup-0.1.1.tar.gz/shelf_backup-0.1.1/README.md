<div align="center">

<br>

# 📚 Shelf

### A stupidly simple backup tool

**Single file • Zero dependencies • Auditable • Reliable**

[![PyPI version](https://img.shields.io/pypi/v/shelf-backup.svg)](https://pypi.org/project/shelf-backup/)
[![Python versions](https://img.shields.io/pypi/pyversions/shelf-backup.svg)](https://pypi.org/project/shelf-backup/)
[![Downloads](https://img.shields.io/pypi/dm/shelf-backup.svg)](https://pypi.org/project/shelf-backup/)
[![License](https://img.shields.io/pypi/l/shelf-backup.svg)](https://github.com/rdyv/shelf/blob/main/LICENSE)

[Install](#installation) • [Quick Start](#quick-start) • [Features](#features) • [Documentation](#documentation)

</div>

---

Shelf is a backup tool that gets out of your way. One Python file does everything: backs up your dotfiles, configs, and system state to git-versioned storage with structured logging.

```bash
pip install shelf-backup
shelf init && shelf backup    # That's it.
```

## Quick Start

```bash
# Install
pip install shelf-backup

# Initialize and backup
shelf init
shelf backup

# Restore anytime
shelf restore
```

## Features

<table>
<tr>
<td width="50%">

**Zero Dependencies**
Only Python 3.8+ stdlib required

**Single File**
One auditable Python file

**Git Versioning**
Every backup is a commit

</td>
<td width="50%">

**Auto Detection**
Configures for macOS/Linux automatically

**Structured Logs**
NDJSON logs for every session

**Comprehensive**
Dotfiles, configs, Homebrew, fonts

</td>
</tr>
</table>

## What Gets Backed Up

- **Dotfiles**: `.zshrc`, `.gitconfig`, `.ssh/config`, etc.
- **App Configs**: VSCode, Vim, tmux, git settings
- **System Prefs**: macOS dock, finder, terminal settings
- **Package Managers**: Homebrew formulas and casks
- **Custom Fonts**: Your installed font collection

## Documentation

<details>
<summary><strong>Advanced Commands</strong></summary>

```bash
# Restore from specific commit
shelf restore COMMIT_HASH

# Show backup history
shelf list

# Check system status
shelf status
```

</details>

<details>
<summary><strong>File Locations</strong></summary>

```
~/.config/shelf/           # Configuration files (JSON)
~/.local/share/shelf/      # Backup data (git repositories)
```

</details>

<details>
<summary><strong>Requirements</strong></summary>

- Python 3.8+
- `git` command (for versioning)
- `brew` command (for Homebrew backups on macOS)

No pip packages, no external libraries.

</details>

---

<div align="center">

**[Install Now](https://pypi.org/project/shelf-backup/)** • **[Report Issues](https://github.com/rdyv/shelf/issues)**

_Made for developers who value simplicity_

</div>
