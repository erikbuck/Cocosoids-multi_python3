import CommonLayers
import cocos
import pyglet
import socket
import sys
from time import sleep
from sys import stdin, exit

from PodSixNet.Connection import connection, ConnectionListener
from threading import *

class GameChatClient(ConnectionListener):
    """
    """
    def __init__(self, target):
        """ """
        super( ConnectionListener, self ).__init__()
        self.target = target
        
    def Loop(self):
        connection.Pump()
        self.Pump()

    #######################################
    ### Network event/message callbacks ###
    #######################################

    def Network_players(self, data):
        print("*** players: " + ", ".join([p for p in data['players']]))

    def Network_message(self, data):
        print(data['who'] + ": " + data['message'])

    def Network_info(self, data):
         """ """
         keep_alive_set = set()
         live_instances = CommonLayers.GameSprite.live_instances
         for info in data['info']:
            id = info['id']
            inst = None
            if not id in live_instances:
                if info['type'] == 'a':
                    inst = CommonLayers.Asteroid(id=id)
                    self.target.batch.add(inst)
                    inst.updateWithInfo(info)
                    inst.motion_vector = (0,0)
                    inst.start()
                
                elif info['type'] == 'b':
                    inst = CommonLayers.Bullet(id=id)
                    self.target.batch.add(inst)
                    inst.updateWithInfo(info)
                    inst.motion_vector = (0,0)
                    inst.start()
                
                elif info['type'] == 'p':
                    inst = CommonLayers.Player(
                        player_id=info['player_id'], id=id)
                    self.target.batch.add(inst)
                    inst.motion_vector = (0,0)
                    inst.updateWithInfo(info)
                    inst.start()
                    if CommonLayers.PlayLayer.ownID != inst.player_id:
                        inst.color = (255, 255, 0)
                    else:
                        self.target.updateLivesRemaining(
                            inst.lives_remaining)
                            
                elif info['type'] == 'e':
                    inst = CommonLayers.Explosion(id=id)
                    self.target.batch.add(inst)
                    inst.updateWithInfo(info)
                    inst.motion_vector = (0,0)
                    inst.start()
            else:
                inst = live_instances[id]
                inst.updateWithInfo(info)
            
            if inst:
                CommonLayers.GameSprite.live_instances[id] = inst
                keep_alive_set.add(id)
                
         for id in live_instances:
            if not id in keep_alive_set:
               CommonLayers.GameSprite.live_instances[id].markForDeath()

    # built in stuff

    def Network_connected(self, data):
        print("You are now connected to the server")

    def Network_error(self, data):
        print('error:', data['error'][1])
        connection.Close()

    def Network_disconnected(self, data):
        print('Server disconnected')
        exit()


class GameChatClientNetworkAction(cocos.actions.Action):
    """    
    """
    
    def __init__(self, host, port):
        """ """
        super( GameChatClientNetworkAction, self ).__init__()
        self.host = host
        self.port = port
        if not self.host:
            self.host = socket.gethostbyname(socket.gethostname())
        
        if not self.port:
            self.port = 8000
        
    def start(self):
        """ """
        self.target.clientConnection = GameChatClient(self.target)
        self.target.clientConnection.Connect((self.host, self.port))
        print("Client started")
    

    def step(self, dt):
        """ """
        self.target.clientConnection.Loop()


class ClientPlayLayer(CommonLayers.PlayLayer):
   """
   """
   def __init__( self ):
       """ """
       super( ClientPlayLayer, self ).__init__()
       self.clientConnection = None

   def fireBulletForPlayer(self, player_id):
       """ """
       self.clientConnection.Send({"action": "fireBulletForPlayer",
          "fireBulletForPlayer":''})
           
   def rotatePlayer(self, player_id, deg):
       self.clientConnection.Send({"action": "rotatePlayer",
           "rotatePlayer":deg})

   def thrustPlayer(self, player_id):
       self.clientConnection.Send({"action": "thrustPlayer",
           "thrustPlayer":''})

   def shieldPlayer(self, player_id):
      #print('shieldPlayer')
      self.clientConnection.Send({"action": "shieldPlayer",
         "shieldPlayer":''})

   def unshieldPlayer(self, player_id):
      self.clientConnection.Send({"action": "unshieldPlayer",
         "unshieldPlayer":''})


if __name__ == "__main__":
    assert False
