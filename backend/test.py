import socket
import pickle
from session import Info
import sys
HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 65432  # The port used by the server
status_array = [(9,14), (20, 25), (36, 48), (64, 85)]
tmp_array = [1.5, 0.5, 0.5, 0.5, 1.5, 0.5, 0.5, 0.5, 1.5, 0.5, 0.5, 0.5, 3.0, 1.5, 0.5, 0.5, 0.5, 1.5, 0.5, 0.5, 0.5, 1.5, 0.5, 0.5, 0.5, 2.0, 1.0, 0.5, 0.5, 2.0, 1.0, 1.0, 1.0, 3.0, 1.0, 1.0, 1.0, 0.5, 0.5, 2.0, 1.0, 1.0, 1.0, 1.0, 2.0, 3.0, 1.5, 0.5, 0.5, 0.5, 1.5, 0.5, 0.5, 0.5, 1.5, 0.5, 0.5, 0.5, 3.0, 1.5, 0.5, 0.5, 0.5, 1.5, 0.5, 0.5, 0.5, 1.5, 0.5, 0.5, 0.5, 2.0, 1.0, 0.5, 0.5, 2.0, 1.0, 1.0, 1.0, 3.0, 2.0, 1.0, 0.5, 0.5, 2.0, 1.0, 1.0, 1.0, 3.0, 3.0]
sum = 0
for arr in tmp_array:
    sum += arr
print(sum)
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    start_status = True
    for status in status_array:
        
        res = Info(False, status[0])
        print(f"beat: {res.beat}, start_status: {res.is_sync}")
        
        my_bytes = pickle.dumps(res)
        print(f"test {len(my_bytes)}")
        s.sendall(my_bytes)
        s.recv(1024)

        res = Info(True, status[1])
        print(f"beat: {res.beat}, start_status: {res.is_sync}")
        
        my_bytes = pickle.dumps(res)
        print(f"test {len(my_bytes)}")
        s.sendall(my_bytes)
        s.recv(1024)
        
    
    


