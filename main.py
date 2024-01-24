from flask import Flask, request, jsonify, send_from_directory, send_file
import requests
import os
import time
import json
import logging

logging.basicConfig(level=logging.DEBUG)

# Затем добавьте logging.debug('Some debug message') в ключевые места вашего кода

app = Flask(__name__)

OPENAI_API_KEY = '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'
static_folder_path = 'static'
client_id = "1c3d92ba1ca3221409523f03fa392b09"
client_secret = "905771cedc24d37bdfc12c24ccb6a700"

def get_sendpulse_token(client_id, client_secret):
    url = "https://api.sendpulse.com/oauth/access_token"
    payload = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    }
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        return response.json().get('access_token')
    else:
        return None
@app.route('/statik/<filename>')
def audio_file(filename):
    return send_from_directory(static_folder_path, filename)

@app.route('/')
def index():
    return send_from_directory('templates', 'index.html')

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
    else:
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


@app.route('/api/convert_to_audio', methods=['POST'])
def api_convert_to_audio():
    data = request.json
    text = data['text']
    contact_id = data['contact_id']

    # Сгенерируйте аудиофайл из текста
    audio_content = convert_text_to_speech_openai(text, "nova", 1.0)  # Адаптируйте параметры под ваши нужды
    if audio_content:
        # Сохраните аудиофайл на диск и получите URL для доступа к нему
        audio_url = save_audio_to_disk(audio_content)
        # Отправьте аудиофайл используя полученный URL
        sendpulse_response = send_voice_message_to_sendpulse(get_sendpulse_token(client_id, client_secret), contact_id, audio_url)
        if sendpulse_response and sendpulse_response.get('success'):
            return jsonify({'audio_url': audio_url}), 200
        else:
            error_message = sendpulse_response.get('message') if sendpulse_response else 'Unknown error'
            return jsonify({'error': f'Unable to send voice message: {error_message}'}), 500
    else:
        return jsonify({'error': 'Unable to convert text to speech'}), 500


def save_audio_to_disk(audio_content):
    timestamp = int(time.time())
    your_domain = 'http://www.text2speech.live/'
    file_name = f'audio_{timestamp}.mp3'
    file_path = os.path.join(static_folder_path, file_name)
    with open(file_path, 'wb') as audio_file:
        audio_file.write(audio_content)
    audio_url = f'https://{your_domain}/static/{file_name}'  # Измените базовый URL на нужный
    return audio_url



def send_voice_message_to_sendpulse(bot_token, contact_id, audio_url):
    url = "https://api.sendpulse.com/telegram/contacts/send"
    headers = {
        'Authorization': f'Bearer {bot_token}',
        'Content-Type': 'application/json'
    }
    data = {
        "contact_id": contact_id,
        "message": {
            "type": "audio",
            "audio": audio_url,
            "caption": ""
        }
    }
    response = requests.post(url, headers=headers, json=data)
    logging.debug(f'Request data: {data}')
    if response.status_code == 200:
        logging.debug(f'SendPulse response: {response.json()}')
        return response.json()
    else:
        logging.error(f'SendPulse send failed: {response.status_code}, {response.text}')
        return None

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000,)

