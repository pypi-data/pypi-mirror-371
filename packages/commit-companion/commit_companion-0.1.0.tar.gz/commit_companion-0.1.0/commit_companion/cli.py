# cli.py
import click
from git_utils import get_staged_diff
from ai_utils import generate_commit_message
import os

@click.group(
    help="""
💬 Commit Companion: Smarter Git Commit Messages with GPT

Use `suggest` to generate a commit message from staged Git changes.
Use `install-hook` to automatically generate commit messages on each commit.

Examples:
  commit-companion suggest --tone casual
  commit-companion install-hook
"""
)
def cli():
    pass

@cli.command(
    help="""
Generate a commit message from staged Git changes.

Options:
  --tone TEXT     Commit tone (neutral, casual, formal, funny, etc.)
  --type TEXT     Conventional prefix (feat, fix, docs, chore, etc.)
  --auto          Skip confirmation prompt (for Git hook use)

Examples:
  commit-companion suggest --tone casual --type feat
  commit-companion suggest --auto --type fix
"""
)
@click.option('--tone', default='neutral', help='Commit tone (neutral, casual, formal, funny, etc.)')
@click.option('--type', default=None, help='Conventional prefix: feat, fix, docs, chore, etc.')
@click.option('--auto', is_flag=True, help='Skip confirmation prompt (for Git hook use)')
def suggest(tone, type, auto):
    diff = get_staged_diff()
    if not diff:
        click.echo("⚠️ No staged changes found.")
        return

    message = generate_commit_message(diff, tone)
    if type:
        message = f"{type}: {message[0].lower() + message[1:]}"
    
    if not auto:
        click.echo("\n✅ Suggested Commit Message:\n")
        click.echo(message)
        confirm = input("\nUse this message? [Y/n]: ").strip().lower()
        if confirm not in ["", "y", "yes"]:
            click.echo("❌ Commit canceled.")
            return
    
    print(message)

@cli.command(
    help="""
Install Commit Companion as a Git hook in the current repo.

Automatically generates a commit message using GPT for each `git commit`.

To uninstall, delete `.git/hooks/prepare-commit-msg`.
"""
)
def install_hook():
    hook_path = os.path.join(".git", "hooks", "prepare-commit-msg")
    script = """#!/bin/bash
TYPE=${TYPE:-feat}
TONE=${TONE:-neutral}
commit-companion suggest --tone "$TONE" --type "$TYPE" --auto > .git/COMMIT_EDITMSG
"""
    try:
        with open(hook_path, "w") as f:
            f.write(script)
        os.chmod(hook_path, 0o755)
        click.echo("✅ Git hook installed successfully.")
    except Exception as e:
        click.echo(f"❌ Failed to install hook: {e}")

@cli.command(
    help="""
Uninstall Commit Companion Git hook from the current repo.

Removes the `prepare-commit-msg` file created by the install-hook command.
"""
)
def uninstall_hook():
    hook_path = os.path.join(".git", "hooks", "prepare-commit-msg")
    try:
        if os.path.exists(hook_path):
            os.remove(hook_path)
            click.echo("🗑️ Git hook uninstalled successfully.")
        else:
            click.echo("ℹ️ No hook found to uninstall.")
    except Exception as e:
        click.echo(f"❌ Failed to uninstall hook: {e}")