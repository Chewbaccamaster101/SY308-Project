import config
import socket
import select
import sys

balances={
    "Alice":100,
    "Bob":100,
    "Carol":0,
}
ss = open("ssatm.bin","rb")
N = ss.readline().strip()
d = ss.readline().strip()
e = ss.readline().strip()
ss.close()




class bank:
  def __init__(self):
    self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self.s.bind((config.local_ip, config.port_bank))
 
  def __del__(self):
    self.s.close()

  def sendBytes(self, m):
    self.s.sendto(m, (config.local_ip, config.port_router))

  def recvBytes(self):
      data, addr = self.s.recvfrom(config.buf_size)
      if addr[0] == config.local_ip and addr[1] == config.port_router:
        return True, data
      else:
        return False, bytes(0)

  #====================================================================
  # TO DO: Modify the following function to output prompt properly
  #====================================================================
  def prompt(self):
    sys.stdout.write("BANK: ")
    sys.stdout.flush()


  #====================================================================
  # TO DO: Modify the following function to handle the console input
  #====================================================================
  def handleLocal(self,inString):
    inString = int.from_bytes(msg, 'big')
    inString = pow(inString, e, N)
    self.sendBytes(inString)
    args=inString.split(" ")
    if args[0] == "deposit":
        try:
            balances[args[1].title()]+=float(args[2])
            print("$%d added to %s's account" % (float(args[2]),args[1].title()))
        except (ValueError,IndexError,KeyError):
            print("invalid amount entered")
    elif args[0] == "balance":
        try:
            print(balances[args[1].title()])
        except (KeyError, IndexError):
            print("User does not exist")
    self.prompt() 


  #====================================================================
  # TO DO: Modify the following function to handle the atm request 
  #====================================================================
  def handleRemote(self, inBytes):
    print("\nFrom ATM: ", inBytes.decode("utf-8") )
    string=inBytes.decode("utf-8"))
    args=string.split(" ")
    if args[0].lower() == "withdraw":
        pass
    elif args[0],lower() == "balance": 
        pass
    self.prompt() 
 

  def mainLoop(self):
    self.prompt()
  
    while True:
      l_socks = [sys.stdin, self.s]
           
      # Get the list sockets which are readable
      r_socks, w_socks, e_socks = select.select(l_socks, [], [])
           
      for s in r_socks:
        # Incoming data from the router
        if s == self.s:
          ret, data = self.recvBytes()
          if ret == True:
            D = pow(data, d, N)
            data = D.to_bytes( (D.bit_length()//8) + 1, 'big')
            self.handleRemote(data) # call handleRemote 
                                 
        # User entered a message
        elif s == sys.stdin:
          m = sys.stdin.readline().rstrip("\n")
          if m == "quit": 
            return
          self.handleLocal(m) # call handleLocal
        

if __name__ == "__main__":
  b = bank()
  b.mainLoop()

