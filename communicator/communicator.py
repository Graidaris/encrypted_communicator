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
    """
    
    """
    
    def __init__(self, port: int):
        
        self.thread_cms = threading.Thread(target=self.catch_server)  # catch message from server
        self.HOST_NAME = socket.gethostname()
        self.IP = socket.gethostbyname(self.HOST_NAME)
        self.PORT = port
        self.BUFFER_SIZE = 1024
        self._stop = False
        self.socket_recv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_send = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        self.lock = threading.Lock()

        self.connectors = []
        self.text = ''
        
        #logging settings
        log_file_path = "logs"
        log_filename = datetime.datetime.now().strftime("%d_%m_%Y") + '.log'
        fullname_log = os.path.join(log_file_path, log_filename)
        logging.basicConfig(filename=fullname_log, level=logging.DEBUG)
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

    def new_message(self) -> bool:
        '''Return True if the stream has new content, and False if if does't '''

        if len(self.text) > 0:
            return True
        else:
            return False

    def __catch_messages(self) -> None:
        while not self._stop:
            try:
                conn, addr = self.socket_recv.accept()
            except OSError as e:
                print(e)
                return

            self.connectors.append(addr)
            threading._start_new_thread(
                self.__processing_message, 
                (conn, addr)
            )

    def __processing_message(self, conn: socket, addr: str) -> None:
        while True:
            data = conn.recv(self.BUFFER_SIZE)
            if not data:
                break

            data = data.decode()
            self.print_text(str(addr) + ":\t" + str(data))

        print(f"Connected user {addr} is closed")
        conn.close()

    def __catch_mfs(self) -> None:
        """Catch message from server"""

        while not self._stop:
            data = self.socket_recv.recv(self.BUFFER_SIZE)
            if not data:
                break

        threading._start_new_thread(
            self.__processing_mfs, 
            (data,)
        )
            
    def __processing_mfs(self, data) -> None:
        """Processing data from the server
        Dictionary: {"FROM":from, "TO":to, "WTF":wtf}
        wtf is a like enum File, Text or something else        
        """
        #Need something for identificate the kind of a message
        #send readiness to the server like "U can send me the data"
        #Client <---{dictionary with info of kind of the message}-- Server
        #Client ----{"OK"}-> Server
        #Client <---{data}-- Server
        #Client ----{done thanks}-> Server
        
        pass

    def send_message(self, message: str, to: str) -> None:
        """Send the message (text) to the client via server
        
        
        """
        #Client ---{dictionary with info of kind of the message}--> Server
        #Client <---{"OK"}-- Server
        #Client ----{data}-> Server
        #Client <---{done thanks}- Server
        logging.info("sending message...")
        d = {"TO":to, "FROM":self.HOST_NAME, "FILETYPE": "str"}  
        logging.info(f"send info {d}")
        self.socket_send.sendall(pickle.dumps(d))
        
        self.socket_send.recv(self.BUFFER_SIZE)
        logging.info("send message")
        self.socket_send.sendall(message.encode())
        self.socket_send.recv()
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
        self.socket_send.sendall(pickle.dumps(d))
        self.socket_send.recv(self.BUFFER_SIZE)
        logging.info(f"send the file")
        with open(path, "rb") as f:
            data = f.read(self.BUFFER_SIZE)
            while data:
                self.socket_send.sendall(data)
                data = f.read(self.BUFFER_SIZE)
        
        self.socket_recv.recv(self.BUFFER_SIZE)
        logging.info("sending the file has been completed")
        
    def recv_file(self, conn: socket, d: dict) -> None:
        path = os.path.join(self.dir_files, d['FILENAME'])            
        
        conn.sendall(pickle.dumps("OK"))
        with open(d['FILENAME'], 'wb') as f:
            for i in range(0, self.BUFFER_SIZE):
                f.write(conn.recv(self.BUFFER_SIZE))
                
        conn.sendall(pickle.dumps("DONE"))
        
    def recv_str(self, conn: socket) -> None:
        conn.sendall(pickle.dumps("OK"))
        while True:
            message = conn.recv(self.BUFFER_SIZE)
            if not message:
                break
            
        message_dec = message.decode()
        self.text += message_dec
        conn.sendall(pickle.dumps("DONE"))
        
    def receive(self, conn: socket) -> None:
        d = conn.recv(self.BUFFER_SIZE)
        d_l = pickle.loads(d)
        if d_l["FILETYPE"] == "str":
            pass
        elif d_l["FILETYPE"] == "file":
            pass
        
    def catch_server(self):
        
        while not self.stop:
        #accept the server connection
            try:
                server, addr = self.socket_recv.accept()
            except OSError as e:
                logging.exception(e)
                
            threading._start_new_thread(self.receive, (server,))
    
        

    def connect(self, addres: str, port: int) -> None:
        """Connect to the server
        Not the recipient of the message
        
        """
        self.socket_send.connect((addres, port))
        self.thread_cms.start()
        
    def start_listen(self) -> None:
        """Start listen port for receive data from the server.
        
        """
        self.thread_cms.start()
        


if __name__ == '__main__':
    if len(sys.argv) > 1:
        com = Communicator(int(sys.argv[1]))

        com.connect(com.IP, int(sys.argv[2]))
        message = None
        while message != "out":
            message = input("enter message: ")
            #com.send_message(message)

        com.stop()
