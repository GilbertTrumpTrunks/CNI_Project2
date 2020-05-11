#!/usr/bin/env Python
# coding=utf-8

import socket
import struct
import pickle
import time
import os
import random
import re
import hashlib
import shutil
import time
import sys
import csv
from PyQt5.QtWidgets import QApplication, QMainWindow

from CN_project2_gui import Ui_MainWindow

file_dir = os.path.dirname(os.path.abspath(__file__))
header_struct = struct.Struct('i1024s')
data_struct = struct.Struct('1024s')

whole_size = 0
current_size = 0


class MyWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.startButton.clicked.connect(self.clickStartButton)

    def clickStartButton(self):
        
        server_ip = self.ipLine.text()
        #server_ip = '129.204.152.91'
        if not re.match(r'[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}', server_ip):
            self.textBrowser.setText('IP地址错误')
            self.startButton.toggle()
            return None
        server_port_string = self.portLine.text()
        server_port = int(server_port_string)
        if server_port < 1024 or server_port > 65535:
            self.textBrowser.setText('端口号错误')
            self.startButton.toggle()
            return None
        file_name = self.srcLine.text()

        ######
        #server_ip = '129.204.152.91'
        
        #file_name = r'C:\Users\Administrator\Desktop\oneplus_x\op'
        #des = r'C:\Users\DonaldJohnTrump\Desktop\新建文件夹 (5)\1919810'
        #des = des  + '/'
        #######
        des = self.desLine.text() + '/'

        # 实现错误输入的处理
        #
        #
        # 实现错误输入的处理

        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((server_ip, server_port))

        md5list = {}
        replist = {}

        self.progressBar.setValue(0)

        start0 = time.time()

        dizhi = file_name
        #print('Shall we start?')
        while(len(dizhi.encode('utf-8'))<200):
            dizhi += ' '
        send_str(dizhi, client)
        #print('dizhi = '+dizhi)
        
        request = client.recv(63).decode('utf-8')
        
        while request[0]== '0':
            request = request[1:]
        #print('request = ' + request)
        #print('request2 = ' + str(string_to_int(request)))
        global whole_size
        whole_size = string_to_int(request)
        #print(whole_size)
        flag = -1
        #print('aftersleep')
        while (flag != 0):
            flag = get(client, self)

        # 计算文件或者文件夹大小

        # if os.path.isdir(file_name):
        #    whole_size = getdirsize(file_name)
        #    rootpath = file_name
        #    send_file_path(file_name,client,md5list,rootpath,replist,self)
        # elif os.path.isfile(file_name):
        #    whole_size = os.path.getsize(file_name)
        #    rootpath = os.path.dirname(file_name)
        #    send_file_path(file_name,client,md5list,rootpath,replist,self)

        # get(client,self)

        replist = csvDictReader1('replist.csv')
        # md5list = csvDictReader1('md5list.csv')
        os.unlink('replist.csv')
        for key in replist:
            fpath, fname = os.path.split(replist[key])
            filepath = str(os.getcwd()) + (fpath[1:])
            print(filepath)
            # 如果路径不存在,创建路径
            if not (os.path.exists(filepath)):
                # print('dir:'+filepath)
                os.makedirs(filepath)
            # 如果是文件移动文件
            if os.path.isfile(os.getcwd() + '\\' + os.path.basename(replist[key][1:])):
                dst = str(os.getcwd()) + str(os.path.dirname(replist[key][1:])) + '\\'
                src = str(os.getcwd()) + '\\' + str(os.path.basename(replist[key][1:]))
                new_file_path = str(os.path.dirname(dst)) + '\\' + str(os.path.basename(src))
                if not os.path.isfile(new_file_path):
                    my_move_file(src, dst)
                    print(src)
                    print(dst)
                # print('\n')

        for f in file_in_path(os.getcwd()):
            # 除了客户端全都移走
            if (os.path.isfile(f)):
                if not ('CN_project2' in os.path.basename(f)):
                    ddes = des + os.path.basename(f)
                    my_move_file(f, ddes)
                    if (os.path.isfile(f)):
                        os.unlink(f)
            elif (os.path.isdir(f)):
                if not ('pycache' in f or 'build' in f or 'dist' in f):
                    fpath, fname = os.path.split(f)
                    filepath = str(des)  # +'/'+fname
                    if not (os.path.exists(filepath)):
                        print('dir:' + filepath)
                        os.makedirs(filepath)
                    shutil.move(f, des)
        end0 = time.time()

        print(str(end0 - start0) + 's')
        self.success_refresh(start0, end0, file_name)
        # client.send("closing")
        data = 'closing'
        b = bytes(data, encoding="utf-8")
        client.sendall(b)
        client.close()
        # shutil.copytree(os.getcwd(),des)
        self.startButton.toggle()

    def success_refresh(self, start, end, file_name):
        # size = get_file_info(client)
        global whole_size
        info = ('下载成功\n' + '文件名：' + file_name
                + '\n下载时间：' + str(end - start) + 's\n' + '下载速度：' + str(
                    whole_size / (end - start) / 1024 / 1024) + 'MB/s\n'
                + '文件大小：' + str(whole_size / 1024 / 1024) + 'MB')
        self.textBrowser.setText(info)

    def fail_refresh(self):
        self.textBrowser.setText('下载失败！')


def get_file_md5(fname):
    m = hashlib.md5()  # 创建md5对象
    with open(fname, 'rb') as fobj:
        while True:
            data = fobj.read(4096)
            if not data:
                break
            m.update(data)  # 更新md5对象

    return m.hexdigest()  # 返回md5对象


def print_file(header):
    file_name = header['file_name']
    file_size = header['file_size']
    print('文件名：%s' % file_name)
    print('文件大小：%s' % file_size)





    
