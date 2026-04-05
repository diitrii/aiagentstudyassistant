import pyperclip


def get_clipboard_text() -> str:
    try:
        text = pyperclip.paste()
        if isinstance(text, str):
            return text.strip()
        return ""
    except Exception:
        return ""