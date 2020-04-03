from socket import socket
from communicator.wtf import WTF

def send_message(receiver: socket, sender: socket , data:str) -> None:
    """Send the message as string to the destination"""
    
    prev = {
        "TO": receiver.getsockname(),
        "FROM": sender.getsockname(),
        "WTF": WTF.SEND_TEXT 
        }
    
    