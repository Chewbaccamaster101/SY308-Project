import config
import socket
import select
import sys
import security

localStorage=open("ssATM.bin","rb")

key=localStorage.readline(16)

balances={
    "Alice":100,
    "Bob":100,
    "Carol":0,
}


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
    self.sendBytes(bytes(inString, "utf-8"))
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
    string=inBytes.decode("utf-8")
    args=string.split(" ")
    if args[0].lower() == "withdraw":
        try:
            if (int(args[2]) > 0):
                if(int(balances[args[1]]) - int(args[2]))<0:
                    self.sendBytes(bytes("Insufficient Balance","utf-8"))
                elif(int(balances[args[1]]) - int(args[2]))>=0:
                    balances[args[1]] = int(balances[args[1]]) - int(args[2])
                    newBal = "$" + str(args[2]) + " dispensed"
                    self.sendBytes(bytes(newBal,"utf-8"))
                elif(int(balances[args[1]]) - int(args[2]))==0:
                    balances[args[1]] = 0
                    newBal = "$" + str(args[2]) + " dispensed"
                    self.sendBytes(bytes(newBal,"utf-8"))
            else:
                self.sendBytes(bytes("Invalid withdrawal","utf-8"))
        except (KeyError, IndexError):
            self.sendBytes(bytes("User does not exist","utf-8"))
        except (ValueError):
            self.sendBytes(bytes("Withdraw must be in integers","utf-8"))
    elif args[0].lower() == "balance":
        try:
            balanceResponse="$"+str(balances[args[1]])
            self.sendBytes(bytes(balanceResponse,"utf-8"))
        except (KeyError, IndexError):
            self.sendBytes(bytes("User does not exist","utf-8"))

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
  b = bank()
  b.mainLoop()
