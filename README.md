=========
video2ocr
=========

Advanced OCR from videos using Tesseract, FFmpeg, and automatic translation.

This project allows you to:

- Automatically extract frames from video files (.mp4, .mov, etc.) using FFmpeg
- Perform OCR on each frame using Tesseract
- Translate the recognized text into another language using Google Translate
- Generate complete HTML reports with frame image, recognized text, and translated text
- Compute SHA256 hashes and create `.zip` packages for forensic purposes

Requirements
============

- Python >= 3.9

Install Python packages:

.. code-block:: bash

   pip install -r requirements.txt

External requirements (FFmpeg and Tesseract)
============================================

⚠️ FFmpeg and Tesseract must be installed and accessible from the system PATH.

Linux (Debian, Ubuntu, etc.)
----------------------------

Install with apt:

.. code-block:: bash

   sudo apt update
   sudo apt install ffmpeg tesseract-ocr

macOS (with Homebrew)
---------------------

Install with Homebrew:

.. code-block:: bash

   brew install ffmpeg tesseract

Windows
-------

1. Download and install FFmpeg:  
   https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip

   - Extract it to `C:\ffmpeg`
   - Add `C:\ffmpeg\bin` to the system PATH

2. Download and install Tesseract OCR:  
   https://github.com/tesseract-ocr/tesseract/releases/download/5.5.0/tesseract-ocr-w64-setup-5.5.0.20241111.exe

   - Install to `C:\Program Files\Tesseract-OCR`
   - Add `C:\Program Files\Tesseract-OCR` to the system PATH

Verify installation:

.. code-block:: bash

   ffmpeg -version
   tesseract --version

Usage
=====

.. code-block:: bash

   python video2ocr.py --lang eng --framerate 5 --translate-language it

Main options:

- ``--lang``: OCR language for Tesseract (e.g. ``eng``, ``ita``, ``chi_sim``)
- ``--framerate``: number of frames per second extracted from the video (default: 5)
- ``--translate-language`` or ``-t``: language to translate the OCR text into
- ``--langs``: list all languages available in your Tesseract installation

Output
======

- HTML report with image, OCR text, and translated text
- `.txt` files with the extracted and translated texts
- CSV files with SHA256 hashes for forensic integrity
- `.zip` archive with all generated data

License
=======

This project is released under the **MIT**  **QUOTE THE AUTHOR**.

Authors:

- Antonio 'Visi@n' Broi – antonio@broi.it


=========   video2ocr   =========




OCR avanzato da video con supporto a Tesseract, FFmpeg e traduzione automatica.

Questo progetto consente di:

Estrarre automaticamente frame da file video (.mp4, .mov, ecc.) con ffmpeg

Eseguire OCR su ogni frame con tesseract

Tradurre i testi riconosciuti in un'altra lingua (con googletrans)

Generare report HTML completi con immagine, testo riconosciuto e testo tradotto

Calcolare hash SHA256 e creare pacchetti .zip a fini forensi

Requisiti

Python >= 3.9

Installazione pacchetti Python:

.. code-block:: bash

pip install -r requirements.txt

Requisiti esterni (FFmpeg e Tesseract)

⚠️ FFmpeg e Tesseract devono essere installati e accessibili nel PATH del sistema.

Linux (Debian, Ubuntu, ecc.)

.. code-block:: bash

sudo apt update
sudo apt install ffmpeg tesseract-ocr

macOS (con Homebrew)

.. code-block:: bash

brew install ffmpeg tesseract

Windows

Scarica e installa FFmpeg:
https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip

Estrai tutto in C:\ffmpeg

Aggiungi C:\ffmpeg\bin al PATH di sistema

Scarica e installa Tesseract OCR:
https://github.com/tesseract-ocr/tesseract/releases/download/5.5.0/tesseract-ocr-w64-setup-5.5.0.20241111.exe

Installa in C:\Program Files\Tesseract-OCR

Aggiungi C:\Program Files\Tesseract-OCR al PATH di sistema

Verifica che siano raggiungibili:

.. code-block:: bash

ffmpeg -version
tesseract --version

Uso

.. code-block:: bash

python video2ocr.py --lang eng --framerate 5 --translate-language it

Opzioni principali:

--lang: lingua OCR per Tesseract (es. eng, ita, chi_sim)

--framerate: fotogrammi al secondo estratti dal video (default: 5)

--translate-language o -t: lingua in cui tradurre il testo OCR

--langs: mostra tutte le lingue disponibili per Tesseract

Output

Report HTML con frame, testo OCR e traduzione

File .txt con testi riconosciuti e tradotti

Hash CSV per validazione forense

Archivio .zip con tutti i dati generati

Licenza

Questo progetto è rilasciato sotto licenza **M.I.T.** **"cita l'autore"**.

Creato da:

Antonio 'Visi@n' Broi – antonio@broi.it

# video2OcrTranslate
