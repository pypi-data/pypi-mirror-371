import re
import math
import sys
import subprocess
from typing import List


PATTERNS = {
    "AWS Access Key ID": r"AKIA[0-9A-Z]{12,20}",
    "GitHub Token": r"gh[pousr]_[A-Za-z0-9]{36}",
    "Slack Token": r"xox[baprs]-[A-Za-z0-9-]{10,48}",
    "Generic URI with credentials": r"[a-zA-Z][a-zA-Z0-9+.-]*:\/\/[^:\s]+:[^@\s]+@[^\/\s]+",
}

CANDIDATE_PATTERNS = [
    (re.compile(r"[A-Za-z0-9+/=]{20,}"), 4.2, "base64ish"),
    (re.compile(r"\b[0-9a-fA-F]{32,}\b"), 3.2, "hexish"),
]

seen = set()


def get_staged_files() -> List[str]:
    """
    Get the list of staged files in the Git repository.

    Uses `git diff --cached --name-only -z` to retrieve all files staged
    for commit, separated by null characters.

    Returns:
        List[str]: A list of staged file paths as UTF-8 strings.
    """

    out = subprocess.check_output(
        ["git", "diff", "--cached", "--name-only", "-z"], text=False
    )

    return [p.decode("utf-8") for p in out.split(b"\x00") if p ]


def read_staged_files(path: str) -> str:
    """
    Read the contents of a staged file.

    Uses `git show :<path>` to fetch the staged version of the file.

    Args:
        path (str): Path of the file to read from the Git index.

    Returns:
        str: The file contents as a string. Returns an empty string
             if the file cannot be read (e.g., if it was deleted).
    """

    try:
        return subprocess.check_output(["git", "show", f":{path}"], text=True, errors="ignore")
    
    except subprocess.CalledProcessError:
        return ""


def shannon_entropy(s: str) -> float:
    """
    Calculate Shannon entropy of a string.
    Entropy measures how 'unpredictable' or 'random' the string is.
    Higher entropy = more random.
    Lower entropy = more predictable.
    """

    if not s:
        return 0.0

    freq = {}
    for ch in s:
        freq[ch] = freq.get(ch, 0) + 1

    length = len(s)
    entropy = 0.0

    # Apply Shannon's entropy formula:
    # H = -Σ (p * log2(p)), where p = frequency / length
    for count in freq.values():
        propability = count / length
        entropy += propability * math.log2(propability)

    return -entropy


def scan_entropy(path: str, content: str) -> List[dict]:
    """"""
    findings = []

    for i, line in enumerate(content.splitlines(), start=1):
        for patt, threshold, label in CANDIDATE_PATTERNS:
            for match in patt.findall(line):
                H = shannon_entropy(match)
                if H >= threshold:
                    #if re.search(r"(?i)(key|secret|token|password|auth|api|password)", line):
                        if line.strip() not in seen:
                            findings.append({
                                "file": path,
                                "line": i,
                                "rule_id": f"entropy_{label}",
                                "match": match,
                                "entropy": H,
                                "context": line.strip()
                            })
    
    return findings


def scan_content(path: str, content: str) -> List[dict]:
    """
    Scan a file’s content for sensitive patterns (e.g., tokens, keys).

    Iterates through all predefined regex patterns and checks for matches.

    Args:
        path (str): The file path being scanned.
        content (str): The file content to scan.

    Returns:
        List[tuple]: A list of tuples (file_path, pattern_name, match_value)
                     for each detected secret.
    """

    findings = []

    for name, pattern in PATTERNS.items():
        for i, line in enumerate(content.splitlines(), start=1):
            for match in re.finditer(pattern, line):
                findings.append({
                    "file": path,
                    "line": i,
                    "rule_id": name,
                    "match": match.group(0),
                    "context": line.strip()
                })
                seen.add(line.strip())
    entropy_issues = scan_entropy(path, content)
    findings.extend(entropy_issues)
            

    return findings


def scan_repo() -> List[dict]:
    """
    Scan all staged files in the repository for sensitive information.

    Retrieves the list of staged files, reads their staged contents,
    and applies secret-detection patterns.

    Returns:
        List[tuple]: A list of findings where each entry is
                     (file_path, pattern_name, match_value).
    """
    files = get_staged_files()
    all_findings = []

    for f in files:
        content = read_staged_files(f)
        all_findings.extend(scan_content(f,content))

    return all_findings