#!/opt/virtualenv/computer_vision/bin/python3

# 20250604-h.23.40
# https://tsurugi-linux.org
# by Visi@n
# LICENSE: MIT

import os
import sys
import subprocess
import shutil
import zipfile
import hashlib
import csv
import argparse
from pathlib import Path
import webbrowser
from datetime import datetime
import platform
from googletrans import Translator  # ✅ IMPORT CORRETTO

HOME = Path.home()
WORKING_DIR = HOME / "02.computer_vision/04.video2ocr"
DIRS = {
    "video": WORKING_DIR / "01.video",
    "images": WORKING_DIR / "02.images",
    "ocr_output": WORKING_DIR / "04.ocr_output",
    "translated_output": WORKING_DIR / "05.translated_output"
}

ASCII_ART = """
By Visi@n
"""

def check_dependencies():
    missing = []
    for cmd in ["ffmpeg", "tesseract"]:
        if shutil.which(cmd) is None:
            missing.append(cmd)
    if missing:
        print("\n❌ I seguenti strumenti non sono installati o non sono nel PATH:")
        for cmd in missing:
            print(f"  - {cmd}")
        sys.exit(1)

def get_installed_languages():
    output = subprocess.check_output(['tesseract', '--list-langs'], text=True)
    return output.splitlines()[1:]

def calculate_hashes(files, output_csv):
    with open(output_csv, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["File", "SHA256"])
        for file in files:
            if file.is_file():
                with open(file, 'rb') as x:
                    writer.writerow([file.relative_to(WORKING_DIR), hashlib.sha256(x.read()).hexdigest()])

def ensure_directories():
    for d in DIRS.values():
        d.mkdir(parents=True, exist_ok=True)

def extract_frames(framerate, timestamp):
    print("🎞️ Estrazione frame da video in corso...")
    for video in DIRS["video"].glob("*"):
        out_pattern = DIRS["images"] / f"{video.stem}-%04d.png"
        subprocess.run(f'ffmpeg -i "{video}" -r {framerate} -f image2 "{out_pattern}"', shell=True)
    print("✅ Frame estratti")
    extracted_files = list(DIRS["images"].glob("*.png"))
    calculate_hashes(extracted_files, WORKING_DIR / f"hash-images-{timestamp}.csv")

def run_ocr(lang, timestamp):
    print("🔍 OCR in corso con Tesseract...")
    for img in DIRS["images"].glob("*.png"):
        output = DIRS["ocr_output"] / img.name.replace(".png", "")
        subprocess.run(f'tesseract -l {lang} "{img}" "{output}"', shell=True)
    print("✅ OCR completato")
    text_files = list(DIRS["ocr_output"].glob("*.txt"))
    calculate_hashes(text_files, WORKING_DIR / f"hash-ocr-{timestamp}.csv")

def translate_texts(dest_lang, timestamp):
    print("🌐 Traduzione testi in corso...")
    translator = Translator()
    for file in DIRS["ocr_output"].glob("*.txt"):
        text = file.read_text(encoding='utf-8')
        translated = translator.translate(text, dest=dest_lang).text
        output_file = DIRS["translated_output"] / file.name.replace(".txt", f"_{dest_lang}.txt")
        output_file.write_text(translated, encoding='utf-8')
    translated_files = list(DIRS["translated_output"].glob("*.txt"))
    calculate_hashes(translated_files, WORKING_DIR / f"hash-translated-{timestamp}.csv")

def create_html_report(lang, dest_lang, timestamp):
    print("📝 Generazione report HTML...")
    report = WORKING_DIR / f"index_{lang}_{dest_lang}_{timestamp}.html"
    with open(report, "w", encoding="utf-8") as f:
        f.write(f"<html><head><title>video2ocrTranslate {timestamp}</title></head><body>")
        f.write(f"<pre style='font-family: monospace;'>{ASCII_ART}</pre>")
        f.write(f"<h2>Report OCR e Traduzione</h2><table border=1>")
        f.write("<tr><th>Frame</th><th>ORIGINAL TEXT OCR</th><th>TEXT TRANSLATED</th></tr>")
        for img in DIRS["images"].glob("*.png"):
            name = img.name.replace(".png", ".txt")
            txt_file = DIRS["ocr_output"] / name
            tr_file = DIRS["translated_output"] / name.replace(".txt", f"_{dest_lang}.txt")
            if txt_file.exists() and tr_file.exists():
                f.write("<tr>")
                f.write(f"<td><a target='_blank' href='02.images/{img.name}'><img width=300 src='02.images/{img.name}'></a></td>")
                f.write(f"<td><a target='_blank' href='04.ocr_output/{txt_file.name}'>Testo</a><br><pre>{txt_file.read_text(encoding='utf-8')}</pre></td>")
                f.write(f"<td><a target='_blank' href='05.translated_output/{tr_file.name}'>Traduzione</a><br><pre>{tr_file.read_text(encoding='utf-8')}</pre></td>")
                f.write("</tr>")
        f.write("</table></body></html>")
    if platform.system() == "Windows":
        os.startfile(report)
    else:
        webbrowser.open_new_tab(str(report))
    return report

def final_zip_and_hash(timestamp, report_path):
    print("📦 Creazione pacchetto finale...")
    zip_file = WORKING_DIR / f"acquisizione-forense-{timestamp}.zip"
    with zipfile.ZipFile(zip_file, 'w') as z:
        for d in DIRS.values():
            for f in d.rglob("*"):
                z.write(f, arcname=f.relative_to(WORKING_DIR))
        z.write(report_path, arcname=report_path.name)
    calculate_hashes([*WORKING_DIR.rglob("*.*")], WORKING_DIR / f"hash-final-{timestamp}.csv")

def main():
    parser = argparse.ArgumentParser(description="OCR from video with Tesseract, FFmpeg and Translate \n WARNING the googletrans Python Library use API google.com ")
    parser.add_argument("--lang", type=str, default="eng", help="OCR Language for Tesseract ex. eng ")
    parser.add_argument("--framerate", type=int, default=5, help="Framerate at second")
    parser.add_argument("--translate-language", "-t", type=str, default="it", help="Destination Language ex. it")
    parser.add_argument("--langs", action="store_true", help="Elenca le lingue supportate da Tesseract")
    args = parser.parse_args()

    if args.langs:
        print("\nLingue disponibili:")
        print("\n".join(get_installed_languages()))
        return

    check_dependencies()
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    ensure_directories()
    extract_frames(args.framerate, timestamp)
    run_ocr(args.lang, timestamp)

    if args.translate_language:
        translate_texts(args.translate_language, timestamp)
        report_path = create_html_report(args.lang, args.translate_language, timestamp)
    else:
        report_path = create_html_report(args.lang, "", timestamp)

    final_zip_and_hash(timestamp, report_path)

if __name__ == '__main__':
    main()
