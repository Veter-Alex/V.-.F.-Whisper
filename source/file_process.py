"""
Модуль содержит функции файловых операций.

Def:
    delete_file(file_path) -> None : Удаляет файл по указанному file_path.
    check_temp_folders_for_other_model(temp_path) -> None : Создает директории
                    для выбора модели обработки.
    get_files(path, extensions) -> list: Возвращает список аудиофайлов
                    в указанной директории с указанными расширениями.
    check_file_must_trascrib(file_list) -> list: Возвращает список аудиофайлов,
                    подлежащих обработке.
    save_text_to_file(text, file_path) -> None: Сохраняет текст
                    в указанный файл.
    file_duration(file_path) -> float: Возвращает длительность аудиофайла
                    в секундах.
"""

from pathlib import Path
from typing import Union

import logger_settings
import variables
from pydub import AudioSegment


def delete_file(file_path: Union[str, Path]) -> None:
    """
    Удаляет указанный файл.

    Args:
        file_path : Union[str, Path]: Путь к файлу, который нужно удалить.

    Returns:
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


def check_temp_folders_for_other_model(temp_path: Union[str, Path]) -> None:
    """
    Создает директории для выбора модели обработки.

    Args:
        temp_path: Путь к временной папке.

    Returns:
        None
    """
    temp_path = Path(temp_path)
    Path.joinpath(temp_path, "tiny (quality = low)").mkdir(
        parents=True, exist_ok=True
    )
    Path.joinpath(temp_path, "base (quality = 2)").mkdir(
        parents=True, exist_ok=True
    )
    Path.joinpath(temp_path, "small (quality = 3)").mkdir(
        parents=True, exist_ok=True
    )
    Path.joinpath(temp_path, "medium (quality = 4)").mkdir(
        parents=True, exist_ok=True
    )
    Path.joinpath(temp_path, "large (quality = max)").mkdir(
        parents=True, exist_ok=True
    )
    Path.joinpath(temp_path, "readme.txt")
    with Path.joinpath(temp_path, "readme.txt").open("w") as f:
        f.write(
            "Директории (tiny, base, small, medium, large) предназначены "
            "для выбора модели обработки (качества обработки). "
            "Более качественная модель лучше выполнит транскрибирование "
            "и перевод, но затратит на это больше времени. "
            "Для обработки с помощь конкретной модели нужно поместить "
            "аудиофайлы (*.mp3, *.mp4, *.ogg, *.wav, *.webm) "
            "в соответствующую директорию. Внутри директорий "
            "можно создавать любую удобную структуру папок. "
            "Файлы с транскрибированным и переведенным текстом будут помещены "
            "в директорию с аудиофайлом с тем же именем и расширением txt.\n\n"
            "Аудиофайлы в корне входной директории (можно создавать любую "
            "удобную структуру папок) будут обработаны с помощью модели "
            "по умолчанию, указанной в настройках программы."
        )


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


def check_file_must_trascrib(file: Union[str, Path]) -> bool:
    """
    Функция для проверки файла, подлежащего обработке.

    Args:
        file: Union[str, Path]:  Объект Path,
                    представляющий файлы для проверки.

    Returns:
        bool: Возвращает True, если файл прошел проверку
    """
    file = Path(file)
    # проверка наличия аудиофайла
    if not file.is_file():
        logger_settings.logger.debug(f"Файл не найден. {file}")
        return False
    # проверяем наличие текстового фала с транскрибированием
    elif file.with_suffix(".txt").is_file():
        logger_settings.logger.debug(f"Файл уже обработан.\n {file}")
        return False
    # проверяем, что длительность аудиофайла меньше заданного лимита
    duration = file_duration_check(file)
    if duration > variables.DURATION_LIMIT:
        logger_settings.logger.debug(
            f"Длительность аудиофайла {file} "
            f"превышает установленный лимит.\n"
        )
        return False
    # если не удалось получить длительность аудиофайла
    elif duration == 0:  # битый аудиофайл
        logger_settings.logger.debug(
            f"Не удалось получить длительность аудиофайла. {file}"
        )
        return False
    else:
        # файл для обработки
        logger_settings.logger.debug(f"Файл для обработки\n {file}")
        return True


def save_text_to_file(
    trans_eng_text: str, path_out: Path = variables.DIR_SOUND_IN
) -> None:
    """
    Сохраняет переведенный английский текст в текстовый файл.

    Args:
        trans_eng_text (str): Переведенный английский текст,
                    который нужно сохранить.
        path_out (Path, optional): Путь к выходному каталогу.

    Returns:
        None
    """

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
        sound.duration_seconds = len(sound) / 1000.0
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
