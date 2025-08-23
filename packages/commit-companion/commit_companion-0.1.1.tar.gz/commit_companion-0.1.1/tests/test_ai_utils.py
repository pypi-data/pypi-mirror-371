from git_utils import get_staged_diff
from ai_utils import generate_commit_message

diff = get_staged_diff()
message = generate_commit_message(diff)
print("\nSuggested Commit Message:\n", message)