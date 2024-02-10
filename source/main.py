from pathlib import Path

import logger_settings
import neural_process
import variables
from dotenv import load_dotenv
import file_process

dotenv_path = f"{Path((__file__)).parent.parent}/.env"
if Path(dotenv_path).is_file():
    load_dotenv(dotenv_path)


def main() -> None:
    # Получаем список аудиофайлов из указанного пути.
    file_list = file_process.get_files(
        Path(variables.DIR_SOUND_IN), list(variables.EXTENSIONS)
    )
    logger_settings.logger.info(f"Всего аудиофайлов: {len(file_list)}")

    file_list = file_process.check_files_must_trascrib(file_list)
    logger_settings.logger.info(
        f"Всего аудиофайлов, подлежащих обработке: {len(file_list)}"
    )

    # Транскрибируем каждый аудиофайл из списка
    for file in file_list:
        # Транскрибируем аудиофайл
        logger_settings.logger.info(f"Транскрибирование аудиофайла\n {file}")
        trans_text = neural_process.final_process(file)

        # сохраняем результат в текстовый файл
        file_to_save = Path(
            variables.DIR_SOUND_OUT, Path(file.stem).with_suffix(".txt")
        )
        file_process.save_text_to_file(trans_text, file_to_save)

    logger_settings.logger.info("Все аудиофайлы обработаны.")


if __name__ == "__main__":
    main()
