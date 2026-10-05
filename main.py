"""Read a PDF out loud (or save it as audio) using offline text-to-speech."""
import argparse
import shutil
import subprocess
import sys

import pyttsx3
from pypdf import PdfReader


def parse_args():
    parser = argparse.ArgumentParser(description="Turn a PDF into speech.")
    parser.add_argument("pdf", nargs="?", default="sample.pdf", help="PDF file to read (default: sample.pdf)")
    parser.add_argument("--rate", type=int, default=200, help="speaking speed in words per minute (default: 200)")
    parser.add_argument("--voice", type=int, help="voice index from --list-voices (default: system voice)")
    parser.add_argument("--start", type=int, default=1, help="page number to start from (default: 1)")
    parser.add_argument("--save", metavar="FILE", help="save the audio to FILE (e.g. book.wav) instead of playing it")
    parser.add_argument("--list-voices", action="store_true", help="list available voices and exit")
    return parser.parse_args()


def main():
    args = parse_args()

    engine = pyttsx3.init()
    voices = engine.getProperty("voices")
    if args.list_voices:
        for i, voice in enumerate(voices):
            print(f"{i}: {voice.name}")
        return

    engine.setProperty("rate", args.rate)
    if args.voice is not None and 0 <= args.voice < len(voices):
        engine.setProperty("voice", voices[args.voice].id)

    try:
        reader = PdfReader(args.pdf)
    except FileNotFoundError:
        sys.exit(f"File not found: {args.pdf}")

    total = len(reader.pages)
    if not 1 <= args.start <= total:
        sys.exit(f"--start must be between 1 and {total}")

    text_parts = []
    for number in range(args.start, total + 1):
        text = (reader.pages[number - 1].extract_text() or "").strip()
        print(f"--- Page {number}/{total} ---")
        print(text or "(no text on this page)")
        if not text:
            continue
        if args.save:
            text_parts.append(text)
        else:
            engine.say(text)
            engine.runAndWait()

    if args.save:
        save_audio(engine, "\n".join(text_parts), args)
        print(f"Saved audio to {args.save}")


def save_audio(engine, text, args):
    # pyttsx3's espeak driver drops longer texts when saving on Linux,
    # so call espeak directly there; other platforms use pyttsx3.
    espeak = sys.platform.startswith("linux") and (shutil.which("espeak-ng") or shutil.which("espeak"))
    if espeak:
        command = [espeak, "-s", str(args.rate), "-w", args.save]
        if args.voice is not None:
            command += ["-v", engine.getProperty("voice")]
        subprocess.run(command, input=text, text=True, check=True)
    else:
        engine.save_to_file(text, args.save)
        engine.runAndWait()


if __name__ == "__main__":
    main()
