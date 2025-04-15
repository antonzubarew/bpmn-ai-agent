from typing import Annotated

from fastapi import FastAPI, File, UploadFile

from fastapi.staticfiles import StaticFiles

import speech_recognition as sr
from pydub import AudioSegment

import io

r = sr.Recognizer()

sr.LANGUAGE = 'ru-RU'

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile):
    # 1. Читаем содержимое файла
    contents = await file.read()
    
    # 2. Создаем файлоподобный объект
    audio_file = io.BytesIO(contents)
    
    try:
        # 3. Загружаем аудио (автоматически определяет формат)
        audio = AudioSegment.from_file(audio_file)
        
        # 4. Конвертируем в нужный формат (16kHz, моно)
        audio = audio.set_frame_rate(16000).set_channels(1)
        
        # 5. Экспортируем в WAV в памяти
        wav_io = io.BytesIO()
        audio.export(wav_io, format="wav")
        wav_io.seek(0)  # Перематываем в начало
        
        # 6. Распознаем речь
        with sr.AudioFile(wav_io) as source:
            audio_data = r.record(source)
            text = r.recognize_google(audio_data, language='ru-RU')
        
        # 7. Возвращат текст
        return {
            "text": text
        }
    
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", reload=True)