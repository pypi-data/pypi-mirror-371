# git_utils.py
import subprocess

def get_staged_diff():
    result = subprocess.run(
        ["git", "diff", "--cached"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    
    if result.returncode != 0:
        raise RuntimeError(f"Git error: {result.stderr.strip()}")
    
    return result.stdout.strip()