import types
import botbolt

def test_imports():
    assert isinstance(botbolt.__version__, str)
    assert callable(botbolt.embed)

def test_bot_init():
    # Uses a fake token; we just ensure the constructor doesn't raise.
    b = botbolt.Bot(token="x"*10, prefix="!", intents="minimal")
    assert hasattr(b, "run")
