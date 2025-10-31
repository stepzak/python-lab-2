import pathlib

import pytest
import tempfile
import shutil
import os
from src.command_line_session import CommandLineSession


@pytest.fixture
def temp_dir():
    """Tmp dir"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    if pathlib.Path(temp_dir).exists():
        shutil.rmtree(temp_dir)


@pytest.fixture
def session():
    """Command Line Session"""
    s = CommandLineSession()
    s.load_modules()
    return s


@pytest.fixture
def session_in_temp_dir(temp_dir, session):
    """Command line session in tmp dir"""
    session.execute_command(f"cd {temp_dir}")
    return session, temp_dir


@pytest.fixture
def session_with_file_structure(temp_dir, session):
    """Session with some file structure in it"""
    structure = {
        "file1.txt": "Hello World\nThis is test file\nAnother line",
        "file2.txt": "Another file\nWith some content\nHello again",
        "empty.txt": "",
    }

    for filename, content in structure.items():
        filepath = os.path.join(temp_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

    os.makedirs(os.path.join(temp_dir, "dir1"))

    with open(os.path.join(temp_dir, "dir1", "file"), "w", encoding='utf-8') as f:
        f.write("")

    os.makedirs(os.path.join(temp_dir, "dir2/subdir"))


    session.execute_command(f"cd {temp_dir}")
    return session, temp_dir, structure
