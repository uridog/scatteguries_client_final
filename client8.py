# Python program to translate
# speech to text and text to speech

import socket
import ssl
import threading as th

import speech_recognition as sr

from enter_screen1 import Ui_startWindow, show_win
from log_in_screen1 import Ui_LogInWindow, show_window
from ready_screen import Ui_readyWindow, show_ready_window
from sign_in_screen import Ui_signUpWindow, show_sign_window
from game_screen1 import Ui_gameWindow, show_game

context = ssl.create_default_context()
# Set the context to not verify the server's SSL/TLS certificate
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE


class Client:

    def __init__(self, server_socket):
        self.socket = server_socket
        self.screen_state = -1
        self.first_name = ""
        self.last_name = ""
        self.username = ""
        self.password = ""
        self.client_ready = False
        self.client_singed = False
        self.game_start = False


def create_msg(data1, cmd1):
    data_len = len(data1)
    data_len_len = len(str(data_len))
    data_len = str(data_len)
    for i in range(4 - data_len_len):
        data_len = "0" + data_len
    return cmd1 + data_len + data1


def handle_cmd(client_socket):
    cmd = client_socket.recv(2).decode()
    return cmd


def handle_data(client_socket):
    cmd = client_socket.recv(2).decode()
    data_len_received = client_socket.recv(4).decode()
    data_received = client_socket.recv(int(data_len_received)).decode()
    return data_received, cmd


def voice_to_text():
    global MyText
    r = sr.Recognizer()
    try:
        # use the microphone as source for input.
        with sr.Microphone() as source2:

            # wait for a second to let the recognizer
            # adjust the energy threshold based on
            # the surrounding noise level
            r.adjust_for_ambient_noise(source2, duration=0.2)

            # listens for the user's input
            try:
                audio2 = r.listen(source2, 5, 3)
                MyText = r.recognize_google(audio2)
            except:
                pass
            # Using google to recognize audio


    except sr.RequestError as e:
        pass

    except sr.UnknownValueError:
        pass


categories_milon = {
    "country": 0,
    "capital": 1,
    "boy": 2,
    "movie": 3,
    "animal": 4,
    "fruit/vegetable": 5,
    "household item": 6,
}
ans = " "
MyText = ""
buf = 1024
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('127.0.0.1', 8820))
s = context.wrap_socket(s, server_hostname='127.0.0.1')
socket_running = True
client8 = Client(s)
start_window = Ui_startWindow(client8)

round_num = 0

try:
    show_win(start_window)
except:
    pass

while client8.screen_state == -1:
    pass
if client8.screen_state == 0:
    sign_in_window = Ui_signUpWindow(client8)
    try:
        e = th.Thread(target=show_sign_window, args=(sign_in_window,))
        e.start()
    except:
        pass
    while client8.username == "":
        pass
    userInfo = client8.username + " " + client8.first_name + " " + client8.last_name + " " + client8.password
    s.send(create_msg(userInfo, "01").encode())
    current_username = client8.username
    while handle_cmd(s) == "20":
        sign_in_window.username_taken.show()
        while client8.username == current_username:
            pass
        userInfo = client8.username + " " + client8.first_name + " " + client8.last_name + " " + client8.password
        s.send(create_msg(userInfo, "01").encode())
    client8.client_singed = True
elif client8.screen_state == 1:
    log_in_window = Ui_LogInWindow(client8)
    try:
        e = th.Thread(target=show_window, args=(log_in_window,))
        e.start()
    except:
        pass
    while client8.username == "":
        pass
    userInfo = client8.username + " " + client8.password
    old_username = client8.username
    old_password = client8.password
    s.send(create_msg(userInfo, "02").encode())
    cmd = handle_cmd(s)
    while cmd == "23" or cmd == "24":
        log_in_window.label_2.show()
        while client8.username == old_username and client8.password == old_password:
            pass
        userInfo = client8.username + " " + client8.password
        s.send(create_msg(userInfo, "02").encode())
        cmd = handle_cmd(s)
    client8.client_singed = True
ready_window = Ui_readyWindow(client8)
try:
    w = th.Thread(target=show_ready_window, args=(ready_window,))
    w.start()
except:
    pass
while socket_running:
    client8.client_ready = False
    round_num = 0
    client8.screen_state = 2
    client8.game_start = False
    while client8.client_ready is False:
        pass
    s.send(create_msg(client8.username, "03").encode())
    client8.screen_state = 3
    game_window = Ui_gameWindow(client8)
    try:
        t1 = th.Thread(target=show_game, args=(game_window,))
        t1.start()
    except:
        pass
    while round_num < 3:
        if round_num == 0:
            while game_window.opened is False:
                pass
            try:
                t3 = th.Thread(target=game_window.waiting_for_players)
                t3.start()
            except:
                pass
        round_num += 1
        # try:
        #     t1 = th.Thread(target=game_window.start_round)
        #     t1.start()
        # except:
        #     pass
        letter_recieved, cmd = handle_data(s)
        while "11" not in cmd:
            letter_recieved, cmd = handle_data(s)
        client8.game_start = True
        letter = letter_recieved
        game_window.set_letter(round_num, letter)
        game_window.game_table.update()
        ans = " "
        while cmd != "10":
            MyText = " "
            voice_to_text()
            s.send(create_msg(MyText, "04").encode())
            ans, cmd = handle_data(s)
            if cmd == "13":
                ans_list = ans.split(":")
                cat_list = ans.split("?")
                for i in range(int(len(ans_list) / 2)):
                    # table in row round num, coloum category dictionary = ans list 1+2i
                    game_window.insert_value(categories_milon[cat_list[1 + 2 * i]], round_num, ans_list[1 + 2 * i])
                    game_window.game_table.update()

        s.send(create_msg("game end", "05").encode())
    game_window.continue_button.show()
    while client8.screen_state == 3:
        pass
    ready_window.ready_button.show()
    ready_window.waiting_text.hide()
    ready_window.dot1.hide()
    ready_window.dot2.hide()
    ready_window.dot3.hide()
