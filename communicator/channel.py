


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
        try:
            self.members.remove(member)
        except ValueError:
            pass
    
    def destroy(self):
        """Destroy the channel
        
        """
        self.members.clear()