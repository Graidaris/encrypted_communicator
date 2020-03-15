#!./venv/bin/python
# -*- coding: utf-8 -*-

import datetime
import socket
import threading
import pickle

class Server:
    def __init__(self):
        self.socket_recv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_send = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.thread_catch_request = threading.Thread(target=self.__update)
        self.HOST_NAME = socket.gethostname()
        self.IP = socket.gethostbyname(self.HOST_NAME)
        self.PORT = 5005
        self.BUFFER_SIZE = 1024
        
        self.stoped = False
        
        self.connecters = []
        
        
    def set_port(self, port):
        self.PORT = port
        
    
    def start(self):        
        self.socket_recv.bind((self.IP, self.PORT))
        self.socket_recv.listen(5)
        self.thread_catch_request.start()
        self.welcome_message()
        self.__command_handler()
        
        
    def __command_handler(self):
        while not self.stoped:
            command = input()
            self.__command_executor(command)
            
            
    def welcome_message(self):
        print(
            f"Server has been started\n"
            f"Adress: {self.IP}:{self.PORT}\n"
            f"Host name: {self.HOST_NAME}"
        )
        
    
    def __command_executor(self, command):
        if command == 'stop':
            self.stop()
        elif command == 'conn':
            self.show_conn()
            
    
    def show_conn(self):
        n = 33
        print("_"*n)
        print( "| %2s | %16s | %5s |" % ("N", "IP address", "Port"))
        print("_"*n)                
        for i, c in enumerate(self.connecters):
            peer_name = c.getpeername()
            print( "| %2d | %16s | %5d |" % (i, peer_name[0], peer_name[1]))
        print("-"*n)
        
        
            
    def stop(self):
        self.stoped = True
        
        for conn in self.connecters:
            conn.close()
            
        self.socket_recv.close()
        self.socket_send.close()
        
    
    def __update(self):
        while not self.stoped:
            try:
                conn, addr = self.socket_recv.accept()
            except OSError:
                if self.stoped:
                    return
                else:
                    continue
            
            print(f"{addr} is connected")
            self.connecters.append(conn)
            threading._start_new_thread(self.__handler_data, (conn, addr))            
            
            
    def __handler_data(self, conn,  addr):
        """Handle data
        
        Format of the data:
            [Sifc.ENUM, DATA]
        
        """
        
        
        all_data = bytearray()
        while True:
            try:
                data = conn.recv(self.BUFFER_SIZE)
            except:
                self.delete_connectors([conn])
                return
            
            if not data:
                break
            
            all_data += data
        self.analyze_data(data)
        threading._start_new_thread( self.__resend, (conn, data))
            
    
    def analyze_data(self, data):
        pass
    
    
    def __resend(self, conn, data):        
        to_delete = []
        for connecter in self.connecters:
            if connecter is not conn:
                try:
                    connecter.send(data.encode())
                except:
                    to_delete.append(connecter)
        self.__delete_connectors(to_delete)
    

            
    def __delete_connectors(self, connecter):
        """
        Delete conectors from the array of connectors
        
        Args:
            param1: connecter is an array []
        """
        for con in connecter:
            try:
                self.connecters.remove(connecter)
            except:
                pass
        
    
if __name__ == "__main__":
    server = Server()
    server.start()
