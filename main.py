import pyttsx3
import PyPDF2

# from tkinter.filedialog import *
with open('The Body Keeps the Score_ Brain, Mind, and Body in the Healing of Trauma.pdf', 'rb') as book:
    reader = PyPDF2.PdfReader(book)
    print(book)

    audio_reader = pyttsx3.init()
    audio_reader.setProperty('rate', 200)
    audio_reader.voices = audio_reader.getProperty("voices")
    audio_reader.setProperty("voice", audio_reader.voices[0].id)  # 0 female 1 male voice

    for page in range(len(reader.pages)):
        next_page = reader.pages[page]
        content = next_page.extract_text()

        audio_reader.say(content)

        print(page)
        print(content)
        audio_reader.runAndWait()
