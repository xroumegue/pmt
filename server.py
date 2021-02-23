import threading
import copy
import socket

import drv_ftdi

HOST = '0.0.0.0'
PORT = 65432

def client_thread(board, conn, addr):

    while True:
        try:
            d = conn.recv(1024)
            if not d:
                break
        except socket.error as e:
            print("error while receiving:: " + str(e))
            break
        drv_ftdi.DATA_LOCK.acquire()
        rail_buf = copy.deepcopy(board.data_buf)
        drv_ftdi.DATA_LOCK.release()
        data = ''
        for i, d_rail in enumerate(rail_buf):
            tmp_v = d_rail['voltage'][-1][1]
            tmp_c = d_rail['current'][-1][1]
            tmp_p = tmp_v * tmp_c
            tmp = d_rail['railnumber'] + ':' + str(tmp_p)
            data = data + tmp + ";"
        try:
            conn.sendall(bytes(data, encoding='utf8'))
        except socket.error as e:
            print("error while sending:: " + str(e))
    print('Closing connection from {:s}:{:d}'.format(addr[0],addr[1]))
    conn.close()

def run_server(board, args):
    rail_data = []
    thread_process = threading.Thread(target=board.get_data)
    thread_process.start()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(10)
        while True:
            try:
                conn, addr = s.accept()
                print('Accepting connection from {:s}:{:d}'.format(addr[0],addr[1]))
                try:
                    threading.Thread(target=client_thread, args=(board, conn, addr)).start()
                except:
                    import traceback
                    traceback.print_exc()
            except socket.error as e:
                print("error while accepting connections:: " + str(e))
