from chalice import Chalice
from chalicelib import storage_service
from chalicelib import recognition_service
from chalicelib import translation_service

import base64
import json
import boto3

##curl --header "Content-Type: application/json" --request POST  --data '{"fromLang":"auto","toLang":"en"}' http://127.0.0.1:8000/images/german-one-way-street-sign.jpg/translate-text


#####
# chalice app configuration
#####
app = Chalice(app_name='Capabilities')
app.debug = True

#####
# services initialization
#####
storage_location = 'contentcen301061242.aws.ai'
storage_service = storage_service.StorageService(storage_location)
recognition_service = recognition_service.RecognitionService(storage_service)
translation_service = translation_service.TranslationService()


#####
# RESTful endpoints
#####
@app.route('/images', methods = ['POST'], cors = True)
def upload_image():
    """processes file upload and saves file to storage service"""
    request_data = json.loads(app.current_request.raw_body)
    file_name = request_data['filename']
    file_bytes = base64.b64decode(request_data['filebytes'])

    image_info = storage_service.upload_file(file_bytes, file_name)

    return image_info


polly_client = boto3.client('polly')

@app.route('/images/{image_id}/translate-text', methods=['POST'], cors=True)
def translate_image_text(image_id):
    """detects then translates text in the specified image"""
    request_data = json.loads(app.current_request.raw_body)
    from_lang = request_data['fromLang']
    to_lang = request_data['toLang']

    MIN_CONFIDENCE = 80.0

    text_lines = recognition_service.detect_text(image_id)

    translated_lines = []
    for line in text_lines:
        # check confidence
        if float(line['confidence']) >= MIN_CONFIDENCE:
            translated_line = translation_service.translate_text(line['text'], from_lang, to_lang)
            translated_lines.append({
                'text': line['text'],
                'translation': translated_line,
                'boundingBox': line['boundingBox']
            })

    # Read out the translated text using Polly
    for line in translated_lines:
        response = polly_client.synthesize_speech(
            Text="Original Text is {text}. Translated text is {translation[translatedText]}".format(**line),
            OutputFormat='mp3',
            VoiceId='Joanna'
        )
        # Save the audio file
        audio_file = "../Website/jamaalFile.mp3"
        with open(audio_file, 'wb') as f:
            f.write(response['AudioStream'].read())
            f.close()
        
        # Add the audio file path to the translated line
        line['audioFile'] = audio_file
        
    return translated_lines

@app.route('/images/list', methods=['GET'], cors=True)
def list_images():
    """lists all the names of images in the storage service"""
    image_names = storage_service.list_items()
    return image_names