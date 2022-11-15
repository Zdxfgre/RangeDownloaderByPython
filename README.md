# Range Downloader

python实现基于HTTP "Range"请求的多线程下载器

指定线程数，根据线程数将目标分为若干部分，每个部分对应一个线程下载

先获取目标长度，根据线程数和长度将目标划分为几个部分，并计算每个部分需要下载的范围，将范围记录使用Range请求下载

下载的临时文件保存为“文件名_id.tmp”的形式，全部下载完成后组成最终目标文件

使用
####
    pyinstaller -F http_downloader.py

编译为.exe文件，位置在dist文件夹中

默认下载路径也在.exe所在文件夹中

命令行输入格式
####
    python http_downloader.py {url} {goal_name} {thread_count}
   
如
####
    python http_downloader.py http://down.360safe.com/setup.exe 111.exe 5

网速表保存在项目路径下
####
    speed_pic.jpg

网速测量采用response.iter_content()的形式，若线程数较少会出现测量不准确的情况
