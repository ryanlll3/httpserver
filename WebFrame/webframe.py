from socket import *
import json
from settings import *
from select import select  # IO 多路复用
from urls import *

# application class


class Application:
    def __init__(self):
        self.rlist = []  # IO 多路复用
        self.wlist = []  # IO 多路复用
        self.xlist = []  # IO 多路复用
        self.sockfd = socket()
        self.sockfd.setsockopt(SOL_SOCKET,SO_REUSEPORT,DEBUG)
        self.sockfd.bind(frame_addr)


    def start(self):
        self.sockfd.listen(5)
        print('Start App Listener %s' % frame_port)
        self.rlist.append(self.sockfd)  # IO 多路复用
        # select monitoring request
        while True:  # IO 多路复用
            rs,ws,xs = select(self.rlist,self.wlist,self.xlist)  # IO 多路复用
            for r in rs:  # IO 多路复用
                if r is self.sockfd:  # IO 多路复用
                    connfd, addr = r.accept()
                    self.rlist.append(connfd)
                else:
                    self.handle(r)
                    self.rlist.remove(r)

    # handle http request
    def handle(self,connfd):
        request = connfd.recv(1024).decode()
        request = json.loads(request)
        # request => {'method':'GET','INFO':'/'}
        if request['method'] == 'GET':
            if request['info'] == '/' or \
                request['info'][-5:] == '.html':  # last 5 char
                response = self.get_html(request['info'])
            else:
                response = self.get_data(request['info'])

        elif request['method'] == 'POST':
            pass

        response = json.dumps(response)
        # response => {'status':'200','data':'XXXX'}
        connfd.send(response.encode())
        connfd.close()

    #handle webpage html
    def get_html(self, info):
        if info == '/':
            filename = STATIC_DIR+"/index.html"
        else:
            filename = STATIC_DIR+info
        try:
            fd = open(filename)
            return {'status': '200', 'data': fd.read()}
        except Exception as e:
            fd = open(STATIC_DIR+'/404.html')
            return {'status': '404', 'data': fd.read()}

    def get_data(self,info):
        for url, func in urls:
            if url == info:
                return {'status':'200','data': func()}
        return {'status':'404','data':'Sorry...not found'}

app = Application()
app.start()

