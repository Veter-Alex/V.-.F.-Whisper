"""
Модуль содержит функции операций нейросетей.

Def:
    change_sampling_rate(audio_file) -> Path: Изменяет частоту дискретизации.
    get_the_model_whisper() -> Dict: Возвращает тип модели для Whisper
                в соответствии с директорией расположения файла.
    sound_to_text(file: Path) -> Union[str, None]: Транскрибирует аудио в текст
                и переводит его на английский.
    final_process(file: Path) -> str: Транскрибирует аудиофайл,
                переводит его на английский, а затем на русский.
    get_language_name(code: str) -> str: Возвращает название языка,
                соответствующего указанному коду.
"""

import datetime
from pathlib import Path
from typing import Any, Dict, Tuple, Union
import file_process
import ffmpeg
import logger_settings
import torch
import variables
import whisper
from transformers import pipeline

# Проверяем доступность CUDA и устанавливаем устройство соответственно
device = "cuda:0" if torch.cuda.is_available() else "cpu"
# Устанавливаем тип данных torch в зависимости от доступности CUDA
torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
# устанавливаем количество потоков для torch
torch.set_num_threads(4)


def change_sampling_rate(audio_file: Path) -> Path:
    """
    Функция для изменения частоты дискретизации аудиофайла
    на целевую и сохраняет результирующий файл.

    Parameters:
        audio_file (Path): Путь к входному аудиофайлу.

    Returns:
        Path: Путь к перепробованному аудиофайлу.
    """
    # Загрузка аудиофайла
    stream = ffmpeg.input(audio_file)
    audio = stream.audio
    output_file = Path.joinpath(
        audio_file.parent, f"16KHz_{audio_file.stem}{audio_file.suffix}"
    )
    # stream = ffmpeg.output(
    #     audio, str(output_file), **{"ar": "16000", "acodec": "flac"}
    # )
    stream = ffmpeg.output(
        audio, str(output_file), **{"ac": "1", "ar": "16000"}
    )
    ffmpeg.run(stream, capture_stdout=True, capture_stderr=True)
    audio_file.unlink()
    output_file.rename(audio_file)
    return audio_file


def get_the_model_whisper(file: Union[Path, str]) -> str:
    """
    Получить тип модели для Whisper
        в соответствии с директорией расположения файла.

    Args:
        file (Union[Path, str]): Путь к файлу.

    Returns:
        str: Тип модели.
    """

    # Сопоставление ключевых слов файла с типами моделей
    QUALITY_MAPPING: Dict[str, str] = {
        "tiny (quality = low)": "tiny",
        "base (quality = 2)": "base",
        "small (quality = 3)": "small",
        "medium (quality = 4)": "medium",
        "large (quality = max)": "large",
    }
    # Преобразовать файл в строку, если он является объектом Path
    file_str = str(file) if isinstance(file, Path) else file
    # Вернуть тип модели на основе директории файла
    return next(
        (value for key, value in QUALITY_MAPPING.items() if key in file_str),
        variables.MODEL,
    )


def sound_to_text(audios: Path) -> Tuple[Any, Any, Any, str]:
    """
    Транскрибирует аудио в текст
        и переводит его на английский.

    Args:
    audios (Path): Путь к аудиофайлу.

    Returns:
    tuple[str, str, str]: Транскрибированный текст,
        переведенный на английский транскрибированный текст
        и обнаруженный язык.
    """
    # Загружаем предобученную модель
    model_whisper = get_the_model_whisper(audios)
    model = whisper.load_model(model_whisper)
    # Загрузка и предварительная обработка аудио
    audio = whisper.load_audio(str(audios))
    audio = whisper.pad_or_trim(audio)

    # Преобразование аудио в логарифмический мел-спектрограмм
    n_mels = 128 if model_whisper == "large" else 80
    mel = whisper.log_mel_spectrogram(audio, n_mels=n_mels).to(model.device)

    # Определение языка
    _, probs = model.detect_language(mel)
    lang = max(probs, key=probs.get)

    # Транскрибируем аудио и переводим в английский при необходимости
    if lang == "en":
        model_en = (
            whisper.load_model(f"{model_whisper}.en")
            if model_whisper != "large"
            else model
        )
        result_en = model_en.transcribe(str(audios), fp16=False, language=lang)
        result = ""
    else:
        result = model.transcribe(str(audios), fp16=False, language=lang)
        result_en = model.transcribe(
            str(audios), fp16=False, language=lang, task="translate"
        )

    # Возвращаем транскрибированный текст, переведенный текст,
    # определенный язык и модель whisper
    return result, result_en, lang, model_whisper


