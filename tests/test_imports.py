def test_imports():
    import ma_debate
    from ma_debate.cli import app
    assert app is not None
