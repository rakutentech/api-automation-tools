import json
import os
from glob import iglob


def safe_mkdirs(path: str):
    """
    This makes new directories if needed.

    Args:
        path: The full path of the would be directory.
    """
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)


def make_json(
    content: dict, path: str, append: bool = False, ensure_ascii: bool = False
):
    """
    This writes a dictionary to a json file.

    Args:
        content: The content to write.
        path: The path to write to.
        append: Whether to append data to an existing json.
        ensure_ascii: Whether to contain ASCII characters.
    """
    if append and os.path.exists(path):
        stored_json = load_json(path)
        content = {**stored_json, **content}

    safe_mkdirs("/".join(path.split("/")[:-1]))
    with open(path, "w") as fp:
        json.dump(content, fp, indent=4, ensure_ascii=ensure_ascii)


def load_json(path: str) -> dict:
    """
    This reads and loads json into python from a file.

    Args:
        path: The path to read from.

    Returns:
        data: The json data.
    """
    if not os.path.exists(path):
        return {}
    with open(path) as fp:
        return json.load(fp)


def find_reference_in_list(name: str, references: list) -> str:
    """
    This finds the matching reference (file path) in a list of references.

    Args:
        name: The name of the file to look for.
        references: The list of references to look through for a match.

    Returns:
        reference: The matching reference from the list.
    """
    return next((ref for ref in references if name == ref.split("/")[-1]), 0)


def get_root_dir(root_checks: None | list[str] = None) -> str:
    """
    This gets the root directory by looking for ['.lock', 'tests', 'Pipfile', 'Poetry'].

    Args:
        root_checks: The things to check for to identify the project's root directory.

    Returns:
        root_dir: The root dir of the project.
    """
    root_checks = root_checks or []
    root_checks += [
        ".git",
        "pytest.ini",
        "poetry.lock",
        "Pipfile.lock",
        "pyproject.toml",
        "Pipfile",
    ]

    cwd = os.getcwd().split("/")
    for i in range(len(cwd), -1, -1):
        path = "/".join(cwd[:i])
        if path:
            list_dir = os.listdir(path)
            if os.path.isdir(path) and any(i in list_dir for i in root_checks):
                return path


def get_src_app_dir() -> str:
    """
    This finds which src app directory (app, map, ..) we're automating against.

    Returns:
        app: The src app/project folder in use.
    """
    path = os.environ.get("PYTEST_CURRENT_TEST", "").split("::")[0]
    path = path or os.getcwd().replace(f"{get_root_dir()}/", "")
    return path.split("/")[1]


def expand_directory(path: str) -> list:
    """
    This expands a directory into a list of its files absolute paths.

    Args:
        path: The path of the directory to traverse.

    Returns:
        files: The list of files in a directory.
    """
    files = [path]
    if os.path.isdir(path):
        files = [
            f
            for f in iglob(f"{path}//**", recursive=True)
            if "ds_store" not in f.lower()
        ]
    return files
