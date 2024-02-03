import file_process
import torch
import whisper
from transformers import pipeline
import variables
from pathlib import Path

device = "cuda:0" if torch.cuda.is_available() else "cpu"
torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
# устанавливаем количество потоков для torch
torch.set_num_threads(4)


def sound_to_text(audios):
    model = whisper.load_model(variables.MODEL)
    # load audio and pad/trim it to fit 30 seconds
    audio = whisper.load_audio(audios)
    audio = whisper.pad_or_trim(audio)
    # make log-Mel spectrogram and move to the same device as the model
    mel = whisper.log_mel_spectrogram(audio).to(model.device)
    # detect the spoken language
    _, probs = model.detect_language(mel)
    lang = max(probs, key=probs.get)
    print(f"Detected language: {max(probs, key=probs.get)}")
    # транскрибируем аудио
    result = model.transcribe(audios, fp16=False, language=lang)
    # транскрибируем аудио и переводим в английский
    if lang == "en":
        result_en = result
    else:
        result_en = model.transcribe(
            audios, fp16=False, language=lang, task="translate"
        )
    # print(result)
    return result["segments"], result_en["segments"], lang


def final_process(file: Path):
    print(f"Сохранен в директории: {file}")
    raw, raw_en, detected_lang = sound_to_text(file)
    translator = pipeline("translation", model="Helsinki-NLP/opus-mt-mul-en")
    translator2 = pipeline("translation", model="Helsinki-NLP/opus-mt-en-ru")
    text = f"Перевод аудиофайла: {file} \n"
    text += f"В файле используется {get_language_name(detected_lang)} язык. \n"
    for segment in raw:
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
    print(text)
    return text


def get_language_name(code):
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
    }
    return languages.get(code, "неизвестный язык")
