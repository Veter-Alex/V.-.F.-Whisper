from pathlib import Path

import file_process
import logger_settings
import neural_process
import variables
from dotenv import load_dotenv

dotenv_path = f"{Path((__file__)).parent.parent}/.env"
if Path(dotenv_path).is_file():
    load_dotenv(dotenv_path)


def main():
    # Получаем список аудиофайлов из указанного пути.
    file_list = file_process.get_audio_file(variables.DIR_SOUND_IN)
    logger_settings.logger.info(f"Всего аудиофайлов: {len(file_list)}")

    # проверяем файл на длительность
    file_list = [
        file
        for file in file_list
        if file_process.file_duration_check(file) < variables.DURATION_LIMIT
    ]
    logger_settings.logger.info(
        f"Всего аудиофайлов, подлежащих обработке: {len(file_list)}"
    )

    # Транскрибируем каждый аудиофайл из списка
    for file in file_list:
        # Транскрибируем аудиофайл
        logger_settings.logger.info(f"Транскрибирование аудиофайла\n {file} ...")
        trans_text_helsinki, trans_text_whisper = neural_process.final_process(file)

        # сохраняем результаты в текстовые файлы
        file_to_save = Path(
            variables.DIR_SOUND_OUT,
            f"{Path(file).stem}_(model:{variables.MODEL}, NLP:helsinki).txt",
        )
        file_process.save_text_to_file(trans_text_helsinki, file_to_save)

        file_to_save = Path(
            variables.DIR_SOUND_OUT,
            f"{Path(file).stem}_(model:{variables.MODEL}, NLP:whisper).txt",
        )
        file_process.save_text_to_file(trans_text_whisper, file_to_save)


    logger_settings.logger.info("Все аудиофайлы обработаны.")


if __name__ == "__main__":
    main()
