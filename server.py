import threading
import copy
import socket

import drv_ftdi

HOST = '0.0.0.0'
PORT = 65432

def run_server(board, args):
    rail_data = []
    thread_process = threading.Thread(target=board.get_data)
    thread_process.start()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        conn, addr = s.accept()
        with conn:
            print('Connected by', addr)
            while True:
                d = conn.recv(1024)
                if not d:
                    drv_ftdi.FLAG_UI_STOP = True
                    break
                drv_ftdi.DATA_LOCK.acquire()
                rail_buf = copy.deepcopy(board.data_buf)
                drv_ftdi.DATA_LOCK.release()
                data = ''
                for i, d_rail in enumerate(rail_buf):
                    tmp_v = d_rail['voltage'][-1][1]
                    tmp_c = d_rail['current'][-1][1]
                    tmp_p = tmp_v * tmp_c
                    tmp = d_rail['railnumber'] + ': ' + str(tmp_p)
                    data = data + tmp + "; "
                conn.sendall(bytes(data, encoding='utf8'))
