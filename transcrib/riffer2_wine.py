"""
Модуль выполняет конвертирование и распаковку
нестандартных форматов аудиофайлов
с помощью программы Riffer2 под Wine

Def:
    Voice7000Converter(audio_file: Path) -> Path:
    unPAK(audio_file: Path) -> Path:
"""
from pathlib import Path


def Voice7000Converter(audio_file: Path) -> Path:
    """
    Функция выполняет конвертирование
    нестандартных форматов аудиофайлов
    с помощью программы Riffer2 под Wine
    и сохраняет результирующий файл.

    Parameters:
        audio_file (Path): Путь к входному аудиофайлу.

    Returns:
        Path: Путь к перепробованному аудиофайлу.
    """
    pass


def unPAK(audio_file: Path) -> Path:
    """
    Функция выполняет распаковку файлов *.pak
    с помощью программы Riffer2 под Wine
    и сохраняет результирующий файл.

    Parameters:
        audio_file (Path): Путь к входному аудиофайлу.

    Returns:
        Path: Путь к перепробованному аудиофайлу.
    """
    pass
