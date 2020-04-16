import socket
import struct
import pickle
import time
import os

server_ip = '192.168.1.2'
server_port = 15619
file_dir = os.path.dirname(os.path.abspath(__file__))
header_struct = struct.Struct('i1024s')
data_struct = struct.Struct('1024s')



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

def file_in_path(path):
    dirs=os.listdir(path)
    My_file=[]
    for file in dirs:
        My_file.append(os.path.join(path,file))
        print(os.path.join(path,file))
    return My_file;
#第二个函数返回的是当前路径下所有文件
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

def send_file_path (My_path,client):
    file_name = My_path
    My_file,My_folder = path_file_walk(file_name)
    for file in My_file:
                if(os.path.isfile(file)):
                            print("114514")
                            client.send(file.encode("utf-8"))
                            start = time.time()
                            print('-'*80)
                            if get(client) == False:
                                print('我觉得你可能打错了文件名 |w ·)')
                            else:
                                end = time.time()
                                print('\n下完啦 (0 V 0)')
                                print('传输时间：', end-start, '超过了全校x%的用户！')
                            print('-'*80)
    for folder in My_folder:
        if(os.path.isdir(folder)):
            print('there is a folder')
            send_file_path(folder,client)
        
def run():
    server_ip = input('Server IP:')
    server_ip = r'192.168.1.6'
    server_port = int(input('Server Port:'))
    server_port = 17493
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((server_ip, server_port))
    while True:
        file_name = input("你想下载的文件叫什么路径呢[输入end断开连接]: ").strip()
        #client.send(file_name.encode('utf-8'))
        send_file_path(file_name,client)

                    
    client.close()

if __name__ == '__main__':
    
    run()
