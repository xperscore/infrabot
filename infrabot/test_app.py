from infrabot.utils import parse_release


def test_parse_release():
    assert parse_release("wkpython") == ("wkpython", "latest", "prod")
    assert parse_release("wkpython 4.0") == (
        "wkpython",
        "latest",
        "4.0",
    )  # not valid to release, but parsed correctly
    assert parse_release("wkpython prod") == ("wkpython", "latest", "prod")
    assert parse_release("wkpython cshs") == ("wkpython", "latest", "cshs")
    assert parse_release("wkpython to cshs") == ("wkpython", "latest", "cshs")
    assert parse_release("wkpython to prod") == ("wkpython", "latest", "prod")
    assert parse_release("wkpython 4.0.0 prod") == ("wkpython", "4.0.0", "prod")
    assert parse_release("wkpython 4.0.0 cshs") == ("wkpython", "4.0.0", "cshs")
    assert parse_release("wkpython@4.0.0 prod") == ("wkpython", "4.0.0", "prod")
    assert parse_release("wkpython@4.0.0 cshs") == ("wkpython", "4.0.0", "cshs")
    assert parse_release("wkpython@4.0.0 to prod") == ("wkpython", "4.0.0", "prod")
    assert parse_release("wkpython@4.0.0 to cshs") == ("wkpython", "4.0.0", "cshs")

    assert parse_release("all to prod") == ("all", "latest", "prod")
    assert parse_release("all to cshs") == ("all", "latest", "cshs")

    assert parse_release("all@latest to prod") == ("all", "latest", "prod")
    assert parse_release("all@latest to cshs") == ("all", "latest", "cshs")
