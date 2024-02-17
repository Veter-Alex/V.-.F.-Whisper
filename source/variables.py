"""
Модуль содержит статические переменные, которые настраивают
    приложение на моменте запуска.
"""

import re
import os
from os import getenv
from pathlib import Path
from sys import exit
import draw
import logger_settings
from dotenv import load_dotenv


os.system("clear")
draw.draw_picture(f"{Path(__file__).parent.parent}/images/logo.png")
print("\n")
logger_settings.logger.info("НАЧАЛО РАБОТЫ.".center(35))
logger_settings.logger.info("(настройки из файла '.env' ):".center(35))
dotenv_path = f"{Path((__file__)).parent.parent}/.env"
if Path(dotenv_path).is_file():
    load_dotenv(dotenv_path)

LOG_LEVEL = getenv("LOG_LEVEL", "INFO")
""" Уровень логирования """
if LOG_LEVEL not in [
    "TRACE",
    "DEBUG",
    "INFO",
    "SUCCESS",
    "WARNING",
    "ERROR",
    "CRITICAL",
]:
    exit("Уровень логирования задан некорректно.\n Error: LOG_LEVEL is None")
else:
    logger_settings.configure_logger(LOG_LEVEL)
    logger_settings.logger.info(f"Уровень логирования: {LOG_LEVEL}")
    logger_settings.logger.info(
        f"Путь к лог-файлу: "
        f"{Path.joinpath(Path(__file__).parent.parent, 'logs', f'{Path(__file__).parent.parent.stem}.log')}\n"
    )

# КОНСТАНТЫ ДЛЯ РАБОТЫ ПРИЛОЖЕНИЯ
# Считывание и проверка входной директории с аудиофайлами
if getenv("DIR_SOUND_IN") is None or not Path(getenv("DIR_SOUND_IN")).is_dir():
    exit(
        "Входная директория, содержащая звуковые файлы"
        " НЕ ЗАДАНА или НЕ ДОСТУПНА.\n"
        "Error: DIR_SOUND_IN is None"
    )
else:
    DIR_SOUND_IN = getenv("DIR_SOUND_IN")
    """ Входная директория с файлами, содержащими звуковые файлы
        и текстовый файл с результатами обработки """
    logger_settings.logger.info(
        f"Входная директория с аудиофайлами: {DIR_SOUND_IN}"
    )

# Считывание и проверка списка расширений для поиска аудиофайлов.
extensions = getenv("EXTENSIONS", "*.*").split(", ")
REGEXP_EXT = re.compile(r"^\*?\.[a-zA-Z0-9]+$")
for ext in extensions:
    if not REGEXP_EXT.match(ext):
        extensions.remove(ext)
        logger_settings.logger.debug(f"Расширение {ext} не поддерживается.")
if not extensions:
    EXTENSIONS = ["*.wav"]
    logger_settings.logger.warning(
        "Расширения не заданы или заданы с некорректно. "
        "Значение '*.wav' установлено по умолчанию"
    )
else:
    EXTENSIONS = extensions
logger_settings.logger.info(f"Расширения для поиска аудиофайлов: {EXTENSIONS}")

CHANGE_SAMPLING_RATE_TO_16KGH = getenv(
    "CHANGE_SAMPLING_RATE_TO_16KGH", "False"
).lower() in ("true", "1")

if getenv("DURATION_LIMIT") is None:
    exit(
        "Максимальная длительность звукового файла в секундах НЕ ЗАДАНА.\n"
        "Error: DURATION_LIMIT is None"
    )
else:
    DURATION_LIMIT = float(getenv("DURATION_LIMIT", "600"))
    """ Максимальная длительность звукового файла в секундах """
    logger_settings.logger.info(
        f"Максимальная длительность звукового файла: " f"{DURATION_LIMIT} сек."
    )

if getenv("MODEL") not in [
    "tiny",
    "base",
    "small",
    "medium",
    "large",
    "large-v2",
    "large-v3",
]:
    MODEL = "small"
    logger_settings.logger.warning(
        "Модель whisper не задана или задана с некорректно. "
        "Значение 'small' установлено по умолчанию"
    )
else:
    MODEL = getenv("MODEL")
    logger_settings.logger.info(f"Модель whisper: {MODEL}\n")
