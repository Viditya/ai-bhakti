from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps, features


ROOT = Path(__file__).resolve().parent
ART = ROOT / "art"
RENDERED = ROOT / "rendered_pages"
OUTPUT = ROOT / "ai_bhakti_video_001_comic.pdf"

PAGE_SIZE = (1240, 1754)
ART_HEIGHT = 1370
BACKGROUND = "#f4e4bd"
INK = "#3c210e"
ACCENT = "#a83220"
DEVANAGARI_FONT = ROOT.parents[2] / "references" / "fonts" / "NotoSansDevanagari-Variable.ttf"

CAPTIONS = [
    "देवराज इंद्र ने बाल हनुमान पर वज्र क्यों चलाया?",
    "एक प्रभात, भूखे बाल हनुमान ने उगते सूर्य को आकाश में लटका हुआ लाल फल समझ लिया।",
    "फल पाने की बाल-सुलभ इच्छा में वे एक ही छलांग में आकाश की ओर उड़ चले।",
    "वे तेज और ताप से निर्भय होकर सूर्यदेव के निकट पहुँचने लगे।",
    "असाधारण घटना देखकर देवलोक में चिंता फैल गई; व्यवस्था की रक्षा का दायित्व इंद्र पर आया।",
    "इंद्र ने वज्र चलाया। प्रहार हनुमान की ठोड़ी पर लगा और वे पर्वत पर मूर्च्छित होकर गिर पड़े।",
    "पवनदेव के दुःख से सृष्टि व्याकुल हुई। तब देवताओं ने बाल हनुमान को वरदान दिए - यही शक्तियाँ आगे धर्म की सेवा में समर्पित हुईं।",
]


def require_complex_text_layout() -> None:
    if not features.check_feature("raqm"):
        raise RuntimeError(
            "Hindi PDF generation is blocked: Pillow has no RAQM/HarfBuzz "
            "complex-text shaping. Install a RAQM-enabled rendering environment "
            "and rerun; BASIC layout is not acceptable for Devanagari."
        )
    if not DEVANAGARI_FONT.exists():
        raise RuntimeError(f"Approved Devanagari font is missing: {DEVANAGARI_FONT}")


def font(size: int, weight: int = 400) -> ImageFont.FreeTypeFont:
    selected = ImageFont.truetype(
        str(DEVANAGARI_FONT),
        size=size,
        layout_engine=ImageFont.Layout.RAQM,
    )
    try:
        axes = selected.get_variation_axes()
        values = [axis["default"] for axis in axes]
        for index, axis in enumerate(axes):
            if axis["name"].lower() == b"weight":
                values[index] = weight
        selected.set_variation_by_axes(values)
    except (OSError, AttributeError, ValueError):
        pass
    return selected


def wrap(draw: ImageDraw.ImageDraw, text: str, selected_font, max_width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current: list[str] = []
    for word in words:
        candidate = " ".join([*current, word])
        width = draw.textbbox(
            (0, 0),
            candidate,
            font=selected_font,
            direction="ltr",
            language="hi",
        )[2]
        if current and width > max_width:
            lines.append(" ".join(current))
            current = [word]
        else:
            current.append(word)
    if current:
        lines.append(" ".join(current))
    return lines


def caption_page(image_path: Path, caption: str, number: int) -> Image.Image:
    page = Image.new("RGB", PAGE_SIZE, BACKGROUND)
    artwork = Image.open(image_path).convert("RGB")
    fitted = ImageOps.fit(
        artwork,
        (PAGE_SIZE[0], ART_HEIGHT),
        method=Image.Resampling.LANCZOS,
        centering=(0.5, 0.5),
    )
    page.paste(fitted, (0, 0))
    draw = ImageDraw.Draw(page)
    draw.rectangle((0, ART_HEIGHT, PAGE_SIZE[0], PAGE_SIZE[1]), fill=BACKGROUND)
    draw.rectangle((0, ART_HEIGHT, 18, PAGE_SIZE[1]), fill=ACCENT)
    body_font = font(43)
    page_font = font(27, weight=700)
    lines = wrap(draw, caption, body_font, PAGE_SIZE[0] - 140)
    line_height = 65
    total_height = len(lines) * line_height
    y = ART_HEIGHT + (PAGE_SIZE[1] - ART_HEIGHT - total_height) // 2 - 8
    for line in lines:
        draw.text(
            (70, y),
            line,
            font=body_font,
            fill=INK,
            direction="ltr",
            language="hi",
        )
        y += line_height
    draw.text(
        (PAGE_SIZE[0] - 62, PAGE_SIZE[1] - 38),
        str(number),
        font=page_font,
        fill=ACCENT,
        anchor="rs",
        direction="ltr",
        language="hi",
    )
    return page


def cover_page() -> Image.Image:
    page = ImageOps.fit(
        Image.open(ART / "panel_01.png").convert("RGB"),
        PAGE_SIZE,
        method=Image.Resampling.LANCZOS,
        centering=(0.5, 0.5),
    )
    overlay = Image.new("RGBA", PAGE_SIZE, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.rounded_rectangle(
        (70, 85, PAGE_SIZE[0] - 70, 390),
        radius=24,
        fill=(45, 21, 6, 205),
        outline=(235, 184, 66, 255),
        width=5,
    )
    title_font = font(86, weight=700)
    subtitle_font = font(40)
    draw.text(
        (PAGE_SIZE[0] // 2, 175),
        "बाल हनुमान और सूर्य",
        font=title_font,
        fill="#fff1c7",
        anchor="mm",
        direction="ltr",
        language="hi",
    )
    draw.text(
        (PAGE_SIZE[0] // 2, 290),
        "एक चित्रकथा",
        font=subtitle_font,
        fill="#f5ca64",
        anchor="mm",
        direction="ltr",
        language="hi",
    )
    return Image.alpha_composite(page.convert("RGBA"), overlay).convert("RGB")


def build() -> Path:
    require_complex_text_layout()
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas

    RENDERED.mkdir(parents=True, exist_ok=True)
    pages = [cover_page()]
    for index, caption in enumerate(CAPTIONS, start=1):
        pages.append(caption_page(ART / f"panel_{index:02}.png", caption, index))

    page_paths = []
    for index, page in enumerate(pages):
        path = RENDERED / f"page_{index:02}.jpg"
        page.save(path, format="JPEG", quality=92, subsampling=0, optimize=True)
        page_paths.append(path)

    pdf = canvas.Canvas(str(OUTPUT), pagesize=A4)
    width, height = A4
    for page_path in page_paths:
        pdf.drawImage(str(page_path), 0, 0, width=width, height=height)
        pdf.showPage()
    pdf.setTitle("बाल हनुमान और सूर्य - एक चित्रकथा")
    pdf.setAuthor("AI Bhakti - isolated comic experiment")
    pdf.save()
    return OUTPUT


if __name__ == "__main__":
    print(build())
