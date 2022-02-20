# to kill all python zombies use ---> sudo pkill python

# Example of TCP_IP Slave (loopback using internal ports)
#===========================================================

#
# KooSimpleSync.py
#=================

import socket
import time

REQ_PORT = 50001
ACK_PORT = 50002

class ss():
    def req_message(msg, port=REQ_PORT):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            for send_count in range(3):
                s.sendto(msg.encode(), ('127.0.0.1', REQ_PORT))
                time.sleep(0.0001)  # Abount 16 milli sec
            s.close()

    def wait_message(msg, port=REQ_PORT):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as r:
            r.bind(('127.0.0.1', port))
            while True:
                data, addr = r.recvfrom(1024)
                if data.decode() == msg:
                    time.sleep(0.0001) # Abount 16 milli sec
                    break
            r.close()
    
#!/usr/bin/env python
# -*- coding: utf-8 -*-
#import pickle
import base64
import sys
import socket

#TCP/IP PORT
M2S_PORT = 50011
S2M_PORT = 50012
LOCALHOST = '127.0.0.1'
CHUNK_SIZE = 8 * 1024

recv_stream = None
recv_data = None
s = socket.socket()
s.bind((LOCALHOST, S2M_PORT))
s.listen()
packet = 0
with socket.socket() as r:
    print("\033[31m Slave Connects \033[0m")
    r.connect((LOCALHOST, M2S_PORT))
    try:
        ss.wait_message('$start')                                          # Master Process
        recv_stream = r.recv(1024 * 1024 * 1024)                           # CHUNK
        #recv_data = pickle.loads(base64.b64decode(recv_stream))
        recv_data = base64.b64decode(recv_stream)
    except Exception as e:
        print('S recv message:' + str(e))

    print(f" the data we got was {recv_data.decode('ascii')} \033[33m we send it back for validation \033[0m")
   
    #bin_data = pickle.dumps(recv_data)
    
    # use this if you want to test error sent back
    # recv_data = "SHITE".encode('ascii')
    #
    bin_data = recv_data
    enc_value = base64.b64encode(bin_data)

    try:
        c, addr = s.accept()
        c.send(enc_value)
        c.close()
    except Exception as e:
        print('S send message:' + str(e))

    packet += 1
print("\033[32m Slave Completed send back now waiting for a validation ACK from the master \033[0m")  
ss.wait_message('$start')                                          # Master Process  
print("\033[32m Slave Completed ACK it was valid \033[0m")
    
