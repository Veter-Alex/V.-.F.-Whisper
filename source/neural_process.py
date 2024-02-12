from pathlib import Path
import datetime
import torch
import variables
import whisper
from transformers import pipeline

device = "cuda:0" if torch.cuda.is_available() else "cpu"
torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
# устанавливаем количество потоков для torch
torch.set_num_threads(4)


def get_the_model_whisper(file : Path) -> str:
    if "tiny (quality = low)" in str(file):
        return "tiny"
    elif "base (quality = 2)" in str(file):
        return "base"
    elif "small (quality = 3)" in str(file):
        return "small"
    elif "medium (quality = 4)" in str(file):
        return "medium"
    elif "large (quality = max)" in str(file):
        return "large"
    else:
        return variables.MODEL


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
        if model_whisper == "large":
            result_en = model.transcribe(
                str(audios), fp16=False, language=lang
            )
        else:
            model_en = whisper.load_model(f"{model_whisper}.en")
            result_en = model_en.transcribe(
                str(audios), fp16=False, language=lang
            )
        result = result_en
    else:
        result = model.transcribe(str(audios), fp16=False, language=lang)
        result_en = model.transcribe(
            str(audios), fp16=False, language=lang, task="translate"
        )

    # Возвращаем транскрибированный текст,
    #   переведенный текст и обнаруженный язык
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
    time_start = time_start = datetime.datetime.now(datetime.timezone.utc)
    raw, raw_en, detected_lang, model_whisper = sound_to_text(file)
    translator = pipeline("translation", model="Helsinki-NLP/opus-mt-mul-en")
    translator2 = pipeline("translation", model="Helsinki-NLP/opus-mt-en-ru")
    text = ""
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
    time_end = datetime.datetime.now(datetime.timezone.utc)
    time_transcrib_file = time_end - time_start
    text += f"Whisper отработал {time_transcrib_file} \n"

    text += "-------------------- \n"
    text_en = raw_en["text"]
    max_length = len(text_en) + 5
    # TODO Разбить текст на блоки не болеее 512 символов
    translation2 = translator2(text_en, max_length=max_length)
    text += f"Русский (Helsinki-NLP/opus-mt-en-ru): \n"
    text += f"{translation2[0]['translation_text']} \n"

    # Разбор по сегментам текста транскрибирования (модели Whisper)
    # и перевода (модели Helsinki-NLP/opus-mt-en-ru)
    text += "\n"
    text += "-------------------- \n" * 2
    text += "Разбор по сегментам. \n"
    text += "Исходный текст (Whisper). \n"
    text += "Английский и русский (Helsinki-NLP) . \n"

    for segment in raw["segments"]:
        text += "-------------------- \n"
        text += f"ID элемента: {segment['id']} Начало: {int(segment['start'])} --- Конец: {int(segment['end'])} \n"
        text += f"Исходный текст:{segment['text']} \n"
        if detected_lang == "en":
            text_en = segment["text"]
            translation2 = translator2(text_en)
            text += f"Русский: {translation2[0]['translation_text']} \n"
        elif detected_lang == "ru":
            text += ""
        else:
            translation = translator(segment["text"])
            text += f"Английский: {translation[0]['translation_text']} \n"
            text_en = translation[0]["translation_text"]
            translation2 = translator2(text_en)
            text += f"Русский: {translation2[0]['translation_text']} \n"
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
