import pathlib as pl

import pytest


def test_ls_basic(session_with_file_structure):
    session, temp_dir, structure = session_with_file_structure

    result = session.execute_command("ls")
    for filename in structure.keys():
        assert filename in result
    assert "dir1" in result
    assert "dir2" in result

def test_ls_directory(session_with_file_structure):
    session, temp_dir, structure = session_with_file_structure

    result = session.execute_command("ls dir1")
    assert 'file' in result

def test_cd_absolute_path(session_with_file_structure):
    session, temp_dir, structure = session_with_file_structure
    path = f"{temp_dir}/dir1"
    result = session.execute_command(f"cd {path}")
    assert pl.Path(path) == pl.Path.cwd()
    assert not result

def test_cd_relative_path(session_with_file_structure):
    session, temp_dir, structure = session_with_file_structure

    result = session.execute_command("cd dir1")
    assert not result

    result = session.execute_command("cd ..")
    assert not result

def test_cd_nonexistent(session_with_file_structure):
    session, temp_dir, structure = session_with_file_structure

    with pytest.raises(FileNotFoundError):
        cmd = session.cmd_map["cd"].cmd
        cmd(['dsjgfgdjf']).execute()

def test_cat_basic(session_with_file_structure):
    session, temp_dir, structure = session_with_file_structure

    result = session.execute_command("cat file1.txt")
    assert "Hello World" in result
    assert "This is test file" in result

def test_cat_multiple_files(session_with_file_structure):
    session, temp_dir, structure = session_with_file_structure

    result = session.execute_command("cat file1.txt file2.txt")
    print(result)
    assert "Hello World" in result
    assert "Another file" in result

def test_cat_nonexistent(session_with_file_structure):
    session, temp_dir, structure = session_with_file_structure

    result = session.execute_command("cat jgjeogkdgsdnaf.txt")
    assert not result
