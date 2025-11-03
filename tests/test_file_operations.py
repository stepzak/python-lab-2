from pathlib import Path
from unittest.mock import patch

def test_rm_basic(session_with_file_structure):
    session, temp_dir, structure = session_with_file_structure

    session.execute_command("rm file1.txt")

    result = session.execute_command("ls")
    assert "file1.txt" not in result.stdout

def test_rm_multiple(session_with_file_structure):
    session, temp_dir, structure = session_with_file_structure

    result = session.execute_command("rm file1.txt file2.txt")
    assert result.errcode == 0

    result = session.execute_command("ls")
    assert "file1.txt" not in result.stdout
    assert "file2.txt" not in result.stdout

def test_rm_dir(session_with_file_structure):
    session, temp_dir, structure = session_with_file_structure
    with patch("builtins.input") as mock_input:
        mock_input.return_value = "y"
        session.execute_command("rm -r dir1")
        result = session.execute_command("ls")
        assert "dir1" not in result.stdout
        assert result.errcode == 0

def test_rm_dir_no(session_with_file_structure):
    session, temp_dir, structure = session_with_file_structure
    with patch("builtins.input") as mock_input:
        mock_input.return_value = 'n'
        session.execute_command("rm -r dir1")
        result = session.execute_command("ls")
        assert "dir1" in result.stdout

def test_rm_parent(session_with_file_structure):
    session, temp_dir, structure = session_with_file_structure
    r_remove = session.execute_command("rm -r ..")
    assert r_remove.errcode != 0
    assert str(Path('..').resolve()) in r_remove.stderr
    result = session.execute_command("ls")
    for file in structure:
        assert file in result.stdout

def test_mv_rename(session_with_file_structure):
    session, temp_dir, structure = session_with_file_structure

    session.execute_command("mv file1.txt renamed.txt")

    result = session.execute_command("ls")
    assert "file1.txt" not in result.stdout
    assert "renamed.txt" in result.stdout
    result = session.execute_command("cat renamed.txt")
    assert "Hello World" in result.stdout

def test_mv_to_directory(session_with_file_structure):
    session, temp_dir, structure = session_with_file_structure

    result = session.execute_command("mv file1.txt dir1/")
    assert result.errcode == 0

    result = session.execute_command("ls dir1/")
    assert "file1.txt" in result.stdout

def test_mv_parent(session_with_file_structure):
    session, temp_dir, structure = session_with_file_structure

    res_mv = session.execute_command("mv .. .")
    assert res_mv.errcode != 0
    assert str(Path('..')) in res_mv.stderr
    result = session.execute_command("ls")

    assert "tmp" not in result.stdout

def test_mv_dir_to_dir(session_with_file_structure):
    session, temp_dir, structure = session_with_file_structure

    session.execute_command("mv dir2 dir1/dir2")
    result = session.execute_command("ls")
    assert "dir2" not in result.stdout

    result = session.execute_command("ls dir1/")

    assert "dir2" in result.stdout

def test_cp_basic(session_with_file_structure):
    session, temp_dir, structure = session_with_file_structure

    result = session.execute_command("cp file1.txt file1_copy.txt")
    assert result.errcode == 0

    result = session.execute_command("ls")
    assert "file1.txt" in result.stdout
    assert "file1_copy.txt" in result.stdout

    result = session.execute_command("cat file1_copy.txt")
    assert "Hello World" in result.stdout

def test_cp_to_directory(session_with_file_structure):
    session, temp_dir, structure = session_with_file_structure

    result = session.execute_command("cp file1.txt dir1/")
    assert result.errcode == 0

    result = session.execute_command("ls dir1/")
    assert "file1.txt" in result.stdout

    result = session.execute_command("ls")
    assert "file1.txt" in result.stdout

def test_cp_dir_to_dir(session_with_file_structure):
    session, temp_dir, structure = session_with_file_structure

    session.execute_command("cp dir2 -r dir1/dir2")

    result = session.execute_command("ls dir1/")
    assert "dir2" in result.stdout
