import socket
import struct
from threading import Thread
import time
from lib.KeyListen import *

Bold = "\033[1m"
Red = "\033[31;1m"
Green = "\033[32;1m"
Yellow = "\033[33;1m"
Blue = "\033[34;1m"
end = "\033[0;1m"

UDPPort = 13117
buffSize = 1024

def startingGameThread(sock):
    try:
        k_listener = KBHit()
        k_listener = k_listener.kbhit()
        endtime = time.time() + 10
        while time.time() < endtime:
            try:
                sock.settimeout(max(0, int(endtime - time.time())))
                intosend = k_listener.getch()
                sock.sendall(intosend.encode())
            except:
                pass
    except:
        pass


# thread that listen to the server in the game so he can print the result of the game
def printScoreResultThread(sock):
    try:
        endtime = time.time() + 10
        while time.time() < endtime:
            output = sock.recv(buffSize)
            if output:
                print(output.decode('utf-8'))
    except:
        pass


def Main():
    TEAM_NAME = f"{Yellow}Instinct\n{end}"
    print(f"{Green}Client started,listening for offer requests...\n{end}")
    # init udp connection
    client = UDPConn()
    try:
        client.bind(("", UDPPort))
    except:
        print(f"{Red}error binding{end}")

    while True:
        data1, addr = client.recvfrom(buffSize)
        host, UDP_Port = addr
        try:
            data1, data2, TCP_Port = struct.unpack('!IBH', data1)
            if data1 == 0xfeedbeef and data2 == 0x2:  # checking recieved message from broadcast
                print(f"{Green}received offer from{end}", host, f"{Green},attempting to connect...\n{end}")
                sock = TCPConn(TCP_Port, host)
                try:
                    # sending the team name
                    sock.sendall(TEAM_NAME.encode('utf-8'))
                    # calling fun start the game
                    SendDataByThread(sock)
                except:
                    print(f"{Red}server closed{end}")
                finally:
                    sock.close()
        except:
            pass


# init TCP connection with the server
def TCPConn(TCP_Port, host):
    # TCP
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (host, TCP_Port)
    try:
        sock.connect(server_address)
    except:
        print(f"{Red}connection failed{end}")
    return sock


# fun that starts the game by opining two threads on for sending, the other for lisining for the result t the end of the game
def SendDataByThread(sock):
    DataIsFound = False
    endtime = time.time() + 10

    # give the server 10 sec to give us the permition to start the game
    while time.time() < endtime and not DataIsFound:
        data = sock.recv(2048)
        print(data.decode('utf-8'))
        data = sock.recv(2048)
        # starting the game
        if data is not None:
            print(data.decode('utf-8'))
            sendingThread = Thread(target=startingGameThread, args=(sock,))
            sendingThread.start()
            sendingThread.join()

            lisenerThread = Thread(target=printScoreResultThread, args=(sock,))
            lisenerThread.start()
            lisenerThread.join()

            DataIsFound = True


# init udp connection that listen to UDP packets to get the broadcast
def UDPConn():
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    return client


if __name__ == '__main__':
    Main()
