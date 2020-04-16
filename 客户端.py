# -*- coding: utf-8 -*-
import socket
import struct
import pickle
import time
import os
import hashlib
import csv
import shutil
server_ip = '192.168.1.2'
server_port = 15619
file_dir = os.path.dirname(os.path.abspath(__file__))
header_struct = struct.Struct('i1024s')
data_struct = struct.Struct('1024s')



def get_file_md5(fname):
    m = hashlib.md5()   #创建md5对象
    with open(fname,'rb') as fobj:
        while True:
            data = fobj.read(4096)
            if not data:
                break
            m.update(data)  #更新md5对象

    return m.hexdigest()    #返回md5对象

def print_file(header):
    file_name = header['file_name']
    file_size = header['file_size']
    file_ctime = header['file_ctime']
    file_atime = header['file_atime']
    file_mtime = header['file_mtime']
    print('文件名：%s' % file_name)
    print('文件大小：%s' % file_size)
    print('文件创建时间：%s' % time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(file_ctime)))
    print('文件最近访问时间：%s' % time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(file_atime)))
    print('文件最近修改时间：%s' % time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(file_mtime)))

def print_progress(percent, width=50):
    if percent >= 100:
        percent = 100
    #字符串拼接的嵌套使用
    show_str=('冲鸭！[%%-%ds]' % width) % (int(width*percent/100)*'>') 
    print('\r%s %d%%' % (show_str, percent), end='')

def get(client):
    #接受序列化的header数据包
    packed_header = client.recv(1024 + 4)
    #解包得到序列化的header的长度和header正文
    header_size, header_s = header_struct.unpack(packed_header)
    #大小为0则说明查无此文件
    if header_size == 0:
        return False
    #否则开始传
    else:
        #反序列化得到header正文
        header = pickle.loads(header_s)
        file_name = header['file_name']
        file_size = header['file_size']
        global size
        size = file_size
        print_file(header)
        #with open('%s\\%s' % (file_dir, file_name), 'wb') as f:
        #with open('%s\\%s' % (file_dir, "test.docx"), 'wb+') as f:
        server_dirname,server_filename = os.path.split(file_name)
        with open('%s\\%s' % (file_dir, server_filename), 'wb') as f:
            recv_size = 0
            while recv_size < file_size:
                res = client.recv(1024)
                f.write(res)
                recv_size += len(res)
                recv_per = int(recv_size/file_size*100)
                end = time.time()
                #print_progress(recv_per,window)
            #window.textBrowser.setText('666666\n')

        return True

#返回路径下的文件
def file_in_path(path):
    dirs=os.listdir(path)
    My_file=[]
    for file in dirs:
        My_file.append(os.path.join(path,file))
        print(os.path.join(path,file))
    return My_file;

#第二个函数返回的是当前路径下多级所有文件
def path_file_walk(path):
    My_file=[]
    My_folder = []
    for root,dirs,files in os.walk(path):
        for name in files:
            My_file.append(os.path.join(root,name))
            print(os.path.join(root,name))
        for name in dirs:
            My_folder.append(os.path.join(root,name))
            print(os.path.join(root,name))
        return My_file,My_folder

#发送指定目录文件
def send_file_path (My_path,client,md5list,rootpath,replist):
    file_name = My_path
    My_file,My_folder = path_file_walk(file_name)
    for folder in My_folder:
        if(os.path.isdir(folder)):
            replist[str(folder)]=get_relative_path(folder,rootpath)
            send_file_path(folder,client,md5list,rootpath,replist)
            
    for file in My_file:
                if(os.path.isfile(file)):
                            #print("114514")
                            client.send(file.encode("utf-8"))
                            start = time.time()
                            #print('-'*80)
                            if get(client) == False:
                                print('我觉得你可能打错了文件名 |w ·)')
                            else:
                                end = time.time()
                                #print('\n下完啦 (0 V 0)')
                                #print('传输时间：', end-start, '超过了全校x%的用户！')
                                md5list[str(file)]=get_file_md5(file)
                                replist[str(file)]=get_relative_path(file,rootpath)
                            #print('-'*80)
