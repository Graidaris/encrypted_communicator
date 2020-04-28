#!./venv/bin/python
# -*- coding: utf-8 -*-

import datetime
import socket
import threading
import pickle
import os

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
            threading._start_new_thread(self.__receive, (conn, addr))            
            
            
    def __receive(self, conn,  addr):
        """Receive data
        
        """
                
        d = conn.recv(self.BUFFER_SIZE)
        d_l = pickle.loads(d)
        if d_l["FILETYPE"] == "str":
            self.recv_str(conn)
        elif d_l["FILETYPE"] == "file":
            self.recv_file(conn, d_l)
            
            
    def send_message(self, message: str, to: str) -> None:
        """Send the message (text) to the client via server
        
        
        """
        #Client ---{dictionary with info of kind of the message}--> Server
        #Client <---{"OK"}-- Server
        #Client ----{data}-> Server
        #Client <---{done thanks}- Server
        
        d = {"TO":to, "FROM":self.HOST_NAME, "FILETYPE": "str"}          
        self.socket_send.sendall(pickle.dumps(d))        
        self.socket_send.recv(self.BUFFER_SIZE)        
        self.socket_send.sendall(message.encode())
        self.socket_send.recv(self.BUFFER_SIZE)
        
        
    def send_file(self, path: str, to: str) -> None:
        """Send the file to the destination(other client) via server
        
        """
        
        filename = os.path.split(path)[1]
        filesize = os.path.getsize(path)
        d = {"TO":to, "FROM": self.HOST_NAME, "FILETYPE": "file",
              "FILENAME": filename, "FILESIZE": filesize}
        
        self.socket_send.sendall(pickle.dumps(d))
        self.socket_send.recv(self.BUFFER_SIZE)
        
        with open(path, "rb") as f:
            data = f.read(self.BUFFER_SIZE)
            while data:
                self.socket_send.sendall(data)
                data = f.read(self.BUFFER_SIZE)
        
        self.socket_send.recv(self.BUFFER_SIZE)
        
            
    def recv_file(self, conn: socket, d: dict) -> None:
        path = os.path.join(self.dir_files, d['FILENAME'])
        conn.sendall(pickle.dumps("OK"))
        
        with open(d['FILENAME'], 'wb') as f:
            for _ in range(0, d['FILESIZE'], self.BUFFER_SIZE):
                f.write(conn.recv(self.BUFFER_SIZE))
                
        conn.sendall(pickle.dumps("DONE"))
        
    def recv_str(self, conn: socket) -> None:
        conn.sendall(pickle.dumps("OK"))
        
        while True:
            message = conn.recv(self.BUFFER_SIZE)
            if not message:
                break
        
        message_dec = message.decode()
        conn.sendall(pickle.dumps("DONE"))    
    
    
    
    def __resend(self, conn, data):        #need to complete
        to_delete = []
        for connecter in self.connecters:
            if connecter is not conn:
                try:
                    if data["FILETYPE"] == "str":
                        self.send_message(data['MESSAGE'], data['TO'])
                    elif data["FILETYPE"] == "file":
                        self.send_file()
                    
                    #connecter.send(data.encode())
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
