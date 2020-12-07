# -*- coding: utf-8 -*- 
import socketserver
import threading
import os

lock = threading.Lock()

direc = os.path.dirname(os.path.realpath(__file__))

class MyHandler(socketserver.BaseRequestHandler):
    users = {}
    def remove_user(self, username):
        if username not in self.users:
            return
        lock.acquire()
        del self.users[username]
        lock.release()
        self.send_all_message("[%s] was out" % username)
        print("now %d people are here" % len(self.users))
        return

    def send_all_message(self, msg):
        for sock, _ in self.users.values():
            sock.send(msg.encode())
        return
    
    def send_all_file(self, f): 
        for sock, _ in self.users.values():
            sock.send(f)
        return

    def handle(self):
        print(self.client_address, "connected")
        nickname = None

        try:
            while True:
                self.request.send("insert nickname: ".encode())
                nickname = self.request.recv(1024).decode()
                if nickname in self.users:
                    self.request.send("already exists!\n".encode())
                else:
                    lock.acquire()
                    self.users[nickname] = (self.request, self.client_address)
                    lock.release()
                    print("now %d people are here" % len(self.users))
                    self.send_all_message("[%s] is in\n" % nickname)
                    break

            self.request.send("  if you want to finish the chatting, please insert '/bye'".encode())

            while True:
                msg = self.request.recv(1024)
                print(msg.decode())
                if msg.decode()[:3] == '[F]':
                    content = msg.decode()
                    header = content.split('\n')[0]
                    filename = header[3:].split('.')[0]
                    ext = header[3:].split('.')[1]
                    filename = filename + 'rscv.' + ext

                    

                    f = open('/'.join(direc.split('/')[:-1]) + '/server/' + filename, 'wb')
                    f.write(b'\n'.join(msg.split(b'\n')[1:]))
                    f.close()

                    self.send_all_file(msg)

                elif msg.decode() == "/bye":
                    self.request.close()
                    self.remove_user(nickname)
                    break

                else:
                    self.send_all_message("[%s]: %s" % (nickname, msg.decode()))


        except Exception as e:
            if(nickname):
                print(e, "*user name :", nickname)
            else:
                print(e, "*user name : Unknown")

            
class ChatServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

PORT = 8080

try:
    server = ChatServer(('', PORT), MyHandler)
    server.serve_forever()
except KeyboardInterrupt:
    print("**waiting for aborting server**")
    server.shutdown()
    server.server_close()
    print("**aborting server success**")