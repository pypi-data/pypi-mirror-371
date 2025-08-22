from atikin_env.parser import cast_value

def test_cast_value():
    assert cast_value("true") is True
    assert cast_value("false") is False
    assert cast_value("123") == 123
    assert cast_value("-45") == -45
    assert cast_value("3.14") == 3.14
    assert cast_value("None") is None
    assert cast_value("hello") == "hello"
