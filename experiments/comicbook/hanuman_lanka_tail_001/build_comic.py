"""Build the Lanka-tail comic with browser-native Devanagari shaping."""

from __future__ import annotations

import html
import json
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[2]
ART = ROOT / "art"
RENDERED = ROOT / "rendered"
CONTENT = ROOT / "content.json"
FONT = REPO / "references" / "fonts" / "NotoSansDevanagari-Variable.ttf"
OUTPUT = REPO / "output" / "pdf" / "hanuman_lanka_tail_001_comic.pdf"


def browser_path() -> Path:
    candidates = [
        Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
        Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
        Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    for name in ("msedge", "google-chrome", "chromium", "chrome"):
        resolved = shutil.which(name)
        if resolved:
            return Path(resolved)
    raise RuntimeError("No Chromium-based browser was found for PDF rendering.")


def page(panel: dict, number: int) -> str:
    image = (ART / f"panel_{number:02}.png").resolve().as_uri()
    caption = html.escape(panel["caption_hi"])
    return f"""
      <section class="page">
        <img class="art" src="{image}" alt="">
        <div class="caption"><span>{caption}</span><b>{number}</b></div>
      </section>
    """


def build_html() -> Path:
    data = json.loads(CONTENT.read_text(encoding="utf-8"))
    missing = [
        str(ART / f"panel_{index:02}.png")
        for index in range(1, len(data["panels"]) + 1)
        if not (ART / f"panel_{index:02}.png").is_file()
    ]
    if missing:
        raise FileNotFoundError("Missing panel art: " + ", ".join(missing))
    if not FONT.is_file():
        raise FileNotFoundError(f"Tracked Devanagari font is missing: {FONT}")

    cover_image = (ART / "panel_01.png").resolve().as_uri()
    sheets = [
        f"""
        <section class="page cover">
          <img class="art" src="{cover_image}" alt="">
          <div class="cover-box">
            <h1>{html.escape(data["title_hi"])}</h1>
            <p>{html.escape(data["subtitle_hi"])}</p>
          </div>
        </section>
        """
    ]
    sheets.extend(page(panel, index) for index, panel in enumerate(data["panels"], 1))
    document = f"""<!doctype html>
<html lang="hi">
<head>
<meta charset="utf-8">
<style>
@font-face {{
  font-family: "AI Bhakti Devanagari";
  src: url("{FONT.resolve().as_uri()}") format("truetype");
  font-weight: 100 900;
}}
@page {{ size: A4; margin: 0; }}
* {{ box-sizing: border-box; }}
html, body {{ margin: 0; background: #f4e4bd; }}
body {{ font-family: "AI Bhakti Devanagari", "Nirmala UI", sans-serif; }}
.page {{
  width: 210mm; height: 297mm; overflow: hidden; position: relative;
  page-break-after: always; background: #f4e4bd;
}}
.art {{ width: 100%; height: 232mm; object-fit: cover; display: block; }}
.caption {{
  height: 65mm; border-left: 4mm solid #a83220; padding: 12mm 14mm 10mm 14mm;
  color: #3c210e; font-size: 7mm; line-height: 1.45;
  display: flex; gap: 8mm; align-items: center; justify-content: space-between;
}}
.caption span {{ max-width: 166mm; }}
.caption b {{ color: #a83220; font-size: 5mm; align-self: flex-end; }}
.cover .art {{ width: 100%; height: 100%; }}
.cover::after {{
  content: ""; position: absolute; inset: 0;
  background: linear-gradient(180deg, rgba(25,12,4,.30), rgba(25,12,4,.06) 55%, rgba(25,12,4,.58));
}}
.cover-box {{
  position: absolute; z-index: 2; left: 14mm; right: 14mm; top: 18mm;
  padding: 12mm; text-align: center; border: 1.2mm solid #e9b842;
  border-radius: 5mm; background: rgba(42,20,7,.84);
}}
h1 {{ margin: 0; color: #fff1c7; font-size: 17mm; line-height: 1.1; }}
.cover-box p {{ margin: 5mm 0 0; color: #f5ca64; font-size: 7mm; }}
</style>
</head>
<body>{''.join(sheets)}</body>
</html>"""
    RENDERED.mkdir(parents=True, exist_ok=True)
    path = RENDERED / "comic.html"
    path.write_text(document, encoding="utf-8")
    return path


def build() -> Path:
    html_path = build_html()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    command = [
        str(browser_path()),
        "--headless=new",
        "--disable-gpu",
        "--no-pdf-header-footer",
        "--allow-file-access-from-files",
        f"--print-to-pdf={OUTPUT}",
        html_path.resolve().as_uri(),
    ]
    result = subprocess.run(command, capture_output=True, text=True, timeout=120)
    if result.returncode != 0 or not OUTPUT.is_file() or OUTPUT.stat().st_size < 100_000:
        raise RuntimeError(
            f"Browser PDF render failed ({result.returncode}): "
            f"{result.stderr.strip() or result.stdout.strip()}"
        )
    return OUTPUT


if __name__ == "__main__":
    print(build())
