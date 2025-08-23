# LeakLock
**Stop secrets before they reach GitHub.**

LeakLock is a lightweight security tool that **scans your code in real time and blocks commits containing API keys, tokens, or passwords**.  
It integrates with Git via a pre-commit hook, so secrets never leave your machine.

---

## Features
- Scans staged files for common secret patterns (AWS keys, GitHub tokens, Slack tokens, etc.)
- Detects high-entropy strings that may indicate secrets
- Blocks commits automatically when secrets are found
- Works with the pre-commit framework for cross-platform support

---

## Installation
Install from PyPI:

```bash
pip install leaklock
```

Or install from source:

```bash
git clone https://github.com/your-username/leaklock.git
cd leaklock
pip install -e .

```
Install pre-requesties:
```bash
pip install requirements.txt
```

Make sure you have ".pre-commit-config.yaml" file in your repo:
```bash
repos:
  - repo: local
    hooks:
      - id: leaklock
        name: LeakLock secret scanner
        entry: leaklock
        language: python
        types: [file]   # scan all files
        files: ''       # optional: can limit to staged files
```
Install the hook in your repo:

```bash
pre-commit install
```

This adds a Git pre-commit hook.
Make a commit

---

## Usage
Scan files manually:
```bash
leaklock
```

Run on all staged files before commit:
```bash
git add .
git commit -m "test commit"
```
If secrets are found → ❌ commit is blocked with a warning.

If clean → ✅ commit goes through.

🔑 Example Output
```bash
❌ Commit blocked by LeakLock (secrets detected):

- AWS Access Key ID detected in app/config.py:23
- Slack Token detected in utils/slack.py:10

Fix or remove these values before committing.
```

---

## Contributing
Contributions are welcome!
- Fork the repo
- Create a feature branch (git checkout -b feature/new-scan)
- Submit a PR

---

## License
MIT License © 2025 LeakLock Contributors