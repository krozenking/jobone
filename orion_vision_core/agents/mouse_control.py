import pyautogui

def click(x, y):
    """Belirtilen koordinatlarda tıklama yapar."""
    pyautogui.click(x, y)

def write(text):
    """Belirtilen metni yazar."""
    pyautogui.write(text)

def move_mouse(x, y, duration=0.1):
    """Fareyi belirtilen koordinatlara hareket ettirir."""
    pyautogui.moveTo(x, y, duration=duration)

def drag_mouse(x1, y1, x2, y2, duration=0.1):
    """Fareyi belirtilen koordinatlardan diğerine sürükler."""
    pyautogui.moveTo(x1, y1, duration=duration)
    pyautogui.dragTo(x2, y2, duration=duration, button='left')

if __name__ == '__main__':
    # Örnek kullanım
    # Fareyi (100, 100) koordinatlarına hareket ettir
    move_mouse(100, 100)

    # (100, 100) koordinatına tıkla
    click(100, 100)

    # "Merhaba Dünya" yaz
    write("Merhaba Dünya")

    # Fareyi (200, 200) koordinatlarına sürükle
    # drag_mouse(100, 100, 200, 200)
