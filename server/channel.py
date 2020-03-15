


class Channel:
    
    def __init__(self, name):
        self.members = []
        self.NAME = name
        
    def add(self, member):
        """Add a new member to the channel.
        
        Args:
            param1: address of the member
        """
        self.members.append(member)
    
    def kick(self, member):
        """Kick out a member from the channel 
        
        Args:
            param1: address of the member
        
        """
        self.members.remove(member)
    
    def destroy(self):
        """Destroy the channel
        
        """
        self.members.clear()