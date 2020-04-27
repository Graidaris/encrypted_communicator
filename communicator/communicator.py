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

from Crypto.PublicKey import RSA

from .config_manager import ConfigManager, DEFAULT_FILENAME as DEFAULT_CONFIG_FILENAME


class Communicator:
    """Client <---{dictionary with info of kind of the message}-- Server\n
        Client ----{"OK"}-> Server\n
        Client <---{data}-- Server\n
        Client ----{done thanks}-> Server"""
    
    
    
    def __init__(self, port: int, config_path='config.json'):
        
        self.thread_cms = threading.Thread(target=self.catch_server)  # catch message from server
        self.HOST_NAME = socket.gethostname()
        self.IP = socket.gethostbyname(self.HOST_NAME)
        self.PORT = port
        self.BUFFER_SIZE = 1024
        self._stop = False
        self.socket_recv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_recv.bind(('', self.PORT))
        
        self.lock = threading.Lock()
        
        self.priv_RSA = None
        self.pub_RSA = None

        self.connectors = []
        self.content_buffer = []
        self.config = {}
        self.config_manager = ConfigManager()
        self.init_config(config_path)
        #logging settings
        log_filename = datetime.datetime.now().strftime("%d_%m_%Y") + '.log'
        fullname_log = os.path.join(self.config['FOLDERS']["LOGING_FOLDER"], log_filename)
        logging.basicConfig(format='%(asctime)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', 
                            filename=fullname_log, level=logging.DEBUG)
        #end logging settings
        
        logging.info("Communicator was been initialize")
        
    def init_config(self, path=DEFAULT_CONFIG_FILENAME):
        """Init the configs of the communicator"""
        self.config_manager.load_config(path)
        self.config_manager.integrity()
        self.config = self.config_manager.config

    def print_content_buffer(self) -> None:
        '''Prints the content of buffer_content to the console'''
        for content in self.content_buffer:
            for key in content:
                print(f"{key}: {content[key]}", end="")
            print()

    def received_text(self) -> str:
        """Returns text that has been intercepted \n
            after calling the method, the stream is cleared"""
            
        with self.lock: # check pyqt5 thread lock
            content = self.content_buffer.copy()
            self.content_buffer.clear()
            return content.copy()

    def stop(self) -> None:
        self._stop = True
        self.socket_recv.close()
        self.config_manager.save_config(DEFAULT_CONFIG_FILENAME)
        logging.info("Communicator has been stoped")
        

    def new_message(self) -> bool:
        """Return True if the stream has new content, and False if if does't """

        if len(self.content_buffer) > 0:
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
            ss.recv(self.BUFFER_SIZE)
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
        
    def recv_file(self, conn: socket, d: dict, addr: str) -> None:
        path = os.path.join(self.config['FOLDERS']["DOWNLOAD_FILE_FOLDER_PATH"], d['FILENAME'])
        logging.info(f"Receiving file: {d['FILENAME']}")
        conn.sendall(pickle.dumps("OK"))        
        with open(path, 'wb') as f:
            for i in range(0, d['FILESIZE'], self.BUFFER_SIZE):
                f.write(conn.recv(self.BUFFER_SIZE))
        logging.info(f"Receiving {d['FILENAME']} has been complete")
        conn.sendall(pickle.dumps("DONE"))
        conn.close()
        self.content_buffer.append({"FROM":addr, "TYPE":"file", "CONTENT":path})
        
        
    def recv_str(self, conn: socket, addr: str) -> None:
        conn.sendall(pickle.dumps("OK"))
        message = conn.recv(self.BUFFER_SIZE)
        message_dec = message.decode()
        conn.sendall(pickle.dumps("DONE"))
        conn.close()
        self.content_buffer.append({"FROM":addr, "TYPE":"str", "CONTENT":message_dec})
        
    def receive(self, conn: socket, addr: str) -> None:
        d = conn.recv(self.BUFFER_SIZE)
        d_l = pickle.loads(d)
        if d_l["FILETYPE"] == "str":
            self.recv_str(conn, addr)
        elif d_l["FILETYPE"] == "file":
            self.recv_file(conn, d_l, addr)
        
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
            threading._start_new_thread(self.receive, (server,addr,))
                

    def connect(self, addres: str, port: int) -> None:
        """Connect to the server
        Not the recipient of the message
        
        """
        pass
        
    def start_receive(self, n_listen=5):        
        self.socket_recv.listen()
        self.thread_cms.start()
        
    def init_rsa_key(self):
        PUB_KEY_NAME = "pub_key.pem"
        PRIV_PKEY_NAME = "priv_key.pem"
        SIZE_RSA_KEY = 3072
        
        pub_path = os.path.join(self.config['FOLDERS']["PUBLIC_KEYS"], PUB_KEY_NAME)
        priv_path = os.path.join(self.config['FOLDERS']["PRIVAT_KEY"], PRIV_PKEY_NAME)
        if not (os.path.exists(pub_path) or os.path.exists(priv_path)):
            keyPair = RSA.generate(SIZE_RSA_KEY)
            pubKey = keyPair.publickey()
            pubKeyPEM = pubKey.exportKey()
            privKeyPEM = keyPair.exportKey()
            with open(pub_path, "wb") as f:
                f.write(pubKeyPEM)
                
            with open(priv_path, "wb") as f:
                f.write(privKeyPEM)
                
            self.pub_RSA = pubKey
            self.priv_RSA = keyPair
        else:
            with open(priv_path, "rb") as f:                
                priv_key = RSA.import_key(f.read())
            self.priv_RSA = priv_key
            self.pub_RSA = priv_key.publickey()
        

if __name__ == '__main__':
    c = Communicator(5005)