def final_process(file: Path) -> str:
    """
    Транскрибирует аудиофайл, переводит его на английский, а затем на русский.

    Args:
        file (Path): Путь к аудиофайлу.

    Returns:
        str: Текст, содержащий транскрибированный текст,
            переводы и детали сегментов.
    """
    time_start = datetime.datetime.now(datetime.timezone.utc)
    # сохраняем временный файл процесса обработки
    file_to_save = Path(Path(file).with_suffix(".proc"))
    if file_to_save.is_file():
        return "during the transcription process ... "
    else:
        file_process.save_text_to_file(
            f"during the transcription process ...\n"
            f"time start {time_start.strftime('%H:%M:%S (UTC) - %d %b %Y')}",
            file_to_save,
        )

    # Транскрибирование аудио в текст, перевод его на английский,
    # определение языка и модели для обработки.
    if variables.CHANGE_SAMPLING_RATE_TO_16KGH:
        file = change_sampling_rate(file)
    raw, raw_en, detected_lang, model_whisper = sound_to_text(file)
    logger_settings.logger.info(f"Используется модель: {model_whisper}")
    logger_settings.logger.info(f"Язык аудиозаписи: {detected_lang}")
    # Переводчик pipeline с английского языка на русский
    translator_en_ru = pipeline(
        "translation", model="Helsinki-NLP/opus-mt-en-ru"
    )
    # Формирование текста
    text = ""
    text_ru = ""  # текст на русском
    text = f"Транскрибирование аудиофайла:\n {file}\n"
    text += f"В файле используется {get_language_name(detected_lang)} язык. \n"
    text += (
        f"Транскрибирование выполнено с помощью "
        f"модели 'Whisper.{model_whisper}' \n"
    )
    # Формирование текста транскрибирования (модели Whisper)
    # и перевода (модели Helsinki-NLP/opus-mt-en-ru)
    if detected_lang != "en":
        text += "-------------------- \n"
        text += f"Исходный текст (Whisper): \n{raw['text']} \n"
    text += "-------------------- \n"
    text += f"Английский (Whisper): \n{raw_en['text']} \n"
    text += "-------------------- \n"
    text += f"Русский (Helsinki-NLP/opus-mt-en-ru): \n"
    for segment in raw_en["segments"]:
        # Перевод текста с английского на русский
        translation_en_ru = translator_en_ru(segment["text"])
        text_ru += translation_en_ru[0]["translation_text"]  # type: ignore
    text += f"{text_ru} \n"

    # Разбор по сегментам текста транскрибирования (модели Whisper)
    # и перевода (модели Helsinki-NLP/opus-mt-en-ru)
    text += "\n" * 2
    text += "Разбор по сегментам. \n"
    text += "-------------------- \n" * 2
    if detected_lang != "en":
        text += "Исходный текст (модель Whisper).\n"
        text += "-------------------- \n"
        for segment in raw["segments"]:
            text += "-------------------- \n"
            text += (
                f"ID элемента: {segment['id']} "
                f"Начало: {int(segment['start'])} --- "
                f"Конец: {int(segment['end'])} \n"
            )
            text += f"Исходный текст:{segment['text']} \n"

    text += "-------------------- \n" * 2
    text += (
        "Английский (модель Whisper) и русский текст (модель Helsinki-NLP).\n"
    )
    text += "-------------------- \n"
    for segment in raw_en["segments"]:
        text += "-------------------- \n"
        text += (
            f"ID элемента: {segment['id']} "
            f"Начало: {int(segment['start'])} --- "
            f"Конец: {int(segment['end'])} \n"
        )
        text += f"Английский текст:{segment['text']} \n"
        translation_en_ru = translator_en_ru(segment["text"])
        text += f"Русский: {translation_en_ru[0]['translation_text']} \n"  # type: ignore

    time_end = datetime.datetime.now(datetime.timezone.utc)
    time_transcrib_file = time_end - time_start
    # Вычисление времени обработки и добавление в итоговый текст
    idx_str = text.index("-----")
    text = (
        f"{text[:idx_str]}"
        f"Время обработки: {time_transcrib_file}\n"
        f"{text[idx_str:]}"
    )
    if Path(Path(file).with_suffix(".proc")).is_file():
        Path(Path(file).with_suffix(".proc")).unlink()
    return text


