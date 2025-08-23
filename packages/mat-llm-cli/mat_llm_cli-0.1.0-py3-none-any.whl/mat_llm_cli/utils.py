"""Utils function."""


def compose_release_notes(commit_log: str) -> str:
    """
    Compose release notes from the commit log.
    """
    return f"""Here is a commit log:

    # noqa: DAR101

    {commit_log}

    Please write for me the release notes.
    The notes should contain a human-readable summary
    of each new feature that was added.

    Follow the following format:

        ---START---
        <brief summary of the new version>

        ### New Features

        - <describe in plain English> (<commit's first 6 letters>) (<commit author>)
        - <describe in plain English> (<commit's first 6 letters>) (<commit author>)

        ### Bug Fixes

        - <describe in plain English> (<commit's first 6 letters>) (<commit author>)

        ### Deprecations

        - <describe in plain English> (<commit's first 6 letters>) (<commit author>)
        ---FINISH---
    """
