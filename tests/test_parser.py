import pytest

@pytest.mark.parametrize(
    "line, parsed",
    [
        ("ls", ["ls"]),
        ("ls -l ", ["ls", "-l"]),
        ("ls -l 'abc d'", ["ls", "-l", 'abc d']),
        (r"ls     -l       'abc d'   fe\ g    ", ["ls", "-l", 'abc d', "fe g"]),
    ]
)
def test_file_operations_in_temp_dir(session, line: str, parsed: list):
    assert session.shlex_split(line) == parsed

@pytest.mark.parametrize(
    "args, cmd_name_and_args",
    [
        ([], ('', [])),
        (['ls'], ('ls', [])),
        (['ls',  '-l'], ('ls', ['-l'])),
        (['rm', '-r', 'av bc', 'de fg h'], ('rm', ['-r', 'av bc', "de fg h"])),
    ]
)
def test_name_args_parse(session, args, cmd_name_and_args):
    assert session.fetch_name_and_args(args) == cmd_name_and_args

@pytest.mark.parametrize(
    "line, full_parsed",
    [
        ("ls", ("ls", [])),
        ("ls -l ", ("ls", ['-l'])),
        ("ls -l 'abc d'", ("ls", ['-l', 'abc d'])),
        (r"ls -l 'abc d'       ab\ f", ("ls", ['-l', 'abc d', 'ab f'])),
    ]
)
def test_full_parse(session, line, full_parsed):
    assert session.parse_line(line) == full_parsed
