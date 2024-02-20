import boto3

class PollyService:
    def __init__(self, storage_service):
        self.client = boto3.client('polly')
        self.bucket_name = storage_service.get_storage_location()
        
    def synthesize_speech(self, text, voice_id, file_name):
        response = self.client.synthesize_speech(
            OutputFormat = 'mp3',
            Text = text,
            TextType = 'text',
            VoiceId = voice_id
        )
        
        file_bytes = response['AudioStream'].read()
        return file_bytes
    
    def get_voices(self):
        response = self.client.describe_voices()
        return response['Voices']
    
    