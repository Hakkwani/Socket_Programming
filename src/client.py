# -*- coding: utf-8 -*- 
import tkinter
import socket
from threading import Thread
import os

IP = ""
PORT = 0
CONNECTING = False

direc = os.path.dirname(os.path.realpath(__file__))
direc = '/'.join(direc.split('/')[:-1]) + '/upload/'

def putFileHeader(filename): 
    f = open(direc + filename, 'r+')
    content = f.read()
    f.seek(0,0)
    f.write('[F]' + filename + '\n' + content)
    f.close()
    return

def sendFile(filename):
    f = open(direc + filename, 'rb')
    f_data = f.read(1024)
    sock.send(f_data)
    return

def takeoffFileHeader(filename):
    lines = open(direc + filename, 'r').readlines()
    f = open(direc + filename, 'w') 
    for line in lines[1:]:
        f.write(line)
    f.close()
    return

def recMessage(sock):
    while True:
        message = sock.recv(1024)
        if message.decode()[:3] == '[F]':
            content = message.decode()
            header = content.split('\n')[0]
            data = '\n'.join(content.split('\n')[1:])
            filename = header[3:].split('.')[0]
            ext = header[3:].split('.')[1]
            filename = filename + 'rscv.' + ext

            f = open('/'.join(direc.split('/')[:-2]) + '/download/' + filename, 'w')
            f.write(data)
            f.close()

            chatList.insert(tkinter.END, filename + ' has been received')
            chatList.see(tkinter.END)
            
        else:
            chatList.insert(tkinter.END, message.decode())
            chatList.see(tkinter.END)

def connect(event = None):
    global IP
    global PORT
    connectString = inputString.get()
    addr = connectString.split(":")
    IP = addr[0]
    PORT = int(addr[1])
    try:
        sock.connect((IP,PORT))
        global CONNECTING
        CONNECTING = True
        windowConn.destroy()
    except Exception as e:
        print(e)

def sendMessage(event = None):
    message = inputMessage.get()

    # 파일을 전송하는 경우
    # File: [filename] 형식으로만 전송하고
    # 시스템에서도 이러한 메시지가 들어오면 파일 전송으로 인식한다
    if len(message.split(' ')) > 0 and message.split(' ')[0] == 'File:':
        filename = message.split(' ')[1]

        putFileHeader(filename)
        sendFile(filename)
        takeoffFileHeader(filename)
        
        print('{} has been sended from client\n\n'.format(filename))
        inputMessage.set("")
        return

    elif message == "/bye":
        sock.send(message.encode())
        sock.close()
        window.quit()
        return
    
    else:
        sock.send(message.encode())
        inputMessage.set("")
    return 

def on_closing(event=None):
    inputMessage.set("/bye")
    sendMessage()

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

windowConn = tkinter.Tk()
windowConn.title("chatting")
tkinter.Label(windowConn, text="서버IP 및 포트번호").grid(row=0,column=0)
inputString = tkinter.StringVar(value="127.0.0.1:8080")
inputAddr = tkinter.Entry(windowConn, textvariable=inputString, width=20)
inputAddr.grid(row=1,column=1,padx=5,pady=5)
c_button = tkinter.Button(windowConn, text="접속하기",command=connect)
c_button.grid(row=1,column=2,padx=5,pady=5)

width = 400
height = 100

screenWidth = windowConn.winfo_screenwidth()
screenHeight = windowConn.winfo_screenheight()

x = int((screenWidth/2)-(width/2))
y = int((screenHeight/2) - (height / 2))

windowConn.geometry('{}x{}+{}+{}'.format(width, height, x, y))
windowConn.mainloop()

window = tkinter.Tk()
window.title("클라이언트")

frame = tkinter.Frame(window)
scroll = tkinter.Scrollbar(frame)
scroll.pack(side=tkinter.RIGHT, fill = tkinter.Y)

chatList = tkinter.Listbox(frame, height = 15, width=50, yscrollcommand = scroll.set)
chatList.pack(side=tkinter.LEFT, fill = tkinter.BOTH, padx = 5, pady = 5)
frame.pack()

inputMessage =tkinter.StringVar()
inputBox = tkinter.Entry(window, textvariable = inputMessage)
inputBox.bind("<Return>",sendMessage)
inputBox.pack(side=tkinter.LEFT, fill = tkinter.BOTH, expand = tkinter.YES, padx = 5, pady = 5)
sendButton = tkinter.Button(window, text="전송",command = sendMessage)
sendButton.pack(side=tkinter.RIGHT, fill = tkinter.X,padx=5,pady=5)

window.protocol("WM_DELETE_WINDOW", on_closing)

thread = Thread(target=recMessage, args=(sock, ))
thread.daemon = True
thread.start()

if(CONNECTING):
    window.mainloop()


