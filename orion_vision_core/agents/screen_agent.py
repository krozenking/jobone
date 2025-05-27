import cv2
import numpy as np
import pytesseract
import mss
import mss.tools
import easyocr

def capture_screenshot(region=None):
    """Ekran görüntüsü alır."""
    with mss.mss() as sct:
        if region:
            monitor = {"top": region[1], "left": region[0], "width": region[2], "height": region[3]}
        else:
            monitor = sct.monitors[1]  # Birincil ekran

        sct_img = sct.grab(monitor)
        return np.array(sct_img)

def perform_ocr(image):
    """Görüntü üzerinde OCR gerçekleştirir."""
    # gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) # EasyOCR renkli resimleri de destekler
    # text = pytesseract.image_to_string(gray, lang='tur')
    reader = easyocr.Reader(['tr'], gpu=False) # GPU kullanmak için gpu=True yapın
    results = reader.readtext(image)
    text = ""
    for (bbox, text_val, prob) in results:
        text += text_val + " "
    return text

def find_ui_elements(image, template_path):
    """Görüntüde UI öğelerini bulur."""
    template = cv2.imread(template_path, 0)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    w, h = template.shape[::-1]

    res = cv2.matchTemplate(gray_image, template, cv2.TM_CCOEFF_NORMED)
    threshold = 0.8
    loc = np.where(res >= threshold)

    ui_elements = []
    for pt in zip(*loc[::-1]):
        ui_elements.append((pt[0], pt[1], w, h))  # x, y, width, height

    return ui_elements

if __name__ == '__main__':
    # Örnek kullanım
    screenshot = capture_screenshot()
    text = perform_ocr(screenshot)
    print("Ekran görüntüsündeki metin:", text)

    # UI öğesi bulma (örnek)
    # ui_elements = find_ui_elements(screenshot, 'template.png') # template.png dosyasının yolunu belirtin
    # print("Bulunan UI öğeleri:", ui_elements)
    # cv2.imshow('Screenshot', screenshot)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
