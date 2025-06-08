#!/home/vision/anaconda3/envs/py3.12/bin/python

# 20250608 aggiornato con autodetect Whisper, traduzioni, scelta modello
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

# Auto installa moduli mancanti
try:
    import whisper
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "openai-whisper"])
    import whisper

try:
    from googletrans import Translator
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "googletrans==4.0.0-rc1"])
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
    for cmd in ["ffmpeg", "tesseract"]:
        if shutil.which(cmd) is None:
            print(f"\n❌ Lo strumento richiesto '{cmd}' non è installato nel sistema!")
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
    calculate_hashes(list(DIRS["images"].glob("*.png")), WORKING_DIR / f"hash-images-{timestamp}.csv")

def run_ocr(lang, timestamp):
    print("🔍 OCR in corso...")
    for img in DIRS["images"].glob("*.png"):
        output = DIRS["ocr_output"] / img.name.replace(".png", "")
        subprocess.run(f'tesseract -l {lang} "{img}" "{output}"', shell=True)
    print("✅ OCR completato")
    calculate_hashes(list(DIRS["ocr_output"].glob("*.txt")), WORKING_DIR / f"hash-ocr-{timestamp}.csv")

def translate_texts(dest_lang, timestamp):
    print("🌐 Traduzione testi OCR...")
    translator = Translator()
    for file in DIRS["ocr_output"].glob("*.txt"):
        text = file.read_text(encoding='utf-8')
        translated = translator.translate(text, dest=dest_lang).text
        output_file = DIRS["translated_output"] / file.name.replace(".txt", f"_{dest_lang}.txt")
        output_file.write_text(translated, encoding='utf-8')
    calculate_hashes(list(DIRS["translated_output"].glob("*.txt")), WORKING_DIR / f"hash-translated-{timestamp}.csv")

def process_audio_whisper(timestamp, mode="offline", model_size="base"):
    print(f"🎧 Trascrizione audio (Whisper: {model_size}, mode: {mode})...")
    audio_dir = WORKING_DIR / "06.audio"
    audio_dir.mkdir(parents=True, exist_ok=True)

    audio_txt = audio_dir / f"transcript_{timestamp}.txt"
    audio_translated_en = audio_dir / f"transcript_{timestamp}_en.txt"
    audio_translated_it = audio_dir / f"transcript_{timestamp}_it.txt"

    model = whisper.load_model(model_size)
    translator = Translator()

    for video in DIRS["video"].glob("*"):
        audio_path = audio_dir / f"{video.stem}.wav"
        subprocess.run(f'ffmpeg -y -i "{video}" -vn -acodec pcm_s16le -ar 16000 -ac 1 "{audio_path}"', shell=True)

        result = model.transcribe(str(audio_path))
        transcript = result["text"]
        audio_txt.write_text(transcript, encoding='utf-8')

        translated_en = translator.translate(transcript, dest="en").text
        audio_translated_en.write_text(translated_en, encoding='utf-8')

        if mode == "online":
            translated_it = translator.translate(transcript, dest="it").text
            audio_translated_it.write_text(translated_it, encoding='utf-8')
            return audio_txt, audio_translated_en, audio_translated_it

    return audio_txt, audio_translated_en, None

def create_html_report(lang, dest_lang, timestamp, audio_txt=None, audio_tr_en=None, audio_tr_it=None):
    report = WORKING_DIR / f"index_{lang}_{dest_lang}_{timestamp}.html"
    with open(report, "w", encoding="utf-8") as f:
        f.write(f"<html><head><title>video2ocrTranslate {timestamp}</title></head><body>")
        f.write(f"<pre>{ASCII_ART}</pre><h2>Report OCR e Traduzione</h2><table border=1>")
        f.write("<tr><th>Frame</th><th>OCR</th><th>Traduzione</th></tr>")
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
            f.write(f"<hr><h2>🎧 Audio Transcript</h2><p><a target='_blank' href='06.audio/{audio_txt.name}'>Testo</a></p><pre>{audio_txt.read_text()}</pre>")
        if audio_tr_en and audio_tr_en.exists():
            f.write(f"<h3>🌍 Traduzione in Inglese</h3><p><a target='_blank' href='06.audio/{audio_tr_en.name}'>Tradotto EN</a></p><pre>{audio_tr_en.read_text()}</pre>")
        if audio_tr_it and audio_tr_it.exists():
            f.write(f"<h3>🌍 Traduzione in Italiano</h3><p><a target='_blank' href='06.audio/{audio_tr_it.name}'>Tradotto IT</a></p><pre>{audio_tr_it.read_text()}</pre>")

        f.write("</body></html>")
    webbrowser.open_new_tab(str(report))
    return report

def final_zip_and_hash(timestamp, report_path):
    zip_file = WORKING_DIR / f"acquisizione-forense-{timestamp}.zip"
    with zipfile.ZipFile(zip_file, 'w') as z:
        for d in DIRS.values():
            for f in d.rglob("*"):
                z.write(f, arcname=f.relative_to(WORKING_DIR))
        z.write(report_path, arcname=report_path.name)
    calculate_hashes([*WORKING_DIR.rglob("*.*")], WORKING_DIR / f"hash-final-{timestamp}.csv")

def main():
    parser = argparse.ArgumentParser(description="OCR + Audio Whisper con traduzioni")
    parser.add_argument("--lang", type=str, default="eng", help="Lingua OCR per Tesseract chi_sim ara rus ukr")
    parser.add_argument("--translate-language", type=str, default="it", help="Lingua destinazione per testo OCR")
    parser.add_argument("--framerate", type=int, default=5, help="Frame rate estrazione da video")
    parser.add_argument("--audio-offline", action="store_true", help="Trascrizione + traduzione EN")
    parser.add_argument("--audio-online", action="store_true", help="Trascrizione + traduzione EN/IT")
    parser.add_argument("--whisper-model", type=str, default="base", help="Modello Whisper (base, small, medium, large)")
    args = parser.parse_args()

    check_dependencies()
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    ensure_directories()

    video_files = list(DIRS["video"].glob("*"))
    image_files = list(DIRS["images"].glob("*.png"))

    if video_files:
        extract_frames(args.framerate, timestamp)

    if video_files or image_files:
        run_ocr(args.lang, timestamp)
        translate_texts(args.translate_language, timestamp)

        audio_txt = audio_tr_en = audio_tr_it = None
        if args.audio_offline:
            audio_txt, audio_tr_en, audio_tr_it = process_audio_whisper(timestamp, mode="offline", model_size=args.whisper_model)
        elif args.audio_online:
            audio_txt, audio_tr_en, audio_tr_it = process_audio_whisper(timestamp, mode="online", model_size=args.whisper_model)

        report_path = create_html_report(args.lang, args.translate_language, timestamp, audio_txt, audio_tr_en, audio_tr_it)
        final_zip_and_hash(timestamp, report_path)
    else:
        print("❌ Nessun file trovato per elaborazione.")

if __name__ == '__main__':
    main()
