"""
Модуль выполняет конвертирование и распаковку
нестандартных форматов аудиофайлов
с помощью программы Riffer2 под Wine

Def:
    Voice7000Converter(audio_file: Path) -> Path:
"""

from pathlib import Path
import subprocess

import file_process
import logger_settings


def convert_to_wav(in_dir: Path, list_ext: list = ["*.pak"]):
    """
    Функция выполняет конвертирование
    нестандартных форматов аудиофайлов
    с помощью программы Voice7000Converter.exe (Riffer2) под Wine.

    Parameters:
        in_dir (Path): Путь к входной директории для поиска файлов.
        list_ext (list): Расширения файлов для конвертирования
                        (по умолчанию *.pak)

    Returns:
        None
    """
    file_list = file_process.get_files(in_dir, list_ext)
    logger_settings.logger.info(f"Найдено аудиофайлов pak: {len(file_list)}")
    for file in file_list:
        try:
            outputfile = str(Path(file).with_suffix(".wav"))
            command = f"wine ~/riffer2/Voice7000Converter.exe -i {str(file)} -o {outputfile}"
            subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            ).communicate()
            logger_settings.logger.info(
                f"Файл: {file} конвертирован в {outputfile}"
            )
        except BaseException:
            logger_settings.logger.info(
                f"Ошибка конвертирования файла: {file}"
            )
