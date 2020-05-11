import socket
import struct
import pickle
import time
import os
import random
import hashlib
import time
import _compat_pickle

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


def net_is_used(port, ip='127.0.0.1'):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((ip, port))
        s.shutdown(2)
        print('%s:%d is used' % (ip, port))
        return True
    except:
        print('%s:%d is unused' % (ip, port))
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


def get_file_md5(fname):
    m = hashlib.md5()  # 创建md5对象
    with open(fname, 'rb') as fobj:
        while True:
            data = fobj.read(4096)
            if not data:
                break
            m.update(data)  # 更新md5对象
    return m.hexdigest()  # 返回md5对象


# 返回路径下的文件
def file_in_path(path):
    dirs = os.listdir(path)
    My_file = []
    for file in dirs:
        My_file.append(os.path.join(path, file))
        print(os.path.join(path, file))
    return My_file


def write_md5csv(md5dict):
    with open('md5list.csv', 'w') as f:
        [f.write('{0},{1}\n'.format(key, value)) for key, value in md5dict.items()]
    return None


def write_repcsv(repdict):
    with open('replist.csv', 'w') as f:
        [f.write('{0},{1}\n'.format(key, value)) for key, value in repdict.items()]
    return None





# 第二个函数返回的是当前路径下多级所有文件
def path_file_walk(path):
    My_file = []
    My_folder = []
    for root, dirs, files in os.walk(path):
        for name in files:
            My_file.append(os.path.join(root, name))
            print(os.path.join(root, name))
        for name in dirs:
            My_folder.append(os.path.join(root, name))
            print(os.path.join(root, name))
        return My_file, My_folder


def getPort():
    pscmd = "netstat -ntl |grep -v Active| grep -v Proto|awk '{print $4}'|awk -F: '{print $NF}'"
    procs = os.popen(pscmd).read()
    procarr = procs.split("\n")
    tt = random.randint(15000, 20000)
    if tt not in procarr:
        return tt
    else:
        getPort()


# 得到相对路径
def get_relative_path(abspath, rootpath):
    ret = abspath.replace(rootpath, '.', 1)
    return (ret)


def send(file_name, client):
    file_path = os.path.join(file_dir, file_name)
    print(file_path)
    if os.path.isfile(file_path) == 0:
        client.send_number(len(header_struct.pack(*(0, b'0'))).encode('utf-8'))
        client.send(header_struct.pack(*(0, b'0')))
            
    else:
        # 文件头

        header = {
            'file_name': file_name,
            'file_size': os.path.getsize(file_path),
        }
        # 序列化header
        header_str=pickle.dumps(header,4)
        # 把序列化的header长度和header正文打包发送
        #client.send_number(1028)
        client.send(header_struct.pack(*(len(header_str), header_str)))
        # with open(file_path, 'rb') as f:
        f = open(file_path, 'rb')
        for line in f:
            client.send(line)
        f.close()

        # client.send('it\'s eof'.encode('utf-8'))
        time.sleep(0.25)


def send_file_path(My_path, client, md5list, rootpath, replist):
    file_name = My_path
    if os.path.isdir(file_name):
        My_file, My_folder = path_file_walk(file_name)
        for folder in My_folder:
            if (os.path.isdir(folder)):
                replist[str(folder)] = get_relative_path(folder, rootpath)
                send_file_path(folder, client, md5list, rootpath, replist)
                # replist[str(file)] = get_relative_path(file,rootpath)
        for file in My_file:
            if (os.path.isfile(file)):
                send(file, client)
                # client.send(file_name.encode("utf-8"))
                md5list[str(file)] = get_file_md5(file)
                replist[str(file)] = get_relative_path(file, rootpath)
    elif os.path.isfile(file_name):
        # client.send(file_name.encode("utf-8"))
        send(file_name, client)
        md5list[str(file_name)] = get_file_md5(file_name)
        replist[str(file_name)] = get_relative_path(file_name, rootpath)

    return None


def send_str(data, cilent):
    b = bytes(data, encoding="utf-8")
    cilent.sendall(b)

def send_number(num, cilent):
    numb = str(num)
    while len(numb.encode('utf-8'))<63:
            numb = '0'+numb
    b = bytes(numb, encoding="utf-8")
    cilent.sendall(b)

def getdirsize(filePath):
    size = 0
    if (os.path.isdir(filePath)):
        for root, dirs, files in os.walk(filePath):
            for f in files:
                size += os.path.getsize(os.path.join(root, f))
    elif (os.path.isfile(filePath)):
        size = os.path.getsize(filePath)

    return str(size)


