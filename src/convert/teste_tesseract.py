import pytesseract
from PIL import Image
from pathlib import Path

BASE = Path(r"C:\Users\marcelo.lsantos_bhub\AppData\Local\Programs\Tesseract-OCR")

pytesseract.pytesseract.tesseract_cmd = str(BASE / "tesseract.exe")

img = Image.open("logo.png")

texto = pytesseract.image_to_string(
    img,
    lang="por",
    config=f"--tessdata-dir \"{BASE / 'tessdata'}\""
)

print(texto)

