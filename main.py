import os
from tkinter import Tk, filedialog


def read_ppm(filename):
    with open(filename, 'rb') as f:
        magic = f.readline().strip()
        if magic != b'P6':
            raise ValueError("Поддерживается только формат P6 (бинарный PPM)")

        line = f.readline()
        while line.startswith(b'#'):
            line = f.readline()

        width, height = map(int, line.split())
        maxval = int(f.readline().strip())
        if maxval != 255:
            raise ValueError("Поддерживается только максимальное значение 255")

        data = f.read(width * height * 3)
    return width, height, data


def write_ppm(filename, width, height, data):
    with open(filename, 'wb') as f:
        f.write(b'P6\n')
        f.write(f'{width} {height}\n'.encode())
        f.write(b'255\n')
        f.write(data)


def increase_contrast(data):
    pixels = list(data)

    brightness = []
    for i in range(0, len(pixels), 3):
        r, g, b = pixels[i], pixels[i + 1], pixels[i + 2]
        v = 0.2125 * r + 0.7154 * g + 0.0721 * b
        brightness.append(v)

    vmin = min(brightness)
    vmax = max(brightness)
    if vmax == vmin:
        return bytes(pixels)

    k = 255.0 / (vmax - vmin)

    result = []
    for i in range(0, len(pixels), 3):
        r, g, b = pixels[i], pixels[i + 1], pixels[i + 2]
        v = brightness[i // 3]
        vnew = max(0.0, min(255.0, (v - vmin) * k))

        if v > 0:
            ratio = vnew / v
            rnew = int(round(r * ratio))
            gnew = int(round(g * ratio))
            bnew = int(round(b * ratio))
        else:
            rnew = gnew = bnew = int(round(vnew))

        result.extend([
            max(0, min(255, rnew)),
            max(0, min(255, gnew)),
            max(0, min(255, bnew))
        ])
    return bytes(result)


def difference_blend(data1, data2):
    return bytes(abs(a - b) for a, b in zip(data1, data2))


def crop_data(data, width, height, new_w, new_h):
    cropped = bytearray()
    for y in range(new_h):
        start = (y * width) * 3
        end = start + new_w * 3
        cropped.extend(data[start:end])
    return bytes(cropped)


def pick_file(title):
    root = Tk()
    root.withdraw()
    path = filedialog.askopenfilename(
        title=title,
        filetypes=[('PPM images', '*.ppm'), ('All files', '*.*')]
    )
    root.destroy()
    return path if path else None


def pick_save(default_name):
    root = Tk()
    root.withdraw()
    path = filedialog.asksaveasfilename(
        title='Куда сохранить',
        initialfile=default_name,
        defaultextension='.ppm',
        filetypes=[('PPM images', '*.ppm')]
    )
    root.destroy()
    return path if path else None


def main():
    print('=== Лабораторная №5. Вариант 3 ===')
    print('Увеличение контраста + наложение «Разность»')
    print()

    print('Шаг 1. Выберите первое фото')
    file1 = pick_file('Выберите первое фото')
    if not file1:
        print('Отменено.')
        return
    w1, h1, data1 = read_ppm(file1)
    print(f'  Загружено: {os.path.basename(file1)} ({w1}x{h1})')

    print()
    print('Шаг 2. Выберите второе фото')
    file2 = pick_file('Выберите второе фото')
    if not file2:
        print('Отменено.')
        return
    w2, h2, data2 = read_ppm(file2)
    print(f'  Загружено: {os.path.basename(file2)} ({w2}x{h2})')

    print()
    print('Шаг 3. Обработка...')
    contrast_data = increase_contrast(data1)
    print('  Контраст увеличен.')

    w, h = min(w1, w2), min(h1, h2)
    cropped1 = crop_data(contrast_data, w1, h1, w, h)
    cropped2 = crop_data(data2, w2, h2, w, h)
    diff_data = difference_blend(cropped1, cropped2)
    print(f'  Разность получена ({w}x{h}).')

    print()
    print('Шаг 4. Сохранение результатов')
    out1 = pick_save('contrast.ppm')
    if out1:
        write_ppm(out1, w1, h1, contrast_data)
        print(f'  Сохранено: {out1}')

    out2 = pick_save('difference.ppm')
    if out2:
        write_ppm(out2, w, h, diff_data)
        print(f'  Сохранено: {out2}')

    print()
    print('Готово.')


if __name__ == '__main__':
    main()