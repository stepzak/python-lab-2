import pathlib as pl

import pytest


def test_ls_basic(session_with_file_structure):
    session, temp_dir, structure = session_with_file_structure

    result = session.execute_command("ls")
    for filename in structure.keys():
        assert filename in result.stdout
    assert "dir1" in result.stdout
    assert "dir2" in result.stdout

def test_ls_directory(session_with_file_structure):
    session, temp_dir, structure = session_with_file_structure

    result = session.execute_command("ls dir1")
    assert 'file' in result.stdout

def test_cd_absolute_path(session_with_file_structure):
    session, temp_dir, structure = session_with_file_structure
    path = f"{temp_dir}/dir1"
    result = session.execute_command(f"cd {path}")
    assert pl.Path(path) == pl.Path.cwd()
    assert result.errcode == 0

def test_cd_relative_path(session_with_file_structure):
    session, temp_dir, structure = session_with_file_structure

    result = session.execute_command("cd dir1")
    assert result.errcode == 0

    result = session.execute_command("cd ..")
    assert result.errcode == 0

def test_cd_nonexistent(session_with_file_structure):
    session, temp_dir, structure = session_with_file_structure

    file = "fhgjdfg"
    res = session.execute_command(f"cd {file}")
    assert res.errcode != 0
    assert file in res.stderr

def test_cat_basic(session_with_file_structure):
    session, temp_dir, structure = session_with_file_structure

    result = session.execute_command("cat file1.txt")
    assert "Hello World" in result.stdout
    assert "This is test file" in result.stdout

def test_cat_multiple_files(session_with_file_structure):
    session, temp_dir, structure = session_with_file_structure

    result = session.execute_command("cat file1.txt file2.txt")
    assert "Hello World" in result.stdout
    assert "Another file" in result.stdout

def test_cat_nonexistent(session_with_file_structure):
    session, temp_dir, structure = session_with_file_structure
    f = "jgjeogkdgsdnaf.txt"
    result = session.execute_command(f"cat {f}")
    assert f in result.stderr
