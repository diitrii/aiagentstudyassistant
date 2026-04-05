from pathlib import Path

import pytesseract
from PIL import Image, ImageFilter, ImageOps


pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Users\FRDS\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"
)


def crop_to_main_content(image: Image.Image) -> Image.Image:
    width, height = image.size

    left = int(width * 0.12)
    right = int(width * 0.88)
    top = int(height * 0.16)
    bottom = int(height * 0.88)

    return image.crop((left, top, right, bottom))


def preprocess_image_for_ocr(image: Image.Image) -> Image.Image:
    image = crop_to_main_content(image)
    image = image.convert("L")
    image = ImageOps.autocontrast(image)
    image = image.resize(
        (image.width * 2, image.height * 2),
        Image.Resampling.LANCZOS,
    )
    image = image.filter(ImageFilter.SHARPEN)
    image = image.point(lambda p: 255 if p > 165 else 0)
    return image


def extract_text_from_image(image_path: Path) -> str:
    try:
        image = Image.open(image_path)
        processed = preprocess_image_for_ocr(image)

        text = pytesseract.image_to_string(
            processed,
            config="--oem 3 --psm 6",
        )

        if not text:
            return ""

        return text.strip()
    except Exception:
        return ""