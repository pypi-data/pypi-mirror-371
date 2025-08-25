import okkie

def test_simple_word():
    assert okkie.to_okkie("Hello", concat=True) == "Hokkie2lokkielokkie4"

def test_sentence():
    result = okkie.to_okkie("Hello world", concat=False)
    assert "Hokkie" in result
    assert "wokkie" in result
    assert "2" in result  # 'e' → 2

def test_music():
    assert okkie.to_okkie("music", concat=True) == "mokkie5sokkie3sokkie"

def test_programming():
    result = okkie.to_okkie("programming", concat=True)
    assert "pokkierokkie4gokkie" in result
    assert "mokkiemokkie3nokkie" in result

def test_non_letters():
    assert okkie.to_okkie("123!", concat=True) == "123!"
