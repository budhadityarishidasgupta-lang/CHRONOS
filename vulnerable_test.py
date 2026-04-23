import pickle
import os

def load_data(data):
    # CRITICAL: Insecure pickle usage
    return pickle.loads(data)

def start_server():
    api_key = 'sk-ant-1234567890abcdef' # MOCK SECRET
    os.system('ls -la') # UNSAFE SYSTEM CALL

