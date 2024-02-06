from pathlib import Path

from PIL import Image


def draw_picture(picture: str):
    # Открываем изображение
    img = Image.open(picture)

    # Масштабируем изображение до нужного размера
    width, height = img.size
    aspect_ratio = height / width
    new_width = 100
    # Преобразуем результат в целое число
    new_height = int(aspect_ratio * new_width * 0.5)
    img = img.resize((new_width, new_height))

    # Преобразуем изображение в псевдографику и выводим его
    pixels = img.getdata()
    ascii_str = "@%#*+=-:. "

    ascii_img = ""
    for pixel_value in pixels:
        # Используем среднее значение из RGB для оттенков серого
        brightness = sum(pixel_value) / 3
        # Вычисляем индекс символа ASCII
        ascii_index = int(brightness / 25.5)
        # Обеспечиваем, чтобы индекс не выходил за границы массива
        ascii_img += ascii_str[min(ascii_index, len(ascii_str) - 1)]
        if len(ascii_img) == new_width:
            print(ascii_img)
            ascii_img = ""


if __name__ == "__main__":
    draw_picture(f"{Path(__file__).parent.parent}/images/logo.jpg")
