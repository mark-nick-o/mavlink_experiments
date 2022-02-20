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


# Example of TCP_IP Master Sender (loop back using internal ports)
#====================================================================

# -*- coding: utf-8 -*-
import subprocess
from sklearn.datasets import fetch_openml
import numpy as np
#import pickle
#import joblib
import os
import base64
import socket

#TCP/IP PORT
M2S_PORT = 50011
S2M_PORT = 50012
LOCALHOST = '127.0.0.1'

print('---Start TCP/IP / process comm ---')

#if os.path.exists('mnist.jb'):
#    mnist = joblib.load("mnist.jb")
#else:
#    mnist = fetch_openml('mnist_784', version=1, )
#    joblib.dump(mnist, "mnist.jb", compress=3)

# mnist.data : 70,000 784-dimensional vector data
#mnist.data = mnist.data.astype(np.float32)

#bin_data = pickle.dumps(mnist.data)     

json_msg = "{ S_ISO : 32.23, S_APERTURE : 32, S_FOCUS_MODE : 2, S_FOCUS_AREA : 13, S_STILL_CAP : 7, S_SHUT_SPEED : 30, S_EX_PRO : 10 }"
bin_data = json_msg.encode()
enc_value = base64.b64encode(bin_data)  #BASE64

proc = None

with socket.socket() as s:
    try:
        s.bind((LOCALHOST, M2S_PORT))
        s.listen()
        proc = subprocess.Popen(['python', './TCPIP_S01.py'])
        c, addr = s.accept()
        ss.req_message('$start')
        c.send(enc_value)
        c.close()
    except Exception as e:
        print('M send message:' + str(e))

with socket.socket() as r:
    r.connect((LOCALHOST, S2M_PORT))
    try:
        recv_stream = r.recv(1024 * 1024 * 1024)                                     

        #recv_data = pickle.loads(base64.b64decode(recv_stream))                      

        recv_data = base64.b64decode(recv_stream) 
        
        if (enc_value == recv_stream):
            print("Validation OK!")
            ss.req_message('$start')
        else:
            print("Different! NG!")
            proc.terminate()
            print("terminated the slave")            
    except Exception as e:
        print('M recv message:' + str(e))
        

