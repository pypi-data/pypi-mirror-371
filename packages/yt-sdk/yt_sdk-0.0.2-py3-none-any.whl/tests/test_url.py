from yt_sdk.url import url2youtube_id, is_valid_youtube_id


def test_url2youtube_id_for_real_cases():
    # Casos válidos
    assert url2youtube_id(url="https://www.youtube.com/watch?v=dQw4w9WgXcQ") == "dQw4w9WgXcQ"
    assert url2youtube_id(url="http://youtube.com/watch?v=abcdEFG1234") == "abcdEFG1234"
    assert url2youtube_id(url="https://www.youtube.com/embed/abcdEFG1234") == "abcdEFG1234"
    assert url2youtube_id(url="https://www.youtube.com/v/abcdEFG1234") == "abcdEFG1234"
    assert url2youtube_id(url="https://www.youtube.com/watch?v=abcdEFG1234&t=42s") == "abcdEFG1234"

    # Casos inválidos
    assert url2youtube_id(url="https://www.google.com/watch?v=dQw4w9WgXcQ") is None
    assert url2youtube_id(url="https://youtube.com/") is None
    assert url2youtube_id(url="https://www.youtube.com/watch?v=short") is None
    assert url2youtube_id(url="") is None
    assert url2youtube_id(url="https://www.youtube.com/watch?v=") is None
    assert url2youtube_id(url="https://www.youtube.com/watch?v=dQw4w9WgXcQextra") is None


def test_is_valid_youtube_id_various_cases():
    # Casos válidos
    assert is_valid_youtube_id(youtube_id="dQw4w9WgXcQ") is True
    assert is_valid_youtube_id(youtube_id="abcdEFG1234") is True
    assert is_valid_youtube_id(youtube_id="A1B2C3D4E5F") is True
    assert is_valid_youtube_id(youtube_id="a_b-C_dE1F2") is True

    # Casos inválidos
    assert is_valid_youtube_id(youtube_id="short") is False        # demasiado corto
    assert is_valid_youtube_id(youtube_id="toolong1234567") is False  # demasiado largo
    assert is_valid_youtube_id(youtube_id="invalid$id!!") is False  # caracteres no permitidos
    assert is_valid_youtube_id(youtube_id=" ") is False            # espacio
    assert is_valid_youtube_id(youtube_id="") is False             # vacío
    assert is_valid_youtube_id(youtube_id="abcdefghijk ") is False # espacio al final
    assert is_valid_youtube_id(youtube_id="1234567890-") is True   # guion permitido
    assert is_valid_youtube_id(youtube_id=None) is False           # None
    assert is_valid_youtube_id(youtube_id=12345678901) is False    # número en lugar de string
