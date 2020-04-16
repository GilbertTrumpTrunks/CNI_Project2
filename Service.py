import socket
import struct
import pickle
import time
import os
import random


file_dir = os.path.dirname(os.path.abspath(__file__))
header_struct = struct.Struct('i1024s')
data_struct = struct.Struct('1024s')

def get_host_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()

    return ip

def net_is_used(port,ip='127.0.0.1'):
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    try:
        s.connect((ip,port))
        s.shutdown(2)
        print('%s:%d is used' % (ip,port))
        return True
    except:
        print('%s:%d is unused' % (ip,port))
        return False

def is_port_used(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((ip, port))
        return True
    except OSError:
        return False
    finally:
        s.close()

def getPort():
    pscmd = "netstat -ntl |grep -v Active| grep -v Proto|awk '{print $4}'|awk -F: '{print $NF}'"
    procs = os.popen(pscmd).read()
    procarr = procs.split("\n")
    tt= random.randint(15000,20000)
    if tt not in procarr:
        return tt
    else:
        getPort()



def send(file_name, client):
    file_path = os.path.join(file_dir, file_name)
    if os.path.isfile(file_path) == 0:
        client.send(header_struct.pack(*(0, b'0')))
    else:
        #文件头
        header = {
            'file_name': file_name,
            'file_size': os.path.getsize(file_path),
            'file_ctime': os.path.getctime(file_path),
            'file_atime': os.path.getatime(file_path),
            'file_mtime': os.path.getmtime(file_path)
        }
        #序列化header
        header_str = pickle.dumps(header)
        #把序列化的header长度和header正文打包发送
        client.send(header_struct.pack(*(len(header_str), header_str)))
        with open(file_path, 'rb') as f:
            for line in f:
                client.send(line)

def run():
    # 测试
    host_ip = get_host_ip()
    a = getPort()
    print(host_ip)
    net_is_used(a,host_ip)
    server_ip = host_ip
    server_port = a
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((server_ip, server_port))
    server.listen(5)
    print('Server start on')
    print('-> ip: %s port: %d' %(server_ip, server_port))
    while True:
        client, client_addr = server.accept()
        print('A new connection from %s' % client_addr[0])
        while True:
            try:
                request = client.recv(1024).decode('utf-8')
                if request == 'end':
                    break
                print('Send %s to %s' % (request, client_addr[0]))
                send(request, client)
            except ConnectionResetError:
                break
        client.close()
    server.close()

if __name__ == '__main__':
    run()
