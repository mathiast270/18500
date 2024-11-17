import socket
import pickle
from session import Info
import sys
HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 65432  # The port used by the server

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    start_status = True
    for i in range(300):
        res = Info(start_status, i)
        print(f"beat: {res.beat}, start_status: {res.is_sync}")
        
        my_bytes = pickle.dumps(res)
        print(f"test {len(my_bytes)}")
        s.sendall(my_bytes)
        s.recv(1024)
        if(i == 8):
            start_status = False
        if(i == 50):
            start_status = True

        if(i == 150):
            start_status = False
        if( i == 210):
            start_status = True
    
    


