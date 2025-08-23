import sys
from leaklock.secret_scanner import scan_repo


def main ():
    """
    Handles scan and install commands.
    """
    
    print("Scanning staged files for secrets...")
    issues = scan_repo()

    if issues:
        print("\nPotential secrets found in staged files:\n")
        for issue in issues:
            print(f"[{issue['rule_id']}] {issue['file']}:{issue['line']} -- {issue['match']}")
            if "entropy" in issue:
                print(f"    entropy={issue['entropy']}")
            print(f"    line: {issue['context']}\n")

        sys.exit(1)
        
    else:
        print("No secrets found in staged files")

        sys.exit(0)