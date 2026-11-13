def split_text(text: str, size: int, overlap: int) -> list[str]:
    if size <= 0 or overlap < 0 or overlap >= size:
        raise ValueError('Tamanho e sobreposição inválidos')
    text = text.replace('\x00', '').strip()
    return [text[start:start + size] for start in range(0, len(text), size - overlap)
            if text[start:start + size].strip()]
