#!./venv/bin/python
# -*- coding: utf-8 -*-

import datetime
import logging
import os
import pickle
import socket
import sys
import threading
import time


class Communicator:
    """Client <---{dictionary with info of kind of the message}-- Server
        Client ----{"OK"}-> Server
        Client <---{data}-- Server
        Client ----{done thanks}-> Server
    
    """
    
    def __init__(self, port: int):
        
        self.thread_cms = threading.Thread(target=self.catch_server)  # catch message from server
        self.HOST_NAME = socket.gethostname()
        self.IP = socket.gethostbyname(self.HOST_NAME)
        self.PORT = port
        self.BUFFER_SIZE = 1024
        self._stop = False
        self.socket_recv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_recv.bind(('', self.PORT))
        
        self.lock = threading.Lock()

        self.connectors = []
        self.text = ''
        
        #logging settings
        log_file_path = "logs"
        log_filename = datetime.datetime.now().strftime("%d_%m_%Y") + '.log'
        fullname_log = os.path.join(log_file_path, log_filename)
        logging.basicConfig(format='%(asctime)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', 
                            filename=fullname_log, level=logging.DEBUG)
        #end logging settings
        
        logging.info("Communicator was been initialize")
        self.dir_files = "received_files"

    def print_text(self, text: str) -> None:
        '''Print text in a console and add the text to the variable (self.text)'''
        with self.lock:
            logging.info(self.text)
            self.text = self.text + text

    def received_text(self) -> str:
        '''Returns text that has been intercepted \n
            after calling the method, the stream is cleared
        '''
        with self.lock: # check pyqt5 thread lock
            text = self.text
            self.text = ''        
            return text

    def stop(self) -> None:
        self._stop = True
        self.socket_recv.close()
        self.socket_send.close()
        logging.info("Communicator has been stoped")

    def new_message(self) -> bool:
        '''Return True if the stream has new content, and False if if does't '''

        if len(self.text) > 0:
            return True
        else:
            return False

    def send_message(self, message: str, to: str) -> None:
        """Send the message (text) to the client via server
        
        
        """
        logging.info("sending message...")
        d = {"TO":to, "FROM":self.HOST_NAME, "FILETYPE": "str"}  
        logging.info(f"send info {d}")
        
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as ss:
            ss.sendall(pickle.dumps(d))            
            ss.recv(self.BUFFER_SIZE)
            logging.info("send message")
            ss.sendall(message.encode())
            ss.recv(1024)
            logging.info("sending the message has been completed")
        
    def send_file(self, path: str, to: str) -> None:
        """Send the file to the destination(other client) via server
        
        """
        logging.info(f"sending file {path}")
        filename = os.path.split(path)[1]
        filesize = os.path.getsize(path)
        d = {"TO":to, "FROM": self.HOST_NAME, "FILETYPE": "file",
              "FILENAME": filename, "FILESIZE": filesize}
        logging.info(f"send info {d}")
        
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as ss:
            ss.sendall(pickle.dumps(d))
            ss.recv(self.BUFFER_SIZE)
            logging.info(f"send the file")
            with open(path, "rb") as f:
                data = f.read(self.BUFFER_SIZE)
                while data:
                    ss.sendall(data)
                    data = f.read(self.BUFFER_SIZE)
            
            ss.recv(self.BUFFER_SIZE)
            logging.info("sending the file has been completed")
        
    def recv_file(self, conn: socket, d: dict) -> None:
        path = os.path.join(self.dir_files, d['FILENAME'])
        logging.info(f"Receiving file: {d['FILENAME']}")
        conn.sendall(pickle.dumps("OK"))        
        with open(d['FILENAME'], 'wb') as f:
            for i in range(0, d['FILESIZE'], self.BUFFER_SIZE):
                f.write(conn.recv(self.BUFFER_SIZE))
        logging.info(f"Receiving {d['FILENAME']} has been complete")
        conn.sendall(pickle.dumps("DONE"))
        conn.close()
        
    def recv_str(self, conn: socket) -> None:
        conn.sendall(pickle.dumps("OK"))
        
        message = conn.recv(self.BUFFER_SIZE)
                    
        message_dec = message.decode()
        self.text += message_dec
        conn.sendall(pickle.dumps("DONE"))
        conn.close()
        
    def receive(self, conn: socket) -> None:
        d = conn.recv(self.BUFFER_SIZE)
        d_l = pickle.loads(d)
        if d_l["FILETYPE"] == "str":
            self.recv_str(conn)
        elif d_l["FILETYPE"] == "file":
            self.recv_file(conn, d_l)
        
    def catch_server(self):
        
        print("Started listing")
        while not self._stop:
        #accept the server connection
            try:
                server, addr = self.socket_recv.accept()
            except OSError as e:
                logging.exception(e)
            
            log_mes = 'New connector: ' + str(server)
            logging.info(log_mes)
            threading._start_new_thread(self.receive, (server,))
                

    def connect(self, addres: str, port: int) -> None:
        """Connect to the server
        Not the recipient of the message
        
        """
        pass
        
    def start_receive(self, n_listen=5):        
        self.socket_recv.listen()
        self.thread_cms.start()

if __name__ == '__main__':
    c = Communicator(5005)  
    print('Start receive test...')
    c.start_receive()
    
    input('stop...')
    
    c.stop()
