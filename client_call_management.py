import threading
import sys
import client_backup
import socket
import time
TIME_SLEEP = 0.1
TIME_SLEEP_USERS = 0.5
MAX_CHUNK_SIZE = 10  # for zfill - len of messages
EXIT = -1
LISTEN = 10
IP = '172.29.232.74'
LISTEN_PORT = 1000
CALL_PORT = 1001
USERS_PORT = 1002
WAIT_KEY = 1
PERSON_CALLING = 0


class Client(object):
    """
    class client Todo: write more
    """
    def __init__(self, name):
        """
        initiates
        """
        self.listen_socket = None
        self.call_socket = None
        self.users_socket = None
        self.my_name = name
        self.connected = []
        self.being_called = False  # for loop checks if being called
        self.answered_call = False  # for loop checks if call was answered
        self.answered = False  # answer from other user
        self.person_calling = ""
        self.chosen_contact = ""
        self.initiate()

    @staticmethod
    def start_socket(ip, port):
        """
        starts and returns socket
        """
        try:
            # initiate socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # connect to server
            sock.connect((ip, port))
            print("connected with ip: {} and port: {}".format(ip, port))
            return sock
        except Exception as e:
            print("Error start_socket", e)

    @staticmethod
    def receive_mes(sock):
        """
        receives and returns message from client
        """
        try:
            raw_data = sock.recv(MAX_CHUNK_SIZE)
            data = raw_data.decode()
            mes = "invalid message"
            if data.isdigit():
                mes = sock.recv(int(data)).decode()
                mes = str(mes)
            return mes
        except Exception as e:
            sock.close()
            print("Errorr in receive_mes: ", e)

    @staticmethod
    def send_mes(mes, sock):
        """
        gets chunk and sends to server
        """
        print("mes "+mes.decode())
        length = len(mes)
        data = str(length).zfill(MAX_CHUNK_SIZE).encode() + mes
        sock.send(data)

    def initiate(self):
        """
        initiates thread:
        listening for call
        """
        listen_thread = threading.Thread(target=self.listener)
        listen_thread.start()
        users_thread = threading.Thread(target=self.users)
        users_thread.start()

    def initiate_calling(self, calling):
        """
        initiates thread:
        calling
        only initiated once btn pushed
        """
        self.chosen_contact = calling
        call_thread = threading.Thread(target=self.caller)
        call_thread.start()

    def listener(self):
        """
        connects listening socket,
        waits for call
        """
        # connects listening socket:
        self.listen_socket = self.start_socket(IP, LISTEN_PORT)
        # sends name for dictionary
        self.send_mes(self.my_name.encode(), self.listen_socket)
        # gets and sets calling options
        calling_options = self.receive_mes(self.listen_socket)
        print("options listener: {}".format(calling_options))
        self.connected = calling_options.split(',')
        self.get_call()

    def users(self):
        """
        connects with users socket,
        refreshes connected every two seconds
        """
        done = False
        # connects users socket:
        self.users_socket = self.start_socket(IP, USERS_PORT)
        while not done:
            try:
                # gets and sets calling options
                calling_options = self.receive_mes(self.users_socket)
                #print("options listener: {}".format(calling_options))
                self.connected = calling_options.split(',')
                time.sleep(TIME_SLEEP_USERS)
            except socket.error as msg:
                print("socket failure: {}".format(msg))
                done = True
            except Exception as e:
                print(e)

    def get_call(self):
        """
        gets call, answers or declines
        """
        # gets person calling
        mes = self.receive_mes(self.listen_socket)
        print("get call: {}".format(mes))
        self.person_calling = str(mes).split()[PERSON_CALLING]
        self.being_called = True
        print("made being called True: {}".format(self.being_called))

    def caller(self):
        """
        checks if wants to call if so, gets options and calls
        """
        # connects calling socket:
        self.call_socket = self.start_socket(IP, CALL_PORT)
        print("yay!!!!!!!!!!!!!")
        # sends name
        self.send_mes(self.my_name.encode(), self.call_socket)
        self.send_mes(self.chosen_contact.encode(), self.call_socket)
        answer = self.receive_mes(self.call_socket)
        if answer.startswith("no"):
            print("didn't answer")
            self.answered = False
            self.call_socket.close()
        else:
            self.answered = True
            #self.start_call(self.chosen_contact)
        self.answered_call = True

    def start_call(self, calling):
        """
        starts call - if answered positive
        """
        print("yay!, starting call")
        client_backup.main(calling, self.my_name)

    def dont_answer(self):
        """
        if client doesnt want to answer call
        """
        print("got to dont answer")
        self.send_mes("N".encode(), self.listen_socket)

    def answer(self):
        """
        if client wants to answer
        """
        print("got to answer")
        self.send_mes("Y".encode(), self.listen_socket)
        self.start_call(self.person_calling)


def main(name):
    """
    check my methods
    """
    client = Client(name)
    while True:
        time.sleep(TIME_SLEEP)


if __name__ == '__main__':
    main("Noa")