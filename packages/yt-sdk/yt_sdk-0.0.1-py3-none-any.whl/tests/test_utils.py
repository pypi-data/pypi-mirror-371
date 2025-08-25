from yt_sdk.url import url2youtube_id


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
