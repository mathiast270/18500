

from music_manager import MusicManager
import socket
import pickle

class Info:
    def __init__(self,is_sync, beat):
        self.is_sync = is_sync
        self.beat = beat

HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)

def create_and_handle_session(sheet_path, music_xml_path,image_path):
    manager = MusicManager(sheet_path,music_xml_path,image_path)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        print("Starting Socket")
        s.bind((HOST, PORT))
        s.listen()
        conn, addr = s.accept()
        #s.sendall
        while True:
            data = conn.recv(1024)
            
            if not data:
                break
            restored_obj = pickle.loads(data)
            manager.set_sync_status(restored_obj.beat,restored_obj.is_sync)
            conn.sendall(data)
        manager.done()
            
    
