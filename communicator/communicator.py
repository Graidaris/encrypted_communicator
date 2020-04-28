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

from communicator.config_manager import ConfigManager, DEFAULT_FILENAME as DEFAULT_CONFIG_FILENAME


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
        self._stop = False
        self.socket_recv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_recv.bind(('', self.PORT))
        
        self.lock = threading.Lock()
        
        self.RSA_key = None

        self.connectors = []
        self.content_buffer = []
        self.config = {}
        self.config_manager = ConfigManager()
        self.init_config(config_path)
        self.init_logging()
        
        self.BUFFER_SIZE = self.config["BUFFER_SIZE"]
        
    def create_ff(self, path, file_name="", mod='w') -> str:
        """Check if the full path to the file exists 
        and creates a path if it does not exist. Return full path.
        """
        full_path = os.path.join(path, file_name)
        if not os.path.exists(full_path):
            if not os.path.exists(path):
                os.makedirs(path)
            if file_name != "":                
                with open(full_path, mod):
                    pass
            
        return full_path
        
        
    def init_logging(self) -> None:
        """Logging settings"""
        
        log_filename = datetime.datetime.now().strftime("%d_%m_%Y") + '.log'
        path = self.config['FOLDERS']["LOGING"]
        fullname_log = self.create_ff(path, log_filename, "a+")
        logging.basicConfig(format='%(asctime)s: %(message)s', 
                            datefmt='%m/%d/%Y %I:%M:%S %p', 
                            filename=fullname_log, level=logging.DEBUG)
    
    def init_config(self, path=DEFAULT_CONFIG_FILENAME) -> None:
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
        path = os.path.join(self.config['FOLDERS']["DOWNLOAD"], d['FILENAME'])
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
        while not self._stop:
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
        
    def start_receive(self, n_listen=5) -> None:
        """Start receive information from server"""
        self.socket_recv.listen()
        self.thread_cms.start()
        
    def init_rsa_key(self) -> None:
        """Initialization RSA keys"""
        PRIV_PKEY_NAME = "priv_key.pem"
        SIZE_RSA_KEY = self.config["SIZE_RSA_KEY"]
        
        pub_path = self.config['FOLDERS']["PUBLIC_KEYS"]
        priv_path = self.config['FOLDERS']["PRIVAT_KEY"]
        
        if not os.path.exists(priv_path):
            logging.info("Generate the RSA key")
            full_pub_path = self.create_ff(pub_path)
            full_priv_path = self.create_ff(priv_path, PRIV_PKEY_NAME, 'a+')
            
            keyPair = RSA.generate(SIZE_RSA_KEY)
            privKeyPEM = keyPair.exportKey()
                
            with open(full_priv_path, "wb") as f:
                f.write(privKeyPEM)
                
            self.RSA_key = keyPair
        else:
            full_priv_path = os.path.join(priv_path, PRIV_PKEY_NAME)
            with open(full_priv_path, "rb") as f:                
                priv_key = RSA.import_key(f.read())
            self.RSA_key = priv_key