def get_language_name(code: str) -> str:
    """
    Возвращает название языка, соответствующего указанному коду.

    Параметры:
    code (str): Код языка для поиска.

    Возвращает:
    str: Название соответствующего языка
            или "неизвестный язык", если код не найден.
    """
    languages = {
        "ru": "русский",
        "en": "английский",
        "zh": "китайский",
        "es": "испанский",
        "ar": "арабский",
        "he": "иврит",
        "hi": "хинди",
        "bn": "бенгальский",
        "pt": "португальский",
        "fr": "французский",
        "de": "немецкий",
        "ja": "японский",
        "pa": "панджаби",
        "jv": "яванский",
        "te": "телугу",
        "ms": "малайский",
        "ko": "корейский",
        "vi": "вьетнамский",
        "ta": "тамильский",
        "it": "итальянский",
        "tr": "турецкий",
        "uk": "украинский",
        "pl": "польский",
        "ca": "каталонский",
        "nl": "голландский",
        "sv": "шведский",
        "id": "индонезийский",
        "fi": "финский",
        "el": "греческий",
        "cs": "чешский",
        "ro": "румынский",
        "da": "датский",
        "hu": "венгерский",
        "no": "норвежский",
        "th": "тайский",
        "ur": "урду",
        "hr": "хорватский",
        "bg": "болгарский",
        "lt": "литовский",
        "la": "латынь",
        "mi": "маори",
        "ml": "малаялам",
        "cy": "валлийский",
        "sk": "словацкий",
        "fa": "персидский",
        "lv": "латышский",
        "sr": "сербский",
        "az": "азербайджанский",
        "sl": "словенский",
        "kn": "каннада",
        "et": "эстонский",
        "mk": "македонский",
        "br": "бретонский",
        "eu": "баскский",
        "is": "исландский",
        "hy": "армянский",
        "ne": "непальский",
        "mn": "монгольский",
        "bs": "боснийский",
        "kk": "казахский",
        "sq": "албанский",
        "sw": "суахили",
        "gl": "галисийский",
        "mr": "маратхи",
        "si": "сингальский",
        "km": "кхмерский",
        "sn": "шона",
        "yo": "йоруба",
        "so": "сомалийский",
        "af": "африкаанс",
        "oc": "окситанский",
        "ka": "грузинский",
        "be": "белорусский",
        "tg": "таджикский",
        "sd": "синдхи",
        "gu": "гуджарати",
        "am": "амхарский",
        "yi": "идиш",
        "lo": "лаосский",
        "uz": "узбекский",
        "fo": "фарерский",
        "ht": "гаитянский креольский",
        "ps": "пашто",
        "tk": "туркменский",
        "nn": "нюношк",
        "mt": "мальтийский",
        "sa": "санскрит",
        "lb": "люксембургский",
        "my": "мьянманский",
        "bo": "тибетский",
        "tl": "тагальский",
        "mg": "малагасийский",
        "as": "ассамский",
        "tt": "татарский",
        "haw": "гавайский",
        "ln": "лингала",
        "ha": "хауса",
        "ba": "башкирский",
        "jw": "яванский",
        "su": "сунданский",
        "yue": "кантонский",
    }
    return languages.get(code, "неизвестный язык")
