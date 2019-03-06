import config
import socket
import select
import sys

nameDic = {"alice":"0000", "bob":"1111", "carol":"2222"}

class atm:
  def __init__(self):
    self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self.s.bind((config.local_ip, config.port_atm))
    self.name = ""
    self.sessionFlag="no session";

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
    if self.sessionFlag == "no session":
        sys.stdout.write("ATM: ")
        sys.stdout.flush()
    elif self.sessionFlag == "in session":
        sys.stdout.write("ATM (" + self.name + "):")
        sys.stdout.flush()



  #====================================================================
  # TO DO: Modify the following function to handle the console input
  #====================================================================
  def handleLocal(self,inString):
    self.sendBytes(bytes(inString, "utf-8"))
    args=inString.lower().split(" ")
    if sessionFlag =="no session":
        if args[0] == "begin-session":
            activeCard=open("Inserted.card","r")
            name = activeCard.readline().strip().lower()
            if name in nameDic:
                pin = nameDic[name]
                print("Please Enter Your PIN: ")
                enterpin = input()
                if pin == enterpin:
                    self.sessionFlag ="in session"
                    self.name = name
                else:
                    print("INVALID PIN")
                    self.sessionFlag="no session"
                    pass
            else:
                print("INVALID CARD")
                self.sessionFlag="no session"
                pass
    if sessionFlag =="in session":
        if self.name != "":
            if args[0] == "balance"::


    self.prompt()



  #====================================================================
  # TO DO: Modify the following function to handle the bank's reply
  #====================================================================
  def handleRemote(self, inBytes):
    print("From Bank: ", inBytes.decode("utf-8") )

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
            self.handleRemote(data) # call handleRemote


        # User entered a message
        elif s == sys.stdin:
          m = sys.stdin.readline().rstrip("\n")
          if m == "quit":
            return
          self.handleLocal(m) # call handleLocal


if __name__ == "__main__":
  a = atm()
  a.mainLoop()
