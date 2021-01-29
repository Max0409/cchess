import socket
def tcpClient():
    host = "127.0.0.1"
    port = 9999

    s = socket.socket()
    s.connect((host, port))

    message = '1,2'
    
    s.send(message.encode())
    data = s.recv(1024)
    print("Received from server "+ str(data))
    s.close()
if __name__ == '__main__':
    tcpClient()
