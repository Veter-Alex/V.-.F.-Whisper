import time
from pathlib import Path

import file_process
import logger_settings
import neural_process
import riffer2_wine
import variables
from dotenv import load_dotenv

dotenv_path = f"{Path((__file__)).parent.parent}/.env"
if Path(dotenv_path).is_file():
    load_dotenv(dotenv_path)


def main() -> None:
    while True:
        # riffer2_wine.convert_other_type_audiofiles(variables.DIR_SOUND_IN)

        file_process.check_temp_folders_for_other_model(variables.DIR_SOUND_IN)
        # Получаем список аудиофайлов из указанного пути.
        file_list = file_process.get_files(
            Path(variables.DIR_SOUND_IN), list(variables.EXTENSIONS)
        )
        logger_settings.logger.info(f"Найдено аудиофайлов: {len(file_list)}")

        # Транскрибируем каждый аудиофайл из списка
        for file in file_list:
            if file_process.check_file_must_trascrib(file):
                # Транскрибируем аудиофайл
                print("\n")
                logger_settings.logger.info(
                    f"Транскрибирование аудиофайла\n {file}"
                )
                trans_text = neural_process.final_process(file)
                if trans_text == "during the transcription process ... ":
                    logger_settings.logger.warning(
                        f"Файл:\n {file}\n в процессе обработки или необходимо"
                        f" удалить временный файл (имя файла).proc.\n"
                    )
                else:
                    # сохраняем результат в текстовый файл
                    file_to_save = Path(Path(file).with_suffix(".txt"))
                    file_process.save_text_to_file(trans_text, file_to_save)

        logger_settings.logger.info(
            "Все аудиофайлы в текущем цикле программы обработаны.\n"
        )
        time.sleep(10)


if __name__ == "__main__":
    main()
