from flask import Flask, request, render_template, send_file
import requests

app = Flask(__name__)

OPENAI_API_KEY = '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'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    text = request.form['text']
    voice = request.form['voice']
    speed = float(request.form['speed'])
    audio_content = convert_text_to_speech_openai(text, voice, speed)
    if audio_content:
        file_path = 'output.mp3'
        with open(file_path, 'wb') as audio_file:
            audio_file.write(audio_content)
        return send_file(file_path, as_attachment=True)
    return "Error converting text to speech"

def convert_text_to_speech_openai(text, voice, speed):
    url = 'https://api.openai.com/v1/audio/speech'
    headers = {'Authorization': f'Bearer {OPENAI_API_KEY}', 'Content-Type': 'application/json'}
    data = {'model': 'tts-1', 'input': text, 'voice': voice, 'speed': speed}
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.content
    else:
        return None

if __name__ == '__main__':
    # Запуск приложения для публичного доступа и отключение режима отладки
    app.run(host='0.0.0.0', port=5000, debug=False)
