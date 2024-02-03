from pathlib import Path
from unittest.mock import MagicMock

import pytest
import wisper_test.logger_settings
import wisper_test.variables
from wisper_test.file_process import get_audio_file

# Mock the logger to avoid actual logging during tests
# logger_settings.logger = MagicMock()

# Test IDs for different scenarios
HAPPY_PATH_ID = "happy_path"
EDGE_CASE_NO_AUDIO_FILES_ID = "edge_case_no_audio_files"
ERROR_CASE_INVALID_PATH_ID = "error_case_invalid_path"

# Sample paths for testing
SAMPLE_DIR = Path("/home/alex/projects/wisper_test/test_audio")
SAMPLE_DIR_EMPTY = Path("/home/alex/projects/wisper_test/test_audio_empty")
NON_EXISTENT_DIR = Path("/home/alex/projects/wisper_test/non_existent_dir")

# Sample audio file names
AUDIO_FILES = ["audio1.wav", "audio2.wav", "audio3.wav"]
PROCESSED_FILES = ["audio1.wav", "audio1.txt", "audio2.wav"]


@pytest.fixture
def setup_audio_files(tmp_path):
    # Arrange: Create a directory with audio files and some already processed (with .txt)
    for audio in AUDIO_FILES:
        (tmp_path / audio).touch()
    for processed in PROCESSED_FILES:
        (tmp_path / processed).touch()
    return tmp_path


@pytest.fixture
def setup_empty_dir(tmp_path):
    # Arrange: Create an empty directory
    return tmp_path


@pytest.fixture
def setup_non_existent_dir():
    # Arrange: Reference a non-existent directory
    return NON_EXISTENT_DIR


@pytest.mark.parametrize(
    "test_input, expected, test_id",
    [
        # Happy path tests with various realistic test values
        (
            pytest.lazy_fixture("setup_audio_files"),
            ["audio3.wav"],
            HAPPY_PATH_ID,
        ),
        # Edge cases
        (
            pytest.lazy_fixture("setup_empty_dir"),
            [],
            EDGE_CASE_NO_AUDIO_FILES_ID,
        ),
        # Error cases
        (
            pytest.lazy_fixture("setup_non_existent_dir"),
            pytest.raises(FileNotFoundError),
            ERROR_CASE_INVALID_PATH_ID,
        ),
    ],
)
def test_get_audio_file(test_input, expected, test_id):
    if test_id == ERROR_CASE_INVALID_PATH_ID:
        # Act & Assert: Verify that a FileNotFoundError is raised for a non-existent path
        with expected:
            get_audio_file(test_input)
    else:
        # Act: Call the function with the test input
        result = get_audio_file(test_input)

        # Assert: Verify the function returns the expected list of audio files
        assert result == expected, f"Test failed for {test_id}"
