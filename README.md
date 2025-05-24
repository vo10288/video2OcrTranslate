=========
video2ocr
=========
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

Questo progetto è rilasciato sotto licenza GNU GPL v3.

Creato da:

Antonio 'Visi@n' Broi – antonio@broi.it

# video2OcrTranslate
