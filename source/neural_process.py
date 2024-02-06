from pathlib import Path

import torch
import variables
import whisper
from transformers import pipeline

device = "cuda:0" if torch.cuda.is_available() else "cpu"
torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
# устанавливаем количество потоков для torch
torch.set_num_threads(4)


def sound_to_text(audios: Path) -> tuple[str, str, str]:
    """
    Транскрибирует аудио в текст
        и при необходимости переводит его на английский.

    Args:
    audios (Path): Путь к аудиофайлу.

    Returns:
    tuple[str, str, str]: Транскрибированный текст, переведенный текст и обнаруженный язык.
    """
    # Загружаем предобученную модель
    model = whisper.load_model(variables.MODEL)

    # Загрузка и предварительная обработка аудио
    audio = whisper.load_audio(audios)
    audio = whisper.pad_or_trim(audio)

    # Преобразование аудио в логарифмический мел-спектрограмм
    mel = whisper.log_mel_spectrogram(audio).to(model.device)

    # Определение языка
    _, probs = model.detect_language(mel)
    lang = max(probs, key=probs.get)
    print(f"Detected language: {max(probs, key=probs.get)}")

    # Транскрибируем аудио и переводим в английский при необходимости
    if lang == "en":
        if variables.MODEL == "large":
            result = model.transcribe(audios, fp16=False, language=lang)
        else:
            model_en = whisper.load_model(f"{variables.MODEL}.en")
            result = model_en.transcribe(audios, fp16=False, language=lang)
        result_en = result
    else:
        result = model.transcribe(audios, fp16=False, language=lang)
        result_en = model.transcribe(
            audios, fp16=False, language=lang, task="translate"
        )

    # Возвращаем транскрибированный текст,
    #   переведенный текст и обнаруженный язык
    # return result["segments"], result_en["segments"], lang
    return result, result_en, lang


def final_process(file: Path):
    raw, raw_en, detected_lang = sound_to_text(file)
    translator = pipeline("translation", model="Helsinki-NLP/opus-mt-mul-en")
    translator2 = pipeline("translation", model="Helsinki-NLP/opus-mt-en-ru")
    text = f"Перевод аудиофайла: {file} \n"
    text += f"В файле используется {get_language_name(detected_lang)} язык. \n"
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
    text_Helsinki_NLP = text

    text = f"Перевод аудиофайла: {file} \n"
    text += f"В файле используется {get_language_name(detected_lang)} язык. \n"
    text += "-------------------- \n"
    text += f"Исходный текст:{raw['text']} \n"
    text += "-------------------- \n"
    text += f"Английский (Whisper_NLP):{raw_en['text']} \n"
    text_Whisper_NLP = text

    return text_Helsinki_NLP, text_Whisper_NLP


def get_language_name(code: str) -> str:
    """
    Возвращает название языка, соответствующего указанному коду.

    Параметры:
    code (str): Код языка для поиска.

    Возвращает:
    str: Название соответствующего языка или "неизвестный язык", если код не найден.
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
