import cocos
import socket
import sys
from time import sleep, localtime
from weakref import WeakKeyDictionary
from PodSixNet.Server import Server
from PodSixNet.Channel import Channel

class GameClientChannel(Channel):
    """
    This entire class has been added.
    This is the server representation of a single connected client.
    """
    def __init__(self, *args, **kwargs):
        self.nickname = "anonymous"
        Channel.__init__(self, *args, **kwargs)
        self.commands = []
    
    def Close(self):
        self._server.DelPlayer(self)

    ##################################
    ### Network specific callbacks ###
    ##################################

    def Network_message(self, data):
        self._server.SendToAll({"action": "message",
            "message": data['message'],
            "who": self.nickname})

    def Network_nickname(self, data):
        self.nickname = data['nickname']
        self._server.SendPlayers()

    def Network_rotatePlayer(self, data):
        self.commands.append(data)

    def Network_thrustPlayer(self, data):
        self.commands.append(data)

    def Network_shieldPlayer(self, data):
        self.commands.append(data)

    def Network_unshieldPlayer(self, data):
        self.commands.append(data)

    def Network_fireBulletForPlayer(self, data):
        self.commands.append(data)


class GameChatServer(Server):
    """
        This entire class has been added.
        This is the network server itself.
    """
    channelClass = GameClientChannel

    def __init__(self, *args, **kwargs):
        Server.__init__(self, *args, **kwargs)
        self.client_channels = WeakKeyDictionary()
        print('Server launched')

    def Connected(self, channel, addr):
        self.AddPlayer(channel)

    def AddPlayer(self, player):
        print("New Player" + str(player.addr))
        self.client_channels[player] = True
        self.SendPlayers()

    def DelPlayer(self, player):
        print("Deleting Player" + str(player.addr))
        del self.client_channels[player]
        self.SendPlayers()

    def SendPlayers(self):
        self.SendToAll({"action": "players",
            "players": [p.nickname for p in self.client_channels]})

    def SendToAll(self, data):
        [p.Send(data) for p in self.client_channels]


class GameChatServerNetworkAction(cocos.actions.Action):
    """
    This entire class has been added
    """
    
    def __init__(self):
        """ """
        super( GameChatServerNetworkAction, self ).__init__()
        self.chat_server = None
    
    def start(self):
        """ """
        host = socket.gethostbyname(socket.gethostname())
        port = 8000
        self.chat_server = GameChatServer(localaddr=(host, port))
    
    def step(self, dt):
        """ """
        for channel in self.chat_server.client_channels:
            # Is this thread safe?!?
            if not channel.addr[0] in self.target.players:
                self.target.addPlayer(channel.addr[0])
            
            commands = channel.commands
            for command in commands:
                if command['action'] == 'rotatePlayer':
                    deg = command['rotatePlayer']
                    self.target.rotatePlayer(channel.addr[0], deg)
                elif command['action'] == 'thrustPlayer':
                    self.target.thrustPlayer(channel.addr[0])
                elif command['action'] == 'shieldPlayer':
                    self.target.shieldPlayer(channel.addr[0])
                elif command['action'] == 'unshieldPlayer':
                    self.target.unshieldPlayer(channel.addr[0])
                elif command['action'] == 'fireBulletForPlayer':
                    self.target.fireBulletForPlayer(channel.addr[0])
                else:
                    print('Error: Unknown command,', command,\
                        'from client,', channel)

            channel.commands = [] # Is this thread sage?!?
    
        new_info = self.target.getInfo()
        self.chat_server.SendToAll({"action": "info",
            "info":new_info})
        self.chat_server.Pump()
