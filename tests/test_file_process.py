import pytest
from pathlib import Path
from unittest.mock import patch
from file_process import delete_file


# Assuming logger_settings.logger is a Loguru logger instance
# Mocking logger to avoid actual logging during tests
@pytest.fixture
def mock_logger(mocker):
    with patch("logger_settings.logger") as mock_logger:
        yield mock_logger


# Happy path tests with various realistic test values
@pytest.mark.parametrize(
    "file_path, test_id",
    [
        (
            "/home/alex/project/transcrib/source/existing_file.txt",
            "existing_file",
        ),
        (
            Path("/home/alex/project/transcrib/source/existing_file.txt"),
            "existing_path_object",
        ),
    ],
    ids=lambda test_id: f"happy_path_{test_id}",
)
def test_delete_file_happy_path(tmp_path, file_path, test_id, mock_logger):
    # Arrange
    file_to_delete = tmp_path / file_path
    file_to_delete.touch()  # Create the file

    # Act
    delete_file(file_to_delete)

    # Assert
    assert not file_to_delete.exists()
    mock_logger.info.assert_called_with(
        f"Файл {file_to_delete} успешно удален."
    )


# Edge cases
@pytest.mark.parametrize(
    "file_path, test_id",
    [
        ("", "empty_string"),
        (".", "current_directory"),
        (
            "non_existing_path/non_existing_file.txt",
            "non_existing_nested_file",
        ),
    ],
    ids=lambda test_id: f"edge_case_{test_id}",
)
def test_delete_file_edge_cases(tmp_path, file_path, test_id, mock_logger):
    # Arrange
    if test_id != "empty_string":
        file_path = tmp_path / file_path

    # Act
    delete_file(file_path)

    # Assert
    if test_id == "empty_string":
        mock_logger.info.assert_called_with(f"Файл {file_path} не найден.")
    else:
        mock_logger.info.assert_called_with(
            f"Произошла ошибка при удалении файла {file_path}: [Errno 2] No such file or directory: '{file_path}'"
        )


# Error cases
@pytest.mark.parametrize(
    "file_path, test_id",
    [
        (
            "/home/alex/project/transcrib/source/readonly_file.txt",
            "readonly_file",
        ),
    ],
    ids=lambda test_id: f"error_case_{test_id}",
)
def test_delete_file_error_cases(tmp_path, file_path, test_id, mock_logger):
    # Arrange
    file_to_delete = tmp_path / file_path
    file_to_delete.touch()
    file_to_delete.chmod(0o444)  # Make the file read-only

    # Act
    delete_file(file_to_delete)

    # Assert
    assert file_to_delete.exists()
    mock_logger.info.assert_called_with(
        f"Произошла ошибка при удалении файла {file_to_delete}: [Errno 13] Permission denied: '{file_to_delete}'"
    )