def run():
    # 测试
    host_ip = get_host_ip()
    a = getPort()
    host_ip='0.0.0.0'
    print(host_ip)
    net_is_used(a, host_ip)
    server_ip = host_ip
    server_port = a
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((server_ip, server_port))
    server.listen(5)
    md5list = {}
    replist = {}
    print('Server start on')
    print('-> ip: %s port: %d' % (server_ip, server_port))
    while True:
        client, client_addr = server.accept()
        print('A new connection from %s' % client_addr[0])
        while True:
            try:
                request = client.recv(200).decode('utf-8')
                print(request)
                while(request[-1]==' '):
                    request = request[0:-1]
                if request == r'closing':
                    break
                if request == 'end':
                    break
                print('Send %s to %s' % (request, client_addr[0]))
                if (os.path.exists('replist.csv')):
                    os.unlink('replist.csv')
                
                glosize = getdirsize(request)
                glosize = str(glosize)
                while(len(glosize.encode('utf-8'))<63):
                    glosize = '0'+glosize
                send_str(glosize, client)
                time.sleep(2)
                if os.path.isdir(request):
                    file_name = request
                    whole_size = getdirsize(file_name)
                    rootpath = file_name
                    send_file_path(file_name, client, md5list, rootpath, replist)
                    write_repcsv(replist)
                    send('replist.csv', client)
                elif os.path.isfile(request):
                    file_name = request
                    whole_size = os.path.getsize(file_name)
                    rootpath = os.path.dirname(file_name)
                    send_file_path(file_name, client, md5list, rootpath, replist)
                    write_repcsv(replist)
                    send('replist.csv', client)

                    # client, client_addr = server.accept()#新加的，看能不能解决10053
            except ConnectionResetError:
                break
            # client, client_addr = server.accept()#新加的，看能不能解决10053
        client.close()
    server.close()
    if (os.path.exists('replist.csv')):
        os.unlink('replist.csv')

def string_to_int(strr):
    if strr == '0':
        return 0
    else:
        temp = 0
        for i in range (len(strr)):
            temp+=int(strr[i])
            if i < len(strr)-1:
                temp*=10
        return temp

if __name__ == '__main__':
    run()

# 此部分代码为服务端，已经可以实现单个文件配合ui界面的传输 20200416#
# import socket
# import struct
# import pickle
# import time
# import os
# import random

##server_ip = '192.168.1.104'
##server_port = 15184
# file_dir = os.path.dirname(os.path.abspath(__file__))
# header_struct = struct.Struct('i1024s')
# data_struct = struct.Struct('1024s')

# def get_host_ip():

#    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

#    try:
#        #获取本机IP地址
#        s.connect(('8.8.8.8', 80))
#        ip = s.getsockname()[0]
#    finally:
#        s.close()

#    return ip

##def net_is_used(port,ip='127.0.0.1'):
##    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
##    try:
##        s.connect((ip,port))
##        s.shutdown(2)
##        print('%s:%d is used' % (ip,port))
##        return True
##    except:
##        print('%s:%d is unused' % (ip,port))
##        return False

# def is_port_used(ip, port):
#    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#    try:
#        s.connect((ip, port))
#        return True
#    except OSError:
#        return False
#    finally:
#        s.close()


# def getPort():
#    pscmd = "netstat -ntl |grep -v Active| grep -v Proto|awk '{print $4}'|awk -F: '{print $NF}'"
#    procs = os.popen(pscmd).read()
#    procarr = procs.split("\n")
#    tt= random.randint(15000,20000)
#    if tt not in procarr:
#        return tt
#    else:
#        getPort()


# def send(file_name, client):
#    file_path = os.path.join(file_dir, file_name)
#    if os.path.isfile(file_path) == 0:
#        client.send(header_struct.pack(*(0, b'0')))
#    else:
#        #文件头
#        header = {
#            'file_name': file_name,
#            'file_size': os.path.getsize(file_path),
#            'file_ctime': os.path.getctime(file_path),
#            'file_atime': os.path.getatime(file_path),
#            'file_mtime': os.path.getmtime(file_path)
#        }
#        #序列化header
#        header_str = pickle.dumps(header)
#        #把序列化的header长度和header正文打包发送
#        client.send(header_struct.pack(*(len(header_str), header_str)))
#        with open(file_path, 'rb') as f:
#            for line in f:
#                client.send(line)

# def run():
#    # 测试
#    host_ip = get_host_ip()
#    a = getPort()
#    print(host_ip)
#   # net_is_used(a,host_ip)
#    server_ip = host_ip
#    server_port = a
#    #创建socket对象，但是还没有连接
#    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#    #绑定
#    server.bind((server_ip, server_port))
#    server.listen(5)
#    print('Server start on')
#    print('-> ip: %s port: %d' %(server_ip, server_port))
#    while True:
#        #接受一个新连接
#        client, client_addr = server.accept()
#        print('A new connection from %s' % client_addr[0])
#        while True:
#            try:
#                request = client.recv(1024).decode('utf-8')
#                if request == 'end':
#                    break
#                print('Send %s to %s' % (request, client_addr[0]))
#                send(request, client)
#                client, client_addr = server.accept()#新加的，看能不能解决10053
#            except ConnectionResetError:
#                break
#        client.close()

#    server.close()

# if __name__ == '__main__':
#    run()
# 此部分代码为服务端，已经可以实现单个文件配合ui界面的传输 20200416#
