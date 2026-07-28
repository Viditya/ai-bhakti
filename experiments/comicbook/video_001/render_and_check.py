from pathlib import Path

import pypdfium2 as pdfium
from PIL import Image, ImageOps
from pypdf import PdfReader


ROOT = Path(__file__).resolve().parent
PDF = ROOT / "ai_bhakti_video_001_comic.pdf"
OUTPUT = ROOT / "rendered_pdf"


def main() -> None:
    reader = PdfReader(str(PDF))
    if len(reader.pages) != 8:
        raise ValueError(f"Expected 8 pages, found {len(reader.pages)}")

    OUTPUT.mkdir(parents=True, exist_ok=True)
    document = pdfium.PdfDocument(str(PDF))
    thumbnails = []
    for index, page in enumerate(document):
        bitmap = page.render(scale=1.5)
        image = bitmap.to_pil()
        image.save(OUTPUT / f"page_{index:02}.png")
        thumbnail = image.copy()
        thumbnail.thumbnail((300, 425), Image.Resampling.LANCZOS)
        thumbnails.append(ImageOps.expand(thumbnail, border=4, fill="white"))

    sheet = Image.new("RGB", (640, 1740), "#34200f")
    for index, thumbnail in enumerate(thumbnails):
        x = 10 + (index % 2) * 315
        y = 10 + (index // 2) * 430
        sheet.paste(thumbnail, (x, y))
    sheet.save(OUTPUT / "contact_sheet.png")
    print(f"Verified {len(reader.pages)} pages and rendered them to {OUTPUT}")


if __name__ == "__main__":
    main()
