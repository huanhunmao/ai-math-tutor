try:
    from paddleocr import PaddleOCR
except Exception as error:
    PaddleOCR = None
    _ocr_import_error = error
else:
    _ocr_import_error = None

_ocr = None


def get_ocr():
    global _ocr
    if PaddleOCR is None:
        raise RuntimeError(
            f"OCR 依赖未安装或当前环境不支持：{_ocr_import_error}"
        )
    if _ocr is None:
        _ocr = PaddleOCR(use_angle_cls=True, lang="ch")
    return _ocr


def extract_text_from_image(image_path: str) -> str:
    result = get_ocr().ocr(image_path, cls=True)

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
