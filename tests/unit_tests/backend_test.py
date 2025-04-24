import pytest
import importlib.util
from unittest.mock import patch
from mongo_id_utils import is_valid_object_id


def test_missing_mongo_uri(monkeypatch):
    monkeypatch.delenv("MONGO_URI", raising=False)

    # Path to the actual file
    path = "backend/database.py"
    spec = importlib.util.spec_from_file_location("database", path)
    module = importlib.util.module_from_spec(spec)

    # Patch dotenv *before* the module is executed
    with patch("dotenv.load_dotenv", return_value=None):
        with pytest.raises(ValueError, match="MONGO_URI is not set"):
            spec.loader.exec_module(module)


def test_is_valid_object_id_invalid_collection():
    result = is_valid_object_id("NotACollection", "68094b3267aa3dbf50919a52")
    assert result is False
