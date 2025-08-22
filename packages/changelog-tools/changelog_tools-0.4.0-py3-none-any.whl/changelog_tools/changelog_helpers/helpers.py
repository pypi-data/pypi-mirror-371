import re
from pathlib import Path
from typing import List


def sanitize_changelog_path(changelog_path: Path) -> Path:
    """
    Check that the given path points to a valid file and if a file named CHANGELOG.md exists in the given directory.

    :param Path changelog_path: Path of the changelog we want to extract parts.
    :return: A valid changelog path.
    """

    if not changelog_path.is_file():
        changelog_path = changelog_path / "CHANGELOG.md"

    if not changelog_path.is_file():
        raise FileNotFoundError(f"The changelog file {changelog_path} doesn't exist.")

    return changelog_path


def read_changelog_path(changelog_path: Path) -> List[str]:
    """
    Open and read a changelog path.

    :param Path changelog_path: Path of the changelog we want to extract parts.
    :return: A splited changelog file.
    """

    changelog_file = changelog_path.read_text()

    return changelog_file.split("\n")


def get_version_line_pattern(changelog_format: str = "markdown") -> str:
    """
    :return: Version line pattern depending on changelog file format.
    """

    if changelog_format == "markdown":
        return r"^## \[(.+)\]"


def get_version_pattern(version: str) -> str:
    """
    Use a provided version to create a pattern to help finding version number in a changelog file.

    :return: Version pattern.
    """

    return rf"^## \[{re.escape(version)}\]"


def _get_version_helper(changelog_path: Path | str, include_unreleased: bool = False, get_initial: bool = False) -> str:
    """
    Find and return current version of a changelog file.

    :param Path | str changelog_path: Path of the changelog we want to extract parts.
    :param bool include_unreleased: If set to True, Unreleased section will be taken into account.
    :param bool get_initial: If set to True, return value will be the initial version of the provided changelog file.
    :return: Latest version of the provided changelog file.
    :raises RuntimeError: If the file doesn't contain any version line.
    """

    path = sanitize_changelog_path(Path(changelog_path))

    changelog_file = read_changelog_path(path)

    if get_initial:
        changelog_file = reversed(changelog_file)

    for line in changelog_file:
        current_version = re.search(get_version_line_pattern(), line)

        # If current_version isn't found or we found Unreleased section we continue, unless include_unreleased is set to True
        if current_version is None or (current_version.group(1) == "Unreleased" and not include_unreleased):
            continue
        return current_version.group(1)
    # If no version has been found, we throw an error.
    raise RuntimeError("Couldn't find a version line in the file")


def get_latest_version(changelog_path: Path | str, include_unreleased: bool = False) -> str:
    """
    :param Path | str changelog_path: Path of the changelog we want to extract parts.
    :param bool include_unreleased: If set to True, Unreleased section will be taken into account.
    :return: Latest version of a changelog file.
    """

    return _get_version_helper(changelog_path, include_unreleased)


def get_initial_version(changelog_path: Path | str, include_unreleased: bool = False) -> str:
    """
    :param Path | str changelog_path: Path of the changelog we want to extract parts.
    :param bool include_unreleased: If set to True, Unreleased section will be taken into account.
    :return: Initial version of a changelog file.
    """

    return _get_version_helper(changelog_path, include_unreleased, True)


def is_version_in_changelog(changelog_path: Path | str, version: str) -> bool:
    """
    Check if given version exists in the given changelog file.

    :param Path | str changelog_path: Path of the changelog we want to extract parts.
    :return: True if the provided version number exists, otherwise return False.
    """

    changelog_file = read_changelog_path(Path(changelog_path))

    for line in changelog_file:
        if re.search(rf"^## \[{version}]", line) is None:
            continue
        return True

    return False


def is_version_line(line: str) -> bool:
    """
    Check if the line is a line that contains a version.

    :return: True if the line contains a version, otherwise return False.
    """

    if line.startswith("## ["):
        return True

    return False


def is_section_line(line: str) -> bool:
    """
    Check if the line is a section heading.

    :return: True if the line is a heading, otherwise return False.
    """

    if line.startswith("###"):
        return True

    return False
