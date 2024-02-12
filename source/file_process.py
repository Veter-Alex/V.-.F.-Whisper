"""Модуль содержит функции файловых операций.

Def:
    delete_file(file_path) -> None : Удаляет файл по указанному file_path.

Returns:
    _type_: _description_
    """

from pathlib import Path
import os
import logger_settings
import variables
from pydub import AudioSegment
from typing import Optional, Union


def delete_file(file_path: Union[str, Path]) -> None:
    """
    Удаляет указанный файл.

    Аргументы:
        file_path : Union[str, Path]: Путь к файлу, который нужно удалить.

    Возвращает:
        None
    """
    try:
        Path(file_path).unlink()
        logger_settings.logger.info(f"Файл {file_path} успешно удален.")
    except FileNotFoundError:
        logger_settings.logger.info(f"Файл {file_path} не найден.")
    except Exception as e:
        logger_settings.logger.info(
            f"Произошла ошибка при удалении файла {file_path}: {e}"
        )


def check_temp_folders_for_other_model(
    temp_path: Paht = varibles.DIR_SOUND_IN,
) -> None:
    temp_folders = [
        Path.joinpath(Path(__file__).parent.parent, "tiny"),
        Path.joinpath(Path(__file__).parent.parent, "base"),
        Path.joinpath(Path(__file__).parent.parent, "small"),
        Path.joinpath(Path(__file__).parent.parent, "medium"),
        Path.joinpath(Path(__file__).parent.parent, "large"),
    ]
    for temp_folder in temp_folders:
        pass


def get_files(path_in: Path, extensions: list[str] = ["*.*"]) -> list[Path]:
    """
    Получает список файлов из указанного пути, c указанными расширениями.

    Аргументы:
        path_in (Path, опционально): Входной путь для поиска аудиофайлов.
        extensions (list, опционально): Расширения для поиска аудиофайлов.
    Возвращает:
        list[str]: Список путей к файлам.
    """
    all_files: list[Path] = []
    for ext in extensions:
        all_files.extend(Path(path_in).rglob(ext))
    return all_files


def check_files_must_trascrib(all_files: list[Path]) -> list[Path]:
    files_must_trascrib: list[Path] = []
    for file in all_files:
        # проверяем наличие текстового фала с транскрибированием
        if file.with_suffix(".txt").is_file():
            logger_settings.logger.debug(f"Файл уже обработан.\n {file}")

        # проверяем, что длительность аудиофайла меньше заданного лимита
        elif file_duration_check(file) > variables.DURATION_LIMIT:
            logger_settings.logger.debug(
                f"Длительность аудиофайла {file} "
                f"превышает установленный лимит.\n"
            )

        # если не удалось получить длительность аудиофайла
        elif file_duration_check(file) == 0:  # битый аудиофайл
            logger_settings.logger.debug(
                f"Не удалось получить длительность аудиофайла. {file}"
            )

        else:
            # формируем список аудиофайлов для обработки
            files_must_trascrib.append(file)
            logger_settings.logger.debug(f"Файл для обработки\n {file}")

    return files_must_trascrib


def save_text_to_file(
    trans_eng_text: str, path_out: Path = variables.DIR_SOUND_IN
) -> None:
    # Сохраняем вывод в текстовый файл
    with open(path_out, "w", encoding="utf-8") as output_file:
        output_file.write(trans_eng_text)


def file_duration_check(file: Path) -> float:
    """
    Проверяет длительность данного файла и возвращает длительность в секундах.
    Если файл не может быть обработан, возвращает предел длительности,
        определенный в модуле переменных.

    Args:
        file (str): Путь к проверяемому файлу.

    Returns:
        float: Длительность файла в секундах.
    """
    try:
        sound = AudioSegment.from_file(file)
        # перевод длительности в секунды
        sound.duration_seconds == (len(sound) / 1000.0)
    except Exception:
        # Если файл не может быть обработан, возвращает предел длительности,
        #   определенный в модуле переменных.
        return 0
    else:
        # Пересчитываем длительность в минуты и секунды
        minutes_duartion = int(sound.duration_seconds // 60)
        seconds_duration = round((sound.duration_seconds % 60), 1)
        logger_settings.logger.debug(
            f"Длительность файла\n {file}\n"
            f"{minutes_duartion} мин. {seconds_duration} сек."
        )
        # Возвращаем длительность в секундах.
        return sound.duration_seconds
