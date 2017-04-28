import socket,select,json #for socket coding
from urllib.request import urlopen #for getting public IP
import os #for getting public IP
import threading,re,numpy,pickle

class Server(object):
  connections = [] #current list of clients
  def __init__(self,mute=True):
    self.mute = mute
    #init initial vars
    self.port = None
    self.socket = None #not running until startServer is called
    self.process_thread = None
    self.ipaddr = self.getMyIP()

  def getMyIP(self):
    return re.search("\d+\.\d+\.\d+\.\d+",os.popen("ifconfig").read()).group(0)

  def startServer(self,port=1800):
    self.port = port
    self.socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    self.socket.setblocking(False) #lets select work properly I think
    self.socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,True) #enables easy server restart
    self.socket.bind(("",port)) #binds to any address the computer can be accessed by
    self.socket.listen() #start awaiting connections
    print("running server on %s @ %d" % (self.ipaddr,self.port))

    #process requests in separate thread
    self.process_thread = threading.Thread(target=self.process)
    self.process_thread.daemon = True #terminate if program terminates
    self.process_thread.start()
    return self #enables user to call server = Server().startServer()

  def getConnection(self,address=None,name=None,serial=None):
    connection = None
    if address is not None: #try to get by ipaddr/port
      for client in Server.connections:
        if client.addr == address:
          connection = client
          break
    if connection is None and name is not None: #try to get by name
      for client in Server.connections:
        if client.name == name:
          connection = client
          break
    if connection is None and serial is not None: #try to get by serial number
      for client in Server.connections:
        if client.serialnum == serial:
          connection = client
          break
    return connection #will be None if no matches

  def sendMessage(self,msg,sender="server",address=None,name=None,serial=None):
    recipient = self.getConnection(address,name,serial)
    if recipient is None:
      return False #couldn't find desired connection
    else:
      jsonMSG = json.dumps({"sender":sender,"message":msg})
      if not self.mute: print("sending " + jsonMSG)
      recipient.socket.sendall((str(len(jsonMSG))+"~"+jsonMSG).encode())
      return True #message was sent

  def process(self):
    while True: #process things forever
      clients = [self.socket]
      for client in Server.connections:
        clients.append(client.socket)

      rlist,_,_ = select.select(clients,[],[]) #reads,writes,errors
      for client in rlist:
        if client is self.socket: #new connection request
          (clientsocket,(host,port)) = self.socket.accept()
          if not self.mute: print("connected to %s @ %d" % (host,port))
          Server.connections.append(CozmoConnection((host,port),clientsocket))
        else:
          #get object representing client
          index = -1
          connection = None
          for i in range(len(Server.connections)):
            if Server.connections[i].socket==client:
              connection = Server.connections[i]
              index = i
              break
        
          #process message
          newchar = client.recv(1).decode()
          if newchar == "":
            if not self.mute: print(connection.name + " disconnected.")
            connection.socket.close()
            del(self.connections[index])
            if len(Server.connections)==0:
              CozmoConnection.count = 0 #can restart counts/naming conventions
          else:
            length=""
            while newchar != "~": #wait til read termination character
              length += newchar
              newchar = client.recv(1).decode()
            length = eval(length)
            obj = client.recv(length).decode()
            self.processMessage(connection,json.loads(obj))

  def processMessage(self,connection,obj):
    if not self.mute: print(connection.name + " says: " + json.dumps(obj))
    recipients = obj["recipients"]
    server = (recipients==[])
    msg = obj["message"]
    if "all" in recipients:
      for recip in Server.connections:
        if recip != connection:
          self.sendMessage(obj["message"],sender=connection.name,name=recip.name)
    for recip in recipients:
      if recip=="server": server = True
      else: self.sendMessage(obj["message"],sender=connection.name,name=recip,address=recip,serial=recip)

    if not server: return #job complete
    if type(msg) != str: return #server only answers string questions

    #see if client wants to change their name    
    regex=re.search("^\{name:\s*([^\}]+)\}$",msg)
    if regex is None:
      regex = re.search("^my name is (.+)$",msg.strip())

    if regex:
      name = regex.group(1)
      exists = self.getConnection(address=name,name=name,serial=name)
      if exists is not None:
        self.sendMessage("ERROR. Not unique",name=connection.name)
      else:
        connection.name = name
      return

    #see if client wants to change their serial number string
    regex=re.search("^\{serial:\s*([^\}]+)\}$",msg)
    if regex is None:
      regex=re.search("^my serial is (.+)$",msg.strip())
    
    if regex:
      num = regex.group(1)
      exists = self.getConnection(address=num,name=num,serial=num)
      if exists is not None:
        self.sendMessage("ERROR. Not unique",name=connection.name)
      else:
        connection.serialnum = name
      return

    #if client wants to know who else is connected
    regex=re.search("^who's connected\??$",msg.lower())
    if regex:
      names = []
      for client in Server.connections:
        names.append(client.name)
      self.sendMessage(str(names),name=connection.name)
      return
    
    #see if client wants to ask a question
    regex=re.search("what's\s*(\S*) ([^\?]+)\??$",msg)
    if regex: #ex] "what's my name" or "what's 2+2" or "what's cozmo2's address"
      identifier = regex.group(1)
      trait = regex.group(2)
      if identifier=="": #not asking about a cozmo
        try:
          self.sendMessage(str(eval(trait)),name=connection.name)
        except:
          self.sendMessage("ERROR",name=connection.name)
      elif identifier!="my" and (len(identifier)<2 or identifier[-2:]!="'s"): #not valid question
        self.sendMessage("ERROR",name=connection.name)
      else:
        desired=None
        if identifier=="my":
          desired = connection
        else: #find the cozmo you want
          name = identifier[:-2]
          desired = self.getConnection(address=name,name=name,serial=name)

        if desired is None:
          self.sendMessage("ERROR",name=connection.name)
        else:
          if trait=="name":
            self.sendMessage(desired.name,name=connection.name)
          elif trait=="serial number" or trait=="serial":
            self.sendMessage(str(desired.serialnum),name=connection.name)
          elif trait=="address":
            self.sendMessage(str(desired.addr),name=connection.name) #tuple of (ipaddr,port)
          else:
            self.sendMessage("ERROR",name=connection.name)
      return True
    
    #return error if couldn't process message  
    self.sendMessage("ERROR",name=connection.name)




class CozmoConnection(object):
  count=0 #for naming purposes
  def __init__(self,clientaddr,clientsocket,name=None,serialnum=None):
    self.socket = clientsocket
    self.serialnum = serialnum
    self.addr = clientaddr
    if name is None: self.name = "cozmo%d" % (CozmoConnection.count)
    else: self.name = name
    CozmoConnection.count+=1

if __name__ == "__main__": #run server if calling this program
  server = Server(mute=False).startServer(port=1800)
