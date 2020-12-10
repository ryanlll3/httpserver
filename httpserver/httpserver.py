"""
main application:

get http request
parse http request
forward http request to webframe app
get http response from webframe app
response to client

transmission protocol
httpserver --> webframe {method:'GET', Info:'/'}
webframe --> httpserver {status:'200', data:'ccccc'}

"""

from socket import *
import sys
from threading import Thread
from config import *
import re,json

# server address
ADDR = (HOST,PORT)

# webframe address
WEBAPP = (frame_ip,frame_port)

def connect_frame(env):
    s = socket()
    try:
        s.connect(WEBAPP)
    except Exception as e:
        print(e)
        return
    print(env)
    data = json.dumps(env)
    s.send(data.encode())
    data = s.recv(4096 * 100).decode()
    return json.loads(data)


# HTTPSERVER class

class HTTPServer:
    def __init__(self):
        self.address = ADDR
        self.create_socket()  # connect to browser - user
        self.bind()

    def create_socket(self):
        self.sockfd = socket()
        self.sockfd.setsockopt(SOL_SOCKET,SO_REUSEPORT,DEBUG)

    def bind(self):
        self.sockfd.bind(self.address)
        self.ip = self.address[0]
        self.port = self.address[1]

    # start http server

    def serve_forever(self):
        self.sockfd.listen(5)
        print('Listen the port %d' % self.port)
        while True:
            connfd,addr = self.sockfd.accept()
            print('Connected from',addr)
            client = Thread(target=self.handle,args=(connfd,))
            client.setDaemon(True)  # 当主线程退出时,后台线程随机退出
            client.start()

    # handle client request
    def handle(self,connfd):
        request = connfd.recv(4096).decode()
        pattern = r'(?P<method>[A-Z]+)\s+(?P<info>/\S*)'  # 格式是 (?p<name>...)，其中 name 是组的名称，...是要匹配的表达式。\
        # 它们的行为与正常组完全相同，除了可以通过索引访问还可以通过 group(name) 方式访问它们。非捕获组的格式是 (?:...)。
        try:
            env = re.match(pattern,request).groupdict()
        except:
            connfd.close()
            return
        else:
            data = connect_frame(env)
            if data:
                self.response(connfd, data)

    # send data to browser
    def response(self,connfd,data):
        # data => {'status':'200','data':'****'}
        if data['status'] == '200':
            responseHeaders="HTTP/1.1 200 OK\r\n"  # response header
            responseHeaders += "Content-Type:text/html\r\n"  # response row
            responseHeaders += "\r\n"
            responseBody = data['data']  # response body

        elif data['status'] == '404':
            responseHeaders = "HTTP/1.1 404 Not Found\r\n"  # response header
            responseHeaders += "Content-Type:text/html\r\n"  # response row
            responseHeaders += "\r\n"
            responseBody = data['data']  # response body

        elif data['status'] == '500':
            responseHeaders = "HTTP/1.1 500 Internal Server Error\r\n"  # response header
            responseHeaders += "Content-Type:text/html\r\n"  # response row
            responseHeaders += "\r\n"
            responseBody = data['data']  # response body

        response_data = responseHeaders + responseBody
        connfd.send(response_data.encode())


httpd = HTTPServer()
httpd.serve_forever()


