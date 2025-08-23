# main.py
import click
from git_utils import get_staged_diff
from ai_utils import generate_commit_message

@click.command()
@click.option('--tone', default='neutral', help='Tone of the commit message: neutral, casual, formal, etc.')
@click.option('--type', default=None, help='Conventional commit type: feat, fix, docs, etc.')
@click.option('--auto', is_flag=True, help='Auto mode: skip confirmation (for Git hooks)')
def main(tone, type, auto):
    diff = get_staged_diff()
    if not diff:
        click.echo("⚠️ No staged changes found. Please stage your changes first.")
        return

    message = generate_commit_message(diff, tone)

    if type:
        message = f"{type}: {message[0].lower() + message[1:]}"  # lowercase first char after type

    if not auto:
        click.echo("\n✅ Suggested Commit Message:\n")
        click.echo(message)
        confirm = input("\nUse this commit message? [Y/n]: ").strip().lower()
        if confirm not in ["", "y", "yes"]:
            click.echo("❌ Commit message canceled.")
            return

    print(message)

if __name__ == "__main__":
    main()