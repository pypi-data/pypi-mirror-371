import logging
import pytest

logging.basicConfig(level="INFO")

@pytest.fixture
def youtube_id_real() -> str:
    return "5ViMA_qDKTU"
