import os

class Config:
    def __init__(self):
        self.MAX_SEND_MESSAGE_LENGTH = os.environ.get('MAX_SEND_MESSAGE_LENGTH', 10 * 1024 * 1024)
        self.MAX_RECEIVE_MESSAGE_LENGTH = os.environ.get('MAX_RECEIVE_MESSAGE_LENGTH', 10 * 1024 * 1024) 
        