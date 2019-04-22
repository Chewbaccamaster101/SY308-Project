import config
import socket
import select
import sys
import security

nameDic = {"Alice":"0000", "Bob":"1111", "Carol":"2222"}

localStorage=open("ssATM.bin","rb")

key=localStorage.readline(16)


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
    cipher=security.encrypt(m,key)
    print(cipher)
    cipher=b"".join(cipher)
    print(cipher)
    self.s.sendto(cipher, (config.local_ip, config.port_router))

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
    #self.sendBytes(bytes(inString, "utf-8"))
    args=inString.split(" ")
    if self.sessionFlag =="no session":
        if args[0] == "begin-session":
            activeCard=open("Inserted.card","r")
            name = activeCard.readline().strip().title()
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

            else:
                print("INVALID CARD")
                self.sessionFlag="no session"
                pass
    if self.sessionFlag =="in session":
            if args[0] == "balance":
                balanceQueryStr="balance %s" % (self.name)
                self.sendBytes(bytes(balanceQueryStr,"utf-8"))
            elif args[0] == "withdraw":
                try:
                    withdrawQueryStr="withdraw %s %s" %(self.name,args[1])
                    self.sendBytes(bytes(withdrawQueryStr,"utf-8"))
                except IndexError:
                    print("PLEASE SPECIFY AMOUNT")
                    self.prompt()
            elif args[0] == "end-session":
                self.sessionFlag="no session"
                self.prompt()
            else:
                self.prompt()

    else:
        self.prompt()





  #====================================================================
  # TO DO: Modify the following function to handle the bank's reply
  #====================================================================
  def handleRemote(self, inBytes):
    print("From Bank: ", inBytes.decode("utf-8") )
    string=inBytes.decode("utf-8")
    args=string.split(" ")
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
