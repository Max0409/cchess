client.py 作为客户端（）
server.cpp 作为服务端 （）
test001.py作为神经网络的python实现脚本
client.py server.cpp 之间通过socket通信

server.cpp 将test001.py嵌入，混合编译成可执行文件,编译指令如下
g++ server.cpp -o main  -lpython3.6m 接口规范可以查看代码



