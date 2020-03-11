#!./venv/bin/python
# -*- coding: utf-8 -*-

import threading
import socket
import time
import sys


class Communicator:
    def __init__(self, port):
        self.thread_catch_message = threading.Thread(target=self.__catch_messages)
        self.thread_cms = threading.Thread(target=self.__catch_mfs) #catch message from server
        self.HOST_NAME = socket.gethostname()
        self.IP = socket.gethostbyname(self.HOST_NAME)
        self.PORT = port
        self.BUFFER_SIZE = 1024
        self._stop = False
        self.socket_recv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_send = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        self.connectors = []
        self.text = ''
        print("Initial communicator")
                
    def print_text(self, text):
        '''Print text in a console and add the text to the variable (self.text)'''
        print(text)
        self.text = self.text + text
            
    def received_text(self):
        '''Returns text that has been intercepted \n
            after calling the method, the stream is cleared
        '''
        text = self.text
        self.text = ''
        return text
    
    def start_listen(self):
        if self._stop: return
        
        self.print_text(f"start the server\t{self.IP}:{self.PORT} ")
        self.stop = True
        
        self.socket_recv.bind((self.IP, self.PORT))
        self.socket_recv.listen(1)       
        
        self.thread_catch_message.start()        
    
    def stop_listen(self):
        self._stop = True
        self.socket_recv.close()
        self.socket_send.close()
        
    def new_message(self):
        '''Return True if the stream has new content, and False if if does't '''
        
        if len(self.text) > 0:
            return True
        else:
            return False
    
    def __catch_messages(self):
        while not self._stop:
            try:
                conn, addr = self.socket_recv.accept()
            except OSError as e:
                print(e)
                return
                            
            self.connectors.append(addr)
            threading._start_new_thread(self.__processing_message, (conn, addr))
            
            
    def __processing_message(self, conn, addr):
        while True:
            data = conn.recv(self.BUFFER_SIZE)
            if not data:
                break
            
            data = data.decode()
            self.print_text(str(addr) + ":\t" + str(data))
                
        print(f"Connected user {addr} is closed")
        conn.close()
        
    def __catch_mfs(self):
        """Catch message from server"""
        
        while not self._stop:
            data = self.socket_send.recv(self.BUFFER_SIZE)
            if not data:
                break
            
            data = data.decode()
            print(f"From server: {data}")
    
    def send_message(self, message):
        self.socket_send.send(message.encode())
        
    def connect(self, addres, port):
        self.socket_send.connect((addres, port))
        self.thread_cms.start()
    
    
if __name__ == '__main__':
    if len(sys.argv) > 1:
        com = Communicator(int(sys.argv[1]))
        
        com.connect(com.IP,int(sys.argv[2]))
        message = None
        while message != "out":
            message = input("enter message: ")
            com.send_message(message)
    
    
    
    com.stop_listen()
    