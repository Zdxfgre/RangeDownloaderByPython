import argparse
import threading
import os
import datetime
import requests
import time
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser()
parser.add_argument('url',type=str)
parser.add_argument('goal_name',type=str,default="internet.jpg")
parser.add_argument('Count',type=int,default=5)
args=parser.parse_args()

url=args.url
Count=args.Count
goal_name=args.goal_name

global read
read=0
global starttime
starttime=0
speed_list=[]
time_list=[]


class CalThread(threading.Thread):
    def __init__(self,name,filelength):
        super().__init__()
        self.name=name
        self.filelength=filelength
        
    def run(self):
        st_time=time.time()
        global read
        while(True):
            time.sleep(0.1)
            now_count=0.0
            now_time=time.time()
            for i in range(0,Count):
                tmp_name="{}_{}.tmp".format(self.name,i)
                if(os.path.exists(tmp_name)==True):
                    now_count+=os.path.getsize(tmp_name)
          #  print(read/1024/1024/(now_time-st_time))
           # print(read)
            if(read!=0):
                time_list.append(now_time)
                speed_list.append(read/1024/1024/(now_time-st_time))
            if(read==self.filelength):
                break

class PerThread(threading.Thread):
    #创建一个下载线程
    #一个线程下载一个部分，需要对应的范围，此处直接传入编号即可
    def __init__(self,DownloadRanges,url,id,name):
        super().__init__()
        self.DownloadRanges = DownloadRanges
        self.url = url
        self.id=id
        self.name=name
    def run(self):
        global read
        endpos=self.DownloadRanges[self.id][1]["endpos"]
        startpos=self.DownloadRanges[self.id][2]["stpos"]
        global starttime
        tmp_name="{}_{}.tmp".format(self.name,self.id)
        #找到之前下载的位置
        if(os.path.exists(tmp_name)==True):
            stpos=os.path.getsize(tmp_name)+startpos
        else:
            stpos=startpos
        if(stpos<endpos):
            range_now="{}-{}".format(stpos,endpos)
           # print(range_now)
            headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36 Edg/92.0.902.84",
                    "Range": "bytes={}".format(range_now)
            }
            response=requests.get(self.url,headers=headers)
            chunk_size=1024
            last_time=time.time()
            
            with open("{}_{}.tmp".format(self.name,self.id),"wb") as f:
                for chunk in response.iter_content(chunk_size=1024):
                    read+=len(chunk)
                    f.write(chunk)
               # print(chunk_size)
               # print(datetime.datetime.now())   
                """
                    read+=len(chunk)
                    now_time=time.time()
                   # if(now_time-last_time>0.01):
                    speed=chunk_size*1.0/1024/1024/(now_time-last_time)
                    last_time=now_time
                    speed_list.append(speed)
                    time_list.append(now_time)
                    #print("{:.4f}".format(speed))
                """
                    #f.write(chunk)
                
            #获取对应的编号的部分，以.tmp形式保存
            """
                with open("{}_{}.tmp".format(self.name,self.id),"wb") as f:
                    f.write(response.content)
            """
            f.close()

def GetFileLength(url):
    #获取对象的Length，以便之后的多部份downloader
    response=requests.head(url)
    #通过获取url对应的头信息中的'Content-Length'获取对象的Length
    filelength=int(response.headers['Content-Length'])    
    return filelength


def GetDownloadList(filelength,DownloadCount):
    #根据目标length计算每个range请求下载的范围
    #以一个list的形式返回,队列总包含范围对应前后位置和编号
    DownloadRanges=[]
    onesize=int(filelength/DownloadCount)
    startpos=0
    for i in range(DownloadCount):
        endpos=onesize*(i+1)
        #当前的结束位置
        if(i==DownloadCount-1):
            #对于最后一段,防止因为除法造成的误差
            endpos=filelength
        nowrange="{}-{}".format(startpos,endpos)
        #记录末尾位置，用于断点续传
        DownloadRanges.append([{"range":nowrange},{"endpos":endpos},{"stpos":startpos},i])
        startpos=endpos+1
        #防止重合
    return DownloadRanges


#创建count个下载线程并行下载
def MultiThreadDownload(DownloadRanges,DownloadCount,filelength):
    threads=[]
    global read
    #用一个list保存线程
    global starttime
    starttime=time.time()#一开始的时间
    cal=CalThread(getfilename(url),filelength)
    cal.start()
    threads.append(cal)
    for i in range(DownloadCount):
        now_thread=PerThread(DownloadRanges,url,i,getfilename(url))
        now_thread.start()
        #启动该线程
        threads.append(now_thread)
        
    for thread in threads:
        thread.join()
     


def getfilename(url):
    #获取目标的名字
    name=[]
    leng=len(url)
    flag=0
    for i in range(leng-1,0,-1):
        if(url[i]=='.'):
            flag=1
        if(flag==0):
            continue
        if(url[i]=='/'):
            break
        if(url[i]!='.'):
            name+=url[i]
    name.reverse()
    real_name=''
    for i in range(0,len(name)):
        real_name+=name[i]
    return real_name

    
#组合文件，根据编号顺序组合即可
def combinefile(url):
    filename=goal_name
    originname=getfilename(url)
    with open(filename,"ab") as f:
        for i in range(Count):
           # print(os.path.getsize("{}_{}.tmp".format(originname,i)))
            with open("{}_{}.tmp".format(originname,i),"rb") as partfile:
                f.write(partfile.read())


def pic():
    #作速度图
    st=time_list[0]
 #  print(time_list)
    for i in range(len(time_list)):
        time_list[i]-=st
    plt.plot(time_list,speed_list)
    plt.title('Speed_pic',fontsize=14)
    plt.xlabel(u'Time(s)',fontsize=14)
    plt.ylabel(u'Speed(m/s)',fontsize=14)
    plt.savefig("speed_pic.jpg")
    plt.show()

def download(url,Count,goal_name):
    # length=GetFileLength(url)
   filelength=GetFileLength(url)
   ranges=GetDownloadList(filelength,Count)
   #获取范围列表
   MultiThreadDownload(ranges,Count,filelength)
   #多线程下载
   combinefile(url)
   #组合文件
   pic()
if __name__ == '__main__':
   download(url,Count,goal_name)