#写md5文件                            
def write_md5csv(md5dict):
    with open('md5list.csv', 'w') as f:
        [f.write('{0},{1}\n'.format(key, value)) for key, value in md5dict.items()]
#读md5文件,有问题
def read_md5csv():    
    with open('md5list.csv','r') as f:
        md5dict = {}
        reader = csv.DictReader(f)
        for row in reader:
            md5dict[row['name']]=row['information']
    return md5dict
#写相对目录文件
def write_repcsv(repdict):
    with open('replist.csv', 'w') as f:
        [f.write('{0},{1}\n'.format(key, value)) for key, value in repdict.items()]
        
#读相对目录文件,有问题,待改正
def read_repcsv():    
    with open('replist.csv','r') as f:
        repdict = {}
        reader = csv.DictReader(f)
        for row in reader:
            repdict[row[key]]=row[value]
    return repdict

#移动文件
def my_move_file(srcfile,dstfile):
    if not os.path.isfile(srcfile):
        print("%s not exist!" %(srcfile))
    else:
        fpath,fname=os.path.split(dstfile)    #分离文件名和路径
        if not os.path.exists(fpath):
            os.makedirs(fpath)                #创建路径
        shutil.move(srcfile,dstfile)          #移动文件
        #print("move %s -> %s"%( srcfile,dstfile))
#复制文件
def my_copy_file(srcfile,dstfile):
    if not os.path.isfile(srcfile):
        print("%s not exist!"%(srcfile))
    else:
        fpath,fname=os.path.split(dstfile)    
        if not os.path.exists(fpath):
            os.makedirs(fpath)                
        shutil.copyfile(srcfile,dstfile)      
        #print ("copy %s -> %s"%( srcfile,dstfile))
#得到相对路径      
def get_relative_path(abspath,rootpath):
    ret = abspath.replace(rootpath, '.', 1)
    return(ret)

def run():
    server_ip = input('Server IP:')
    server_port = int(input('Server Port:'))
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((server_ip, server_port))
    md5list = {}
    replist = {}
    des= input("输入目的路径:")
    des = des + '/'
    #des = 'C:/Users/DonaldJohnTrump/Desktop/Project/新建文件夹/test2/'
    start0=time.time()
    while True:
        file_name = input("你想下载的文件叫什么路径呢[输入end断开连接]: ").strip()
        #client.send(file_name.encode('utf-8'))
        if file_name == 'end':
            break
        rootpath = file_name
        send_file_path(file_name,client,md5list,rootpath,replist)
        write_md5csv(md5list)
        write_repcsv(replist)
    
    #遍历绝对路径-相对路径字典
    for key in replist:
        fpath,fname=os.path.split(replist[key])
        filepath = str(os.getcwd())+(fpath[1:])
        print(filepath)
        #如果路径不存在,创建路径
        if not(os.path.exists(filepath)):
            #print('dir:'+filepath)
            os.makedirs(filepath)
        #如果是文件移动文件    
        if os.path.isfile(os.getcwd()+'\\'+os.path.basename(replist[key][1:])):
            #print('is file:'+os.getcwd()+'\\'+os.path.basename(replist[key][1:]))
            #print(os.path.basename(key))
            #print(str(os.getcwd()))
            #print(str(replist[key][1:]))
            
            #print("move %s -> %s"%(os.getcwd()+'\\'+os.path.basename(replist[key][1:]),os.getcwd()+os.path.dirname(replist[key][1:]))+'\\')
            #print('fp:'+os.getcwd()+'    rp:'+os.path.dirname(replist[key][1:])+'\\')
            dst=str(os.getcwd())+str(os.path.dirname(replist[key][1:]))+'\\'
            src = str(os.getcwd())+'\\'+str(os.path.basename(replist[key][1:]))
            new_file_path = str(os.path.dirname(dst))+'\\'+str(os.path.basename(src))
            if not os.path.isfile(new_file_path):
                my_move_file(src,dst)
            #print('\n')
    client.close()
    for f in file_in_path(os.getcwd()):
        if not '客户端' in f:
            #除了客户端全都移走
            shutil.move(f,des)
    #shutil.copytree(os.getcwd(),des)
    end0=time.time()
    print(str(end0-start0)+'s')
    
if __name__ == '__main__':
    
    run()
