"""Defines useful CLI commands."""

from pathlib import Path

import typer
from openai import AzureOpenAI
from pyprojroot import here

from mat_llm_cli.__version__ import __version__ as VERSION
from mat_llm_cli.utils import compose_release_notes

app = typer.Typer()


@app.command()
def write_release_notes(
    endpoint: str,
    api_key: str,
    api_version: str,
    release_notes_dir: Path = Path("./docs/releases"),
):
    """Write release notes for the latest two tags to the release notes directory.

    :param release_notes_dir: The directory to write the release notes to.
        Defaults to "./docs/releases".
    """
    try:
        import git
    except ImportError:
        raise ImportError(
            "git is not installed. Please install it with `pip install llamabot[cli]`."
        )

    repo = git.Repo(here())
    tags = sorted(repo.tags, key=lambda t: t.commit.committed_datetime)
    if len(tags) == 0:
        # No tags, get all commit messages from the very first commit
        log_info = repo.git.log()
        latest_tag = VERSION
    elif len(tags) == 1:
        # Only one tag, get all commit messages from that tag to the current commit
        tag = tags[0]
        log_info = repo.git.log(f"{tag.commit.hexsha}..HEAD")
        latest_tag = tag.name
    else:
        # More than one tag, get all commit messages between the last two tags
        tag1, tag2 = tags[-2], tags[-1]
        log_info = repo.git.log(f"{tag1.commit.hexsha}..{tag2.commit.hexsha}")
        latest_tag = tag2.name

    client = AzureOpenAI(
        azure_endpoint=endpoint,
        api_key=api_key,
        api_version=api_version,
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": compose_release_notes(log_info)}],
    )

    notes = response.choices[0].message.content

    # Create release_notes_dir if it doesn't exist:
    release_notes_dir.mkdir(parents=True, exist_ok=True)
    # Ensure only one newline at the end of the file
    trimmed_notes = notes.rstrip() + "\n"

    # Write release notes to the file
    with open(release_notes_dir / f"{latest_tag}.md", "w+") as f:
        f.write(trimmed_notes)
