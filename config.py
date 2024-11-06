import os

class Config:
    def __init__(self):
        
        self.MAX_SEND_MESSAGE_LENGTH = int(os.environ.get('MAX_SEND_MESSAGE_LENGTH', 10)) * 1024 * 1024
        self.MAX_RECEIVE_MESSAGE_LENGTH = int(os.environ.get('MAX_RECEIVE_MESSAGE_LENGTH', 10)) * 1024 * 1024
        self.STT_MODEL_NAME = os.environ.get('STT_MODEL_NAME', 'base')
        self.STT_MODEL_BEAM_SIZE = int(os.environ.get('STT_MODEL_BEAM_SIZE', 5))
        