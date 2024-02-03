from pathlib import Path

import logger_settings
import variables
from pydub import AudioSegment


def delete_file(file_path):
    """
    Удаляет файл по указанному file_path.

    Аргументы:
        file_path (str): Путь к файлу, который нужно удалить.

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


def get_audio_file(path_in: Path = variables.DIR_SOUND_IN) -> list[str]:
    """
    Получает список аудиофайлов из указанного пути.

    Аргументы:
        path_in (Path, опционально): Входной путь для поиска аудиофайлов.
                        По умолчанию variables.DIR_SOUND_IN.

    Возвращает:
        list[str]: Список путей к аудиофайлам.
    """
    file_list = []
    files = sorted(Path(path_in).rglob("*.wav"))
    for file in list(map(str, files)):
        file_txt = f"{file.split('.')[0]}.txt"
        if Path(file_txt).is_file():
            logger_settings.logger.debug(f"Файл уже обработан.\n {file}")
        else:
            logger_settings.logger.debug(f"Файл для обработки\n {file}")
            file_list.append(file)
    return file_list


def save_text_to_file(trans_eng_text: str, path_out: Path = variables.DIR_SOUND_OUT):
    # Сохраняем вывод в текстовый файл
    with open(path_out, "w", encoding="utf-8") as output_file:
        output_file.write(trans_eng_text)


def file_duration_check(file: str) -> float:
    """
    Проверяет длительность данного файла и возвращает длительность в секундах.
    Если файл не может быть обработан, возвращает предел длительности, определенный в модуле переменных.

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
        return variables.DURATION_LIMIT
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
