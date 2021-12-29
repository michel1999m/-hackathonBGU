from socket import *
from struct import *
import time
import threading
import random

Bold = "\033[1m"
Red = "\033[31;1m"
Green = "\033[32;1m"
Yellow = "\033[33;1m"
Blue = "\033[34;1m"
end = "\033[0;1m"

def generate_math():
    math_long = random.randint(2, 5)
    a = random.randint(1, 9)
    string = str(a)
    while math_long > 0:
        b = random.randint(1, 9)
        op = random.choice(['+', '-', '*', '//', '%'])
        tmp = ' ' + str(op) + ' ' + str(b)
        string += tmp
        math_long -= 1
    string += '?'
    return string


GROUP_1 = []
GROUP_2 = []
TUP = [GROUP_1, GROUP_2]
Counter_TUP = [0, 0]
lock = threading.Lock()
lock2 = threading.Lock()
MV = []
BroadcastIP = '255.255.255.255'
BroadcastPort = 13117


def threaded(connection):  # run func for threading

    string = "Please answer the following question as fast as you can:\nHow much is:\n"
    tmp = generate_math()
    string += tmp

    math_eval = eval(tmp[:len(tmp) - 1])
    to_send = string.encode('utf-8')

    counter = 0
    ClientName = ''
    gotName = False
    endTime = time.time() + 10

    # giving the client 10 sec to send his name
    ClientName, gotName = getTeamName(ClientName, connection, endTime, gotName)

    n = random.randint(1, 2)
    if gotName:
        # adding the player to his team
        addTeamName(ClientName, n)
        message = f"{Blue}Welcome to Quick Maths.\n"
        try:
            # sending the players welcome message
            connection.sendall(message.encode('utf-8'))
            connection.sendall(to_send)
        except:
            print(f"{Red}connection from client lost{end}")
            try:
                connection.close()
                return
            except:
                return
    # count pressings on the key board that the player send to the server
    counter = getKeyboardInput(connection, counter)
    # adding the count of pressing to the team of the player
    increaseCounter(counter, n)
    try:
        # send the result of the game
        connection.sendall(GameOutput().encode())
        connection.close()
    except:
        try:
            connection.close()
        except:
            pass


# adding player to his team
def addTeamName(ClientName, n):
    lock.acquire()
    if n == 2:
        TUP[1].append(ClientName)
    else:
        TUP[0].append(ClientName)
    lock.release()


# fun that adding points to the team of each player
def getKeyboardInput(connection, counter):
    # calculating points of pressing of the keyboard for 10 sec (the end of the game)
    endTime = time.time() + 10
    while time.time() < endTime:
        try:
            data = connection.recv(2048)
            data = str(data.decode('utf-8'))
            print(data)
            if data:
                counter = counter + 1
        except:
            pass
    return counter


# fun to increase the score of each player to his team
def increaseCounter(counter, n):
    # using lock to prevent the overriding of the team score.
    lock2.acquire()
    if (n == 1):
        Counter_TUP[0] = Counter_TUP[0] + counter
    else:
        Counter_TUP[1] = Counter_TUP[1] + counter
    lock2.release()


# function that get thae name of the player until getting \n
def getTeamName(ClientName, connection, endTime, gotName):
    while time.time() < endTime and not gotName:
        try:
            data = connection.recv(1)
            if data.decode('utf-8') == '\n':
                gotName = True
            else:
                ClientName = ClientName + data.decode('utf-8')
        except:
            gotName = False
    return ClientName, gotName


def Main():
    ourPort = random.randint(2000, 40000)

    # calling fun to init the TCP connection
    sock = TCPInitConnection(ourPort)
    #sock.sendall(to_send)
    # calling fun to init the UDP connection
    cs, message = UDPInitConnection(ourPort)

    try:
        sock.listen()
        while True:
            tmp_counter = 0  # thread counter
            threads = []

            # run for 10 sec and collecting players by adding them to the array of threads
            endTime = time.time() + 10
            while time.time() < endTime:
                try:
                    cs.sendto(message, (BroadcastIP, BroadcastPort))  # broadcast
                except:
                    print(f"{Red}broadcasting failed{end}")
                time.sleep(1)
                sock.settimeout(0)  # non blocking con
                try:
                    # initializing threads
                    connection, addr = sock.accept()
                    # set the connection socket non blocking
                    connection.settimeout(0)

                    t = threading.Thread(target=threaded, args=(connection,))
                    threads.append(t)
                    tmp_counter = tmp_counter + 1
                except:
                    pass
            # starting the game by stating the thread of each player
            for x in threads:
                x.start()
            for x in threads:
                x.join()

            if tmp_counter > 0:
                # print the result of the game
                print(GameOutput())
                # initializing vars before starting a new one
                Counter_TUP[0] = 0
                Counter_TUP[1] = 0
                TUP[1] = []
                TUP[0] = []
    except:
        pass


# function that formulates the output string
def GameOutput():
    toPrint = f"{Green}GROUP1\n==\n{end}"
    for x in TUP[0]:
        toPrint = toPrint + x +'\n'
    toPrint = toPrint + f"{Green}GROUP2\n==\n{end}"
    for x in TUP[1]:
        toPrint = toPrint + x +'\n'
    toPrint = toPrint + '\n'
    if Counter_TUP[0] != 0 or Counter_TUP[1] != 0:
        if Counter_TUP[0] > Counter_TUP[1]:
            toPrint = toPrint + f"{Blue}GROUP 1 WINSS WITH {end}" + str(Counter_TUP[0]) + f"{Blue} POINTS{end}" + '\n'
            for x in TUP[0]:
                toPrint = toPrint + x + '\n'
        elif Counter_TUP[0] < Counter_TUP[1]:
            toPrint = toPrint + f"{Blue}GROUP 2 WINS WITH {end}" + str(Counter_TUP[1]) + f"{Blue} POINTS{end}" + '\n'
            for x in TUP[1]:
                toPrint = toPrint + x + '\n'
        else:
            toPrint = toPrint + f"{Blue}its a DRAWWWWWW{end} " + '\n'

    return toPrint


# function that init the UDP connection that broadcast the game offer to the players
def UDPInitConnection(ourPort):
    cs = socket(AF_INET, SOCK_DGRAM)
    cs.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    cs.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
    message = pack('!IBH', 0xabcddcba, 0x2, ourPort)
    return cs, message


# function that init the TCP connection that that accepts the players clients
def TCPInitConnection(ourPort):
    # TCP
    host = gethostname()
    print(f"{Green}server started, listening on IP address{end}",gethostbyname(host))
    sock = socket(AF_INET, SOCK_STREAM)
    server_address = (host, ourPort)
    try:
        sock.bind(server_address)
    except:
        print(f"{Red}error binding{end}")
    return sock


if __name__ == '__main__':
    Main()