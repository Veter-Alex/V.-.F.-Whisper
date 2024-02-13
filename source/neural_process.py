from pathlib import Path
import datetime
import torch
import variables
import whisper
from transformers import pipeline
import librosa
import soundfile
from typing import Dict, Optional, Union

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
    data, sr = librosa.load(audio_file)
    # Изменение частоты дискретизации
    target_sr = 16000  # Целевая частота дискретизации
    resampled_data = librosa.resample(data, orig_sr=sr, target_sr=target_sr)
    # Сохранение результата
    p = Path(audio_file)
    resampled_file = Path.joinpath(p.parent, f"{p.stem}-resampled{p.suffix}")
    soundfile.write(resampled_file, resampled_data, target_sr)
    return Path(resampled_file)


def get_the_model_whisper(file: Union[Path, str]) -> str:
    """Получить тип модели для Whisper
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


def sound_to_text(audios: Path) -> tuple[str, str, str, str]:
    """
    Транскрибирует аудио в текст
        и при необходимости переводит его на английский.

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
    audio = whisper.load_audio(audios)
    audio = whisper.pad_or_trim(audio)

    # Преобразование аудио в логарифмический мел-спектрограмм
    n_mels = 128 if model_whisper == "large" else 80
    mel = whisper.log_mel_spectrogram(audio, n_mels=n_mels).to(model.device)

    # Определение языка
    _, probs = model.detect_language(mel)
    lang = max(probs, key=probs.get)
    print(f"Detected language: {lang}")

    # Транскрибируем аудио и переводим в английский при необходимости
    if lang == "en":
        model_en = (
            whisper.load_model(f"{model_whisper}.en")
            if model_whisper == "large"
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
            переводы и детали сегментов.#### `change_sampling_rate(audio_file: Path) -> Path`
    """
    time_start = time_start = datetime.datetime.now(datetime.timezone.utc)
    # TODO вставить процедуру изменения частоты дискретизации (def change_sampling_rate(audio_file : Path) -> Path:)
    if variables.CHANGE_SAMPLING_RATE_TO_16KGH:
        file = change_sampling_rate(file)
    # Транскрибирование аудио в текст, перевод его на английский,
    # определение языка и модели для обработки.
    raw, raw_en, detected_lang, model_whisper = sound_to_text(file)
    # Переводчик pipeline с английского языка на русский
    translator_en_ru = pipeline(
        "translation", model="Helsinki-NLP/opus-mt-en-ru"
    )
    # Формирование текста
    text = ""
    text_ru = ""  # текст на русском
    text = f"Транскрибирование аудиофайла:\n {file}\n"
    text += f"В файле используется {get_language_name(detected_lang)} язык. \n"
    text += f"Транскрибирование выполнено с помощью модели 'Whisper.{model_whisper}' \n"
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
        text_ru += translation_en_ru[0]["translation_text"]
    text += f"{text_ru} \n"

    # Разбор по сегментам текста транскрибирования (модели Whisper)
    # и перевода (модели Helsinki-NLP/opus-mt-en-ru)
    text += "\n" * 2
    text += "-------------------- \n"
    text += "Разбор по сегментам. \n"
    text += "Исходный текст и английский (модель Whisper).\n"
    text += "русский текст (модель Helsinki-NLP) .\n"
    text += "-------------------- \n"
    if raw == "":
        raw = raw_en
    for i, segment in enumerate(raw["segments"]):
        text += "-------------------- \n"
        text += f"ID элемента: {segment['id']} Начало: {int(segment['start'])} --- Конец: {int(segment['end'])} \n"
        text += f"Исходный текст:{segment['text']} \n"
        if detected_lang == "en":
            translation_en_ru = translator_en_ru(segment["text"])
            text += f"Русский: {translation_en_ru[0]['translation_text']} \n"
        elif detected_lang == "ru":
            text += ""
        else:
            text += f"Английский: {raw_en['segments'][i]['text']} \n"
            # int(str(i).zfill(2))
            translation_en_ru = translator_en_ru(
                raw_en["segments"][i]["text"]
            )
            text += f"Русский: {translation_en_ru[0]['translation_text']} \n"

    time_end = datetime.datetime.now(datetime.timezone.utc)
    time_transcrib_file = time_end - time_start
    # Вычисление времени обработки и добавление в итоговый текст
    idx_str = text.index("-----")
    text = f"{text[:idx_str]}Время обработки: {time_transcrib_file}\n{text[idx_str:]}"

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
