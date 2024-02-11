"""
Модуль содержит статические переменные, которые настраивают
    приложение на моменте запуска.
"""

import os
from os import getenv
from pathlib import Path
from sys import exit

# from file_process import check_dir_sound_in_and_mount
import draw
import logger_settings
from dotenv import load_dotenv


os.system("clear")
draw.draw_picture(f"{Path(__file__).parent.parent}/images/logo.png")
print("\n" * 2)
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
    # TODO вывести путь файла логирования
    # logger_settings.logger.info(f"Путь логфайла: {logger_settings.log_path}")

# Переменные для работы приложения
if (
    getenv("DIR_SOUND_IN") is None
    or not Path(getenv("DIR_SOUND_IN")).is_dir()
):
    exit(
        "Входная директория, содержащяя звуковые файлы"
        " НЕ ЗАДАНА или НЕ ДОСТУПНА.\n"
        "Error: DIR_SOUND_IN is None"
    )
else:
    DIR_SOUND_IN = getenv("DIR_SOUND_IN")
    """ Входная директория с файлами, содержащими звуковые файлы
        и текстовый файл с результатами обработки """
    logger_settings.logger.info(f"Входная директория: {DIR_SOUND_IN}")

# TODO реализовать проверки через регулярные выражения
EXTENSIONS = getenv("EXTENSIONS", "*.*").split(", ")


if getenv("DURATION_LIMIT") is None:
    exit(
        "Максимальная длительность звукового файла в секундах НЕ ЗАДАНА.\n"
        "Error: DURATION_LIMIT is None"
    )
else:
    DURATION_LIMIT = float(getenv("DURATION_LIMIT", "600"))
    """ Максимальная длительность звукового файла в секундах """
    logger_settings.logger.info(
        f"Максимальная длительность звукового файла в секундах: "
        f"{DURATION_LIMIT}"
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
    exit("Модель не задана или задана некорректно.\n Error: MODEL is None")
else:
    MODEL = getenv("MODEL")
    """ Модель whisper """
    logger_settings.logger.info(f"Модель whisper: {MODEL}")
