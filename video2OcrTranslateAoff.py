#!/home/vision/anaconda3/envs/py3.12/bin/python

# 20250608
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
import whisper
from googletrans import Translator

HOME = Path.home()
WORKING_DIR = HOME / "02.computer_vision/04.video2ocr"
DIRS = {
    "video": WORKING_DIR / "01.video",
    "images": WORKING_DIR / "02.images",
    "ocr_output": WORKING_DIR / "04.ocr_output",
    "translated_output": WORKING_DIR / "05.translated_output"
}
ASCII_ART = "By Visi@n"

def check_dependencies():
    missing = []
    for cmd in ["ffmpeg", "tesseract"]:
        if shutil.which(cmd) is None:
            missing.append(cmd)
    if missing:
        print("\n❌ Strumenti mancanti:", ", ".join(missing))
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
    print("🎞️ Estrazione frame da video...")
    for video in DIRS["video"].glob("*"):
        out_pattern = DIRS["images"] / f"{video.stem}-%04d.png"
        subprocess.run(f'ffmpeg -i "{video}" -r {framerate} -f image2 "{out_pattern}"', shell=True)
    print("✅ Frame estratti")
    extracted_files = list(DIRS["images"].glob("*.png"))
    calculate_hashes(extracted_files, WORKING_DIR / f"hash-images-{timestamp}.csv")

def run_ocr(lang, timestamp):
    print("🔍 OCR in corso...")
    for img in DIRS["images"].glob("*.png"):
        output = DIRS["ocr_output"] / img.name.replace(".png", "")
        subprocess.run(f'tesseract -l {lang} "{img}" "{output}"', shell=True)
    print("✅ OCR completato")
    text_files = list(DIRS["ocr_output"].glob("*.txt"))
    calculate_hashes(text_files, WORKING_DIR / f"hash-ocr-{timestamp}.csv")

def translate_texts(dest_lang, timestamp):
    print("🌐 Traduzione testi...")
    translator = Translator()
    for file in DIRS["ocr_output"].glob("*.txt"):
        text = file.read_text(encoding='utf-8')
        translated = translator.translate(text, dest=dest_lang).text
        output_file = DIRS["translated_output"] / file.name.replace(".txt", f"_{dest_lang}.txt")
        output_file.write_text(translated, encoding='utf-8')
    translated_files = list(DIRS["translated_output"].glob("*.txt"))
    calculate_hashes(translated_files, WORKING_DIR / f"hash-translated-{timestamp}.csv")

def process_audio_whisper(timestamp, lang, dest_lang):
    print("🎧 Estrazione audio e trascrizione (Whisper Python)...")
    audio_dir = WORKING_DIR / "06.audio"
    audio_dir.mkdir(parents=True, exist_ok=True)

    audio_txt = audio_dir / f"transcript_{timestamp}.txt"
    audio_translated_txt = audio_dir / f"transcript_{timestamp}_{dest_lang}.txt"

    model = whisper.load_model("base")
    translator = Translator()

    for video in DIRS["video"].glob("*"):
        audio_path = audio_dir / f"{video.stem}.wav"
        subprocess.run(f'ffmpeg -y -i "{video}" -vn -acodec pcm_s16le -ar 16000 -ac 1 "{audio_path}"', shell=True)

        # 🔍 Nessun parametro "language=..." per autodetect
        result = model.transcribe(str(audio_path))
        transcript = result["text"]
        audio_txt.write_text(transcript, encoding='utf-8')

        translated = translator.translate(transcript, dest=dest_lang).text
        audio_translated_txt.write_text(translated, encoding='utf-8')

        print("✅ Audio trascritto e tradotto")

    return audio_txt, audio_translated_txt

def create_html_report(lang, dest_lang, timestamp, audio_txt=None, audio_tr_txt=None):
    print("📝 Generazione report HTML...")
    report = WORKING_DIR / f"index_{lang}_{dest_lang}_{timestamp}.html"
    with open(report, "w", encoding="utf-8") as f:
        f.write(f"<html><head><title>video2ocrTranslate {timestamp}</title></head><body>")
        f.write(f"<pre style='font-family: monospace;'>{ASCII_ART}</pre>")
        f.write("<h2>Report OCR e Traduzione</h2><table border=1>")
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
        f.write("</table>")

        if audio_txt and audio_txt.exists():
            f.write("<hr><h2>🎧 Audio Transcript</h2>")
            f.write(f"<p><a target='_blank' href='06.audio/{audio_txt.name}'>File trascritto</a></p>")
            f.write(f"<pre>{audio_txt.read_text(encoding='utf-8')}</pre>")

        if audio_tr_txt and audio_tr_txt.exists():
            f.write("<h3>🌍 Traduzione</h3>")
            f.write(f"<p><a target='_blank' href='06.audio/{audio_tr_txt.name}'>File tradotto</a></p>")
            f.write(f"<pre>{audio_tr_txt.read_text(encoding='utf-8')}</pre>")

        f.write("</body></html>")
    if platform.system() == "Windows":
        os.startfile(report)
    else:
        webbrowser.open_new_tab(str(report))
    return report

def final_zip_and_hash(timestamp, report_path):
    print("📦 Creazione ZIP finale...")
    zip_file = WORKING_DIR / f"acquisizione-forense-{timestamp}.zip"
    with zipfile.ZipFile(zip_file, 'w') as z:
        for d in DIRS.values():
            for f in d.rglob("*"):
                z.write(f, arcname=f.relative_to(WORKING_DIR))
        if report_path.exists():
            z.write(report_path, arcname=report_path.name)
    calculate_hashes([*WORKING_DIR.rglob("*.*")], WORKING_DIR / f"hash-final-{timestamp}.csv")

def main():
    parser = argparse.ArgumentParser(description="OCR da video con Tesseract, FFmpeg, Whisper e Google Translate")
    parser.add_argument("--lang", type=str, default="eng", help="Lingua OCR / Whisper (es: eng)")
    parser.add_argument("--framerate", type=int, default=5, help="Framerate per estrazione frame")
    parser.add_argument("--translate-language", "-t", type=str, default="it", help="Lingua di destinazione (es: it)")
    parser.add_argument("--langs", action="store_true", help="Elenca le lingue supportate da Tesseract")
    parser.add_argument("--audio-offline", action="store_true", help="Estrai e trascrivi audio con Whisper offline")
    args = parser.parse_args()

    if args.langs:
        print("\nLingue disponibili:")
        print("\n".join(get_installed_languages()))
        return

    check_dependencies()
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    ensure_directories()

    video_files = list(DIRS["video"].glob("*"))
    image_files = list(DIRS["images"].glob("*.png"))

    if video_files:
        extract_frames(args.framerate, timestamp)

    if image_files or video_files:
        run_ocr(args.lang, timestamp)
        translate_texts(args.translate_language, timestamp)

        audio_txt = audio_tr_txt = None
        if args.audio_offline and video_files:
            audio_txt, audio_tr_txt = process_audio_whisper(timestamp, args.lang, args.translate_language)

        report_path = create_html_report(args.lang, args.translate_language, timestamp, audio_txt, audio_tr_txt)
        final_zip_and_hash(timestamp, report_path)
    else:
        print("⚠️ Nessun file video o immagine trovato.")

if __name__ == '__main__':
    main()
