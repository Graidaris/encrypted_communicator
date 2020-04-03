from enum import Enum

class WTF(Enum):
    """Send information from client
    
    What kind of messages did the server recieved 
    
    """
    
    CREATE_ROOM = 1
    PRIVAT_MESSAGE = 2
    SEND_TEXT = 3
    SEND_FILE = 4
    PART_FILE = 5
    END_FILE = 6