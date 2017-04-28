import socket,select,threading,json
import re,time

class Client(object):
  def __init__(self,serial=None,name=None,mute=True):
    self.mute = mute #whether or not to display all debug info

    #init initial vars
    self.port = None
    self.socket = None #not running until startClient is called
    self.process_thread = None
    self.ipaddr = None
    self.name = name
    self.serial = serial
    self.keepalive = False #for process thread termination
    self.awaiting_message = [[],None] #[listening for who, msg received]
    self.processFunction = None #see processMessage function

  def startClient(self,ipaddr="",port=1800):
    self.port = port
    self.ipaddr = ipaddr
    self.socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    self.socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,True)
    if not self.mute: print("Attempting to connect to %s at port %d" % (ipaddr,port))
    self.socket.connect((ipaddr,port))
    if not self.mute: print("Connected.")

    #process requests in separate thread
    self.keepalive = True #set to false to kill client connection
    self.process_thread = threading.Thread(target=self.process)
    self.process_thread.daemon = True #terminate if program terminates
    self.process_thread.start()

    if self.name is not None:
      sendMessage("{name: %s}" % (self.name))
    if self.serial is not None:
      sendMessage("{serial: %s}" % (self.serial))
    else: return self #lets user to call client = Client().startClient()
  
  def process(self):
    timeout_seconds = 1 #so select.select doesn't freeze if no message
    while self.keepalive: #process things
      rlist,_,_ = select.select([self.socket],[],[],timeout_seconds)
      for client in rlist:
        newchar = client.recv(1).decode()
        length=""
        while newchar != "~": #msg will be LENGTH~OBJ ex] "5~{}"
          length += newchar
          newchar = client.recv(1).decode()

        length = eval(length)
        obj = json.loads(client.recv(length).decode())
        if "all" in self.awaiting_message[0] or obj["sender"] in self.awaiting_message[0]:
          #was looking for message and this is the response
          self.awaiting_message[0] = []
          self.awaiting_message[1] = obj
        else:
          self.processMessage(obj)

  def awaitMessage(self,senders=["server"],callback=None):
    """awaitMessage waits for a message from someone named in the senders list. callback is the function that says what to do with this message."""
    #you can also specify senders to be all
    if type(senders) != list: senders = [senders]
    self.awaiting_message[1] = None
    self.awaiting_message[0] = senders
    
    while self.awaiting_message[0] != []: time.sleep(0.1)
    if callback is None: return self.awaiting_message[1]
    else: callback(self.awaiting_message[1])

  def sendMessage(self,msg,sendTo=[],listenFor=[],callback=None):
    """sendMessage sends a message to everyone listed in sendTo. It then waits for a response from anyone in listenFor. Callback processes the response."""
    #you can also specify sendTo or listenFor to be "all"
    if type(sendTo) != list: sendTo = [sendTo]
    if type(listenFor) != list: listenFor = [listenFor]
    jsonMSG = json.dumps({"recipients":sendTo,"message":msg})
    if not self.mute: print("sending "+jsonMSG)

    if listenFor: #setup to wait for response
      self.awaiting_message[1] = None
      self.awaiting_message[0] = listenFor

    self.socket.sendall((str(len(jsonMSG))+"~"+jsonMSG).encode())

    if listenFor and callback is None: return self.awaitMessage(senders=listenFor)
    elif listenFor: return self.awaitMessage(senders=listenFor,callback=callback)
  
  def processMessage(self,obj):
    """processMessage processes any incoming messages. 'obj' is of the form {"sender":name, "message":msg}. msg can be an object, it doesn't have to be a string"""
    if not self.mute: print(obj["sender"] + " says: " + json.dumps(obj["message"]))
    if self.processFunction is not None: self.processFunction(self,obj)


#####DEMO#####
if __name__ == "__main__":
  print("Please enter your IP address:",end="")
  ipaddr=input()
  client = Client(mute=False).startClient(port=1800)
