#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
from urllib.parse import urlparse, urlencode

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    def get_host_port(self, url):
        parsed_url = urlparse(url)
        return parsed_url.hostname, parsed_url.port

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if port == None:
            port = 80
        self.socket.connect((host, port))
        return None
    
    def send_request(self, request):
        self.socket.sendall(request.encode())
        response = self.recvall(self.socket)
        self.close()
        return response
    
    def parse_response(self, response):
        parsed_response = response.split('\r\n\r\n')
        headers = parsed_response[0].strip().split('\r\n')
        body = parsed_response[1]
        code = int(headers[0].split(' ')[1])
        return code, headers, body

    def get_code(self, response):
        parsed_response = response.split('\r\n\r\n')
        headers = parsed_response[0].strip().split('\r\n')
        return int(headers[0].split(' ')[1])

    def get_headers(self, response):
        parsed_response = response.split('\r\n\r\n')
        return parsed_response[0].strip().split('\r\n')

    def get_body(self, response):
        parsed_response = response.split('\r\n\r\n')
        return parsed_response[1]
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):  
        host, port = self.get_host_port(url)
        self.connect(host, port)
        request = f"GET {url} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\nAccept: */*\r\n\r\n"
        response = self.send_request(request)
        return HTTPResponse(self.get_code(response), self.get_body(response))

    def POST(self, url, args=None):
        host, port = self.get_host_port(url)
        self.connect(host, port)

        # Process request string
        request = f"POST {url} HTTP/1.1\r\nHost: {host}\r\nAccept: */*\r\n"
        if args:
            request_body = urlencode(args)
            content_length = len(request_body)
            request += f"Content-Length: {content_length}\r\n\r\n{request_body}\r\n"
            request += "Content-Type : application/x-www-form-urlencoded\r\n\r\n"
        else:
            request += f"Content-Length: 0\r\n\r\n"

        # Send out request
        response = self.send_request(request)
        return HTTPResponse(self.get_code(response), self.get_body(response))

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        # python3 httpclient.py GET <url>
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        # python3 httpclient.py <url> (auto GET)
        print(client.command( sys.argv[1] ))
