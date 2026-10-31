"""Small dependency-free PDF writer used for the interview task brief.

Only what the brief needs is supported: A4 pages, Helvetica text, wrapping and
bullets. Keeping it local avoids shipping a PDF library for one download.
"""

PAGE_WIDTH = 595
PAGE_HEIGHT = 842
MARGIN = 56
USABLE = PAGE_WIDTH - MARGIN * 2

STYLES = {
    "title": {"font": "/F2", "size": 16, "leading": 20},
    "heading": {"font": "/F2", "size": 11, "leading": 15},
    "body": {"font": "/F1", "size": 10, "leading": 14},
    "bullet": {"font": "/F1", "size": 10, "leading": 14},
    "gap": {"font": "/F1", "size": 6, "leading": 8},
}

# Helvetica averages about half the point size per glyph; bold is a touch wider.
_WIDTH_FACTOR = {"/F1": 0.5, "/F2": 0.54}

_REPLACEMENTS = {
    "—": "-",
    "–": "-",
    "’": "'",
    "‘": "'",
    "“": '"',
    "”": '"',
    "…": "...",
    "•": "-",
}


def _ascii(text: str) -> str:
    out = "".join(_REPLACEMENTS.get(char, char) for char in text)
    return out.encode("ascii", "ignore").decode("ascii")


def _escape(text: str) -> str:
    return text.replace("\\", r"\\").replace("(", r"\(").replace(")", r"\)")


def _wrap(text: str, font: str, size: float) -> list[str]:
    limit = max(20, int(USABLE / (_WIDTH_FACTOR[font] * size)))
    lines: list[str] = []
    for paragraph in (_ascii(text) or " ").split("\n"):
        words = paragraph.split()
        if not words:
            lines.append("")
            continue
        current = words[0]
        for word in words[1:]:
            if len(current) + 1 + len(word) <= limit:
                current = f"{current} {word}"
            else:
                lines.append(current)
                current = word
        lines.append(current)
    return lines


def _flow(blocks: list[tuple[str, str]]) -> list[list[str]]:
    """Split the styled blocks into page-sized chunks of content-stream ops."""
    pages: list[list[str]] = []
    current: list[str] = []
    y = PAGE_HEIGHT - MARGIN

    def new_page() -> None:
        nonlocal current, y
        pages.append(current)
        current = []
        y = PAGE_HEIGHT - MARGIN

    for style, text in blocks:
        spec = STYLES[style]
        prefix = "  •  " if style == "bullet" else ""
        for line in _wrap(prefix + text if prefix else text, spec["font"], spec["size"]):
            if y - spec["leading"] < MARGIN:
                new_page()
            current.append(
                f"{spec['font']} {spec['size']} Tf {spec['leading']} TL "
                f"{MARGIN} {y:.2f} Td ({_escape(line)}) Tj"
            )
            y -= spec["leading"]
        y -= 2
    if current:
        pages.append(current)
    return pages


def build_pdf(title: str, blocks: list[tuple[str, str]]) -> bytes:
    """Render the brief. `blocks` is a list of (style, text) pairs."""
    body: list[tuple[str, str]] = [("title", title), ("gap", "")]
    body.extend(blocks)
    pages = _flow(body)

    stream_objects = [f"<< /Length {len(_stream(page))} >>\n{_stream(page)}" for page in pages]

    objects: list[str] = [
        "<< /Type /Catalog /Pages 2 0 R >>",
        f"<< /Type /Pages /Kids [{' '.join(f'{5 + index} 0 R' for index in range(len(pages)))}] "
        f"/Count {len(pages)} >>",
        "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>",
        "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>",
        "<< /Type /Font /Subtype /Type1 /BaseFont /Courier /Encoding /WinAnsiEncoding >>",
    ]
    first_content = len(objects) + 1
    for index, page in enumerate(pages):
        objects.append(
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {PAGE_WIDTH} {PAGE_HEIGHT}] "
            f"/Resources << /Font << /F1 3 0 R /F2 4 0 R /F3 5 0 R >> >> "
            f"/Contents {first_content + index} 0 R >>"
        )
    objects.extend(stream_objects)

    out = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets: list[int] = []
    for index, payload in enumerate(objects, 1):
        offsets.append(len(out))
        out.extend(f"{index} 0 obj\n{payload}\nendobj\n".encode("latin-1"))

    xref_at = len(out)
    out.extend(f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode("ascii"))
    for offset in offsets:
        out.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    out.extend(
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_at}\n%%EOF\n".encode("ascii")
    )
    return bytes(out)


def _stream(ops: list[str]) -> str:
    lines = "\n".join(f"BT {op} ET" for op in ops)
    return f"stream\n{lines}\nendstream"
