from pathlib import Path
import time
import logger_settings
import neural_process
import variables
from dotenv import load_dotenv
import file_process

dotenv_path = f"{Path((__file__)).parent.parent}/.env"
if Path(dotenv_path).is_file():
    load_dotenv(dotenv_path)


def main() -> None:
    working = True
    """Тригер выхода из цикла"""
    cycle = 0
    """ Счетчик циклов выполнения программы"""
    while working:
        file_process.check_temp_folders_for_other_model(
            Path(variables.DIR_SOUND_IN)
        )
        # Получаем список аудиофайлов из указанного пути.
        file_list = file_process.get_files(
            Path(variables.DIR_SOUND_IN), list(variables.EXTENSIONS)
        )
        logger_settings.logger.info(f"Найдено аудиофайлов: {len(file_list)}")

        # Проверяем наличие файлов подлежащих обработке
        if len(file_list) > 0:
            file_list = file_process.check_files_must_trascrib(file_list)
            logger_settings.logger.info(
                f"Всего аудиофайлов, подлежащих обработке: {len(file_list)}"
            )

        # Транскрибируем каждый аудиофайл из списка
        if len(file_list) > 0:
            for file in file_list:
                # Транскрибируем аудиофайл
                logger_settings.logger.info(
                    f"Транскрибирование аудиофайла\n {file}"
                )
                trans_text = neural_process.final_process(file)

                # сохраняем результат в текстовый файл
                file_to_save = Path(Path(file).with_suffix(".txt"))
                file_process.save_text_to_file(trans_text, file_to_save)

        cycle += 1
        logger_settings.logger.debug(f"Закончен цыкл {cycle}")
        logger_settings.logger.info(
            "Все аудиофайлы в текущем цикле программы обработаны.\n"
        )
        time.sleep(10)
    if not working:
        exit("Завершение работы программы по триггеру.")


if __name__ == "__main__":
    main()
