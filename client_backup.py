import sys
import threading
import socket
import numpy as np
import cv2 as cv
import time
from winreg import *
#from constants import *
import pyaudio
VALUES_COUNT = 2
IP = "172.29.225.45"  # IP ADDRESS
SEND_VIDEO_PORT = 1114
RECEIVE_VIDEO_PORT = 1113
SEND_AUDIO_PORT = 1111
RECEIVE_AUDIO_PORT = 1112
TEN_LISTENERS = 10  # AMOUNT OF LISTENERS
FOUR_BYTES = 4  # for self.my_socket.recv
PARTS = 1024
HEADER_LENGTH = 4
BUF = 512
WIDTH = 640
HEIGHT = 480
RANGE_START = 0
CAPTURE = 0
TIME_SLEEP = 0.1
WID = 3
HIGH = 4
WAIT_KEY = 1
END = 0
MAX_CHUNK_SIZE = 10  # for zfill - len of messages
FORMAT = pyaudio.paInt16  # audio format
CHANNELS = 1  # num of channels for audio
RATE = 44100  # audio send rate
chunk = CHUNK = 1024  # audio chunk size
EXIT = -1


class Client(object):
    """
    class client Todo: write more
    """
    def __init__(self, call_name, my_name):
        """
        todo: comment
        """
        # ip, port = self.registry_values()
        self.receive_video_socket = None
        self.send_video_socket = None
        self.receive_audio_socket = None
        self.send_audio_socket = None
        self.my_name = my_name  # "noa"
        self.call_name = call_name  # "amir"
        self.lock = threading.Lock()

        self.voice_device = pyaudio.PyAudio()

        self.voice_stream = self.voice_device.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                                                   frames_per_buffer=chunk, input=True, output=True)
        self.initiate_threads()

    def initiate_threads(self):
        """
        sends call to server
        starts thread that sends video
        """
        receive_audio_thread = threading.Thread(target=self.receive_audio)
        receive_audio_thread.start()
        send_audio_thread = threading.Thread(target=self.send_audio)
        send_audio_thread.start()
        receive_video_thread = threading.Thread(target=self.receive_video)
        receive_video_thread.start()
        send_video_thread = threading.Thread(target=self.send_video)
        send_video_thread.start()

    def send_video(self):
        """
        sends video to server
        """
        self.send_video_socket = self.start_socket(IP, SEND_VIDEO_PORT)
        self.send_chunk(self.call_name.encode(), self.send_video_socket)
        mes = self.receive_mes(self.send_video_socket)
        print(mes)
        mes = self.receive_mes(self.send_video_socket)
        print(mes)
        while mes == "wait":
            time.sleep(TIME_SLEEP)
            mes = self.receive_mes(self.send_video_socket)
            print(mes)
        # print("here send")
        cap = cv.VideoCapture(CAPTURE)
        cap.set(WID, WIDTH)
        cap.set(HIGH, HEIGHT)
        code = 'start'
        code = ('start' + (BUF - len(code)) * 'a').encode('utf-8')
        try:
            while cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    self.send_chunk(code, self.send_video_socket)
                    data = frame.tobytes()
                    for i in range(RANGE_START, len(data), BUF):
                        self.send_chunk(data[i:i + BUF],
                                        self.send_video_socket)
                    time.sleep(TIME_SLEEP)
                else:
                    break
        except ConnectionAbortedError as e:
            print("exception send video")
            self.send_video_socket.close()

    @staticmethod
    def send_chunk(chnk, sock):
        """
        gets chunk and sends to server
        """
        length = len(chnk)
        data = str(length).zfill(MAX_CHUNK_SIZE).encode() + chnk
        sock.send(data)

    def receive_chunk(self):
        """
        gets chunk from server
        """
        raw_chunk_size = b''
        raw_chunk_size_to_get = MAX_CHUNK_SIZE
        while len(raw_chunk_size) < raw_chunk_size_to_get:
            raw_chunk_size += self.receive_video_socket.recv(
                raw_chunk_size_to_get - len(raw_chunk_size))
        try:
            chunk_size = int(raw_chunk_size.decode())
        except Exception as e:
            print('raw chunk size is {} its length is {}'
                  .format(raw_chunk_size, len(raw_chunk_size)))
            print("exception receive chunk 1: {}".format(e))
        left = chunk_size
        chunk = b''
        try:
            while left > END:
                chunk += self.receive_video_socket.recv(left)
                left = left - len(chunk)
            return chunk
        except Exception as e:
            print("exception receive chunk 1: {}".format(e))
            self.receive_video_socket.close()

    def receive_video(self):
        """
        receives and shows video from server
        """
        self.receive_video_socket = self.start_socket(IP, RECEIVE_VIDEO_PORT)
        self.send_chunk(self.my_name.encode(), self.receive_video_socket)
        print(self.receive_mes(self.receive_video_socket))
        try:
            code = b'start'
            num_of_chunks = WIDTH * HEIGHT * WID / BUF
            while True:
                chunks = []
                start = False
                while len(chunks) < num_of_chunks:
                    chunk = self.receive_chunk()
                    if start:
                        chunks.append(chunk)
                    elif chunk.startswith(code):
                        start = True

                byte_frame = b''.join(chunks)
                frame = np.frombuffer(
                    byte_frame, dtype=np.uint8).reshape(HEIGHT, WIDTH, WID)

                cv.imshow('recv', frame)
                if cv.waitKey(WAIT_KEY) & 0xFF == ord('q'):
                    break

            self.receive_video_socket.close()
            cv.destroyAllWindows()

        except Exception as e:
            self.receive_video_socket.close()
            cv.destroyAllWindows()
            print("Error receive_video:", e)
            sys.exit(EXIT)

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
            print("Error receive_mes: ", e)

    @staticmethod
    def start_socket(ip, port):
        """
        starts and returns socket
        """
        try:
            # initiate socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # connect to server
            print("ip =", ip)
            print("port =", port)
            sock.connect((ip, port))
            return sock
        except Exception as e:
            print("Error start_socket", e)
            #exit()

    def receive_audio(self):
        """
        receives and plays audio
        """
        print("got to receive audio")
        self.receive_audio_socket = self.start_socket(IP, RECEIVE_AUDIO_PORT)
        self.send_chunk(self.my_name.encode(), self.receive_audio_socket)
        print(self.receive_mes(self.receive_audio_socket))

        print("receive stream made")
        i = 0
        done = False
        try:
            while not done:
                i += 1
                data = self.receive_audio_socket.recv(CHUNK)  # gets audio chunk
                print("got audio chunk number {} of length {}".format(i, len(data)))
                self.lock.acquire()
                self.voice_stream.write(data)  # plays
                self.lock.release()
                # if len(data) == 0:
                  #   done = True
                #print("wrote chunk #{}".format(i))
        except KeyboardInterrupt:
            print("exception receive audio")
            pass
        print('Shutting down')
        self.close_all()
        # stream_receive.close()
        # p_receive.terminate()

    def send_audio(self):
        """
        records and sends audio to server
        """
        print("got to send audio")
        self.send_audio_socket = self.start_socket(IP, SEND_AUDIO_PORT)
        self.send_chunk(self.call_name.encode(), self.send_audio_socket)
        mes = self.receive_mes(self.send_audio_socket)
        print(mes)
        mes = self.receive_mes(self.send_audio_socket)
        print(mes)
        while mes == "wait":
            time.sleep(TIME_SLEEP)
            mes = self.receive_mes(self.send_audio_socket)
            print(mes)
        # p_send = pyaudio.PyAudio()  # Create an interface to PortAudio
        print('Recording...')

        # stream_send = p_send.open(format=FORMAT, channels=CHANNELS, rate=RATE, frames_per_buffer=chunk, input=True,
        #                          output=False)
        print("send stream opened")
        try:
            # Store data in chunks for 3 seconds
            done = False
            num = 1
            while not done:
                self.lock.acquire()
                data = self.voice_stream.read(chunk)   # records chunk
                self.lock.release()
                print("chunk {} recorded".format(num))
                self.send_audio_socket.send(data)  # sends chunk
                print("chunk {} sent".format(num))
                num += 1
            print('Finished recording')
        except Exception as e:
            print("sending audio error: {}".format(e))
        self.close_all()
        self.voice_stream.close()
        self.voice_device.terminate()

    def close_all(self):
        """
        closes all sockets and connections
        """
        self.receive_video_socket.close()
        self.send_video_socket.close()
        self.receive_audio_socket.close()
        self.send_audio_socket.close()


def main(call_name, my_name):
    """
    check my methods
    """
    client = Client(call_name, my_name)
    while True:
        time.sleep(TIME_SLEEP)


if __name__ == '__main__':
    main("noa", "amir")
