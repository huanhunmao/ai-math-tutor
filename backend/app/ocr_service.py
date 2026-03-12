from paddleocr import PaddleOCR
from PIL import Image

ocr = PaddleOCR(use_angle_cls=True, lang="ch")


def extract_text_from_image(image_path: str) -> str:
    result = ocr.ocr(image_path, cls=True)

    lines = []
    for block in result:
        if not block:
            continue
        for item in block:
            if len(item) < 2:
                continue
            text = item[1][0].strip()
            if text:
                lines.append(text)

    return "\n".join(lines)