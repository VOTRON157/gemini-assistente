import speech_recognition as sp
from gtts import gTTS
import google.generativeai as genai
from pydub import AudioSegment
from pydub.playback import play
import re
from dotenv import load_dotenv
import os
import subprocess

load_dotenv()

genai.configure(api_key=os.getenv('TOKEN'))

instrucoes = (
    "Você é um assistente virtual."
    "Não de respostas muito longas."
)

model = genai.GenerativeModel(model_name='gemini-1.5-flash', system_instruction=instrucoes)
chat = model.start_chat(history=[])

micro = sp.Recognizer()
with sp.Microphone() as source:
    while True:
        print("Ouvindo...")
        audio = micro.listen(source, phrase_time_limit=6) # Esse "6" é o tempo que o código vai ficar ouvindo, se a pessoa falar algo que dure 7 segundos, só vai capturar os 6 segundos de fala. Você pode remover essa opção, porém, se tiver varias pessoas na chamada, o código nunca irá parar de capturar o som, já que as pessoas não irão parar de falar.

        try:                               
            text = micro.recognize_google(audio, language="pt-BR")              
            print("Fala capturada, gerando saida...")

            response = chat.send_message(text) 
            string_nova = re.sub(r'[^a-zA-Z0-9À-ÿ.,;:!?\'"()\- ]', '', response.text)
            gTTS(string_nova, lang='pt', slow=False).save('out.mp3')

            root = r'out.mp3'
            output_audio_file = "final.mp3"
            ffmpeg_command = ["ffmpeg", "-y", "-i", 'out.mp3', "-filter:a", 'atempo=2.0', output_audio_file]
            subprocess.run(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            song = AudioSegment.from_mp3('final.mp3')
            play(song)

        except sp.UnknownValueError:
            print("Não entendi oque foi falado.")
            gTTS('Não entendi o que foi capturado pelo microfone.', lang='pt', slow=False).save('out.mp3')
            output_audio_file = "final.mp3"
            ffmpeg_command = ["ffmpeg", "-y", "-i", 'out.mp3', "-filter:a", 'atempo=2.0', output_audio_file]
            subprocess.run(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            song = AudioSegment.from_mp3('final.mp3')
            play(song)

        except sp.RequestError as e:
            print("Estou tendo problemas para achar resultados no Google Speech Recognition service; {0}".format(e))