def getdirsize(filePath):
    size = 0
    for root, dirs, files in os.walk(filePath):
        for f in files:
            size += os.path.getsize(os.path.join(root, f))

    return size

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
    

# def compare_md5(fname,sermd5=get_file_md5(fname)):
#    if get_file_md5(fname) == sermd5:
#        return true
#    else:
#        return false

def print_progress(window):
    global current_size
    global whole_size
    window.progressBar.setValue(current_size / whole_size * 100)


def get(client, window):
    # 接受序列化的header数据包
    print('into get')
    #headerlength =recv_number(client)
    packed_header = client.recv(1028)
    # 解包得到序列化的header的长度和header正文
    header_size, header_s = header_struct.unpack(packed_header)
    # 大小为0则说明查无此文件
    if header_size == 0:
        return -1
    # 否则开始传
    else:
        # 反序列化得到header正文
        header = pickle.loads(header_s,encoding="utf-8")
        file_name = header['file_name']
        file_size = header['file_size']
        # size = file_size
        print_file(header)
        global current_size
        current_size += file_size
        server_dirname, server_filename = os.path.split(file_name)
        with open('%s\\%s' % (file_dir, server_filename), 'wb') as f:
            recv_size = 0
            while recv_size < file_size:
                res = client.recv(min(file_size-recv_size,1024))
                # if('it\'s eof' in str(res)):
                # break
                f.write(res)
                recv_size += len(res)
                recv_per = int(recv_size / file_size * 100)
                end = time.time()
                # print_progress(recv_per,window)
            # print_progress(window)
            # window.textBrowser.setText('666666\n')
        # 更新进度条
        print_progress(window)
        if (file_name == 'replist.csv'):
            return 0
        return 1


# 返回路径下的文件
def file_in_path(path):
    dirs = os.listdir(path)
    My_file = []
    for file in dirs:
        My_file.append(os.path.join(path, file))
        print(os.path.join(path, file))
    return My_file


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


# 发送指定目录文件
# def send_file_path(My_path,client,md5list,rootpath,replist,window):
#    file_name = My_path
#    if os.path.isdir(file_name):
#        My_file,My_folder = path_file_walk(file_name)
#        for folder in My_folder:
#            if(os.path.isdir(folder)):
#                replist[str(folder)] = get_relative_path(folder,rootpath)
#                send_file_path(folder,client,md5list,rootpath,replist,window)
#        for file in My_file:
#            if(os.path.isfile(file)):
#                #print("114514")
#                client.send(file.encode("utf-8"))
#                #print('-'*80)
#                if get(client,window) == False:
#                    print('-'*80)
#    elif os.path.isfile(file_name):
#        client.send(file_name.encode("utf-8"))
#        start = time.time()
#        #print('-'*80)
#        if get(client,window) == False:
#            print('我觉得你可能打错了文件名 |w ·)')
#        else:
#            end = time.time()
#            #print('\n下完啦 (0 V 0)')
#            #print('传输时间：', end-start, '超过了全校x%的用户！')
#            md5list[str(file_name)] = get_file_md5(file_name)
#            replist[str(file_name)] = get_relative_path(file_name,rootpath)

#    return None

# 写md5文件


# 读md5文件,有问题
def read_md5csv():
    with open('md5list.csv', 'r') as f:
        md5dict = {}
        reader = csv.DictReader(f)
        for row in reader:
            md5dict[row['name']] = row['information']
    return md5dict


def csvDictReader1(path):
    items = {}
    with open(path) as rf:
        reader = csv.reader(rf, delimiter=',')
        for row in reader:
            items[row[0]] = row[1]
            # items.update(row)
    return items


# 写相对目录文件
def write_repcsv(repdict):
    with open('replist.csv', 'w') as f:
        [f.write('{0},{1}\n'.format(key, value)) for key, value in repdict.items()]
    return None


# 读相对目录文件,有问题,待改正
#def read_repcsv():
    #with open('replist.csv', 'r') as f:
        #repdict = {}
        #reader = csv.DictReader(f)
        #for row in reader:
            #repdict[row[key]] = row[value]
    #return repdict


# 移动文件
def my_move_file(srcfile, dstfile):
    if not os.path.isfile(srcfile):
        print("%s not exist!" % (srcfile))
    else:
        fpath, fname = os.path.split(dstfile)  # 分离文件名和路径
        if not os.path.exists(fpath):
            os.makedirs(fpath)  # 创建路径
        shutil.move(srcfile, dstfile)  # 移动文件
        # print("move %s -> %s"%( srcfile,dstfile))


# 复制文件
def my_copy_file(srcfile, dstfile):
    if not os.path.isfile(srcfile):
        print("%s not exist!" % (srcfile))
    else:
        fpath, fname = os.path.split(dstfile)
        if not os.path.exists(fpath):
            os.makedirs(fpath)
        shutil.copyfile(srcfile, dstfile)
        # print ("copy %s -> %s"%( srcfile,dstfile))


# 得到相对路径
def get_relative_path(abspath, rootpath):
    ret = abspath.replace(rootpath, '.', 1)
    return (ret)

def send_str(data, cilent):
    b = bytes(data, encoding="utf-8")
    cilent.sendall(b)

def send_number(num, cilent):
    numb = str(num)
    if len(numb.encode('utf-8'))<10:
            numb = '0'+numb
    b = bytes(numb, encoding="utf-8")
    cilent.sendall(b)
    
def recv_number(client):
    numb =string_to_int(client.recv(63).decode('utf-8'))
    return numb

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MyWindow()
    mainWindow.show()
    sys.exit(app.exec_())
