#include <iostream>
#include <python2.7/Python.h>
#include <string> 
#include <stdio.h> 
#include <unistd.h>
#include <iostream>
#include <sys/socket.h>
#include <arpa/inet.h>

#define MAXSIZE 1024

using namespace std;

void HelloWorld();
int Add(int a,int b);
void TestTransferDict();
void TestClass();


class tcp_server
{
private:
        int socket_fd,accept_fd;
        sockaddr_in myserver;
        sockaddr_in remote_addr;
 
public:
        tcp_server(int listen_port);
        int recv_msg();


};

tcp_server::tcp_server(int listen_port) {
 
        if(( socket_fd = socket(PF_INET,SOCK_STREAM,IPPROTO_TCP)) < 0 ){
                throw "socket() failed";
        }
 
        memset(&myserver,0,sizeof(myserver));
        myserver.sin_family = AF_INET;
        myserver.sin_addr.s_addr = htonl(INADDR_ANY);
        myserver.sin_port = htons(listen_port);
 
        if( bind(socket_fd,(sockaddr*) &myserver,sizeof(myserver)) < 0 ) {
                throw "bind() failed";
        }
 
        if( listen(socket_fd,10) < 0 ) {
                throw "listen() failed";
        }
}
 
int tcp_server::recv_msg() {
 
        while( 1 ) {
 
                socklen_t sin_size = sizeof(struct sockaddr_in);
                if(( accept_fd = accept(socket_fd,(struct sockaddr*) &remote_addr,&sin_size)) == -1 )
                {
                        throw "Accept error!";
                        continue;
                }
                printf("Received a connection from %s\n",(char*) inet_ntoa(remote_addr.sin_addr));
                char buffer[MAXSIZE];
                if( !fork() ) {
                        //char buffer[MAXSIZE];
                        memset(buffer,0,MAXSIZE);
                        if( ( read(accept_fd,buffer,MAXSIZE)) < 0 ) {
                                throw("Read() error!");
                        } else {
                                printf("Received message: %s\n",buffer);
                                break;
                        }
                        exit(0);
                }
             
                int c=Add(1,2);
                cout<<c<<endl;
                char sendBuf[MAXSIZE];
                sendBuf[0]=c+'0';
                sendBuf[1]='\0';
                send(accept_fd, sendBuf, strlen(sendBuf), 0);
                close(accept_fd);
        }
        return 0;
}


int main(int argc,char* argv[])
{

        
cout << "Starting Test..." << endl;

cout << "HelloWorld()-------------" << endl;
HelloWorld();
/*
cout << "Add()--------------------" << endl;
Add(1,2);

cout << "TestDict-----------------" << endl;
TestTransferDict();
cout << "TestClass----------------" << endl;
TestClass();
*/
//tcp_server ts(atoi(argv[1]));
//ts.recv_msg();
      

return 0;
}


void HelloWorld()
{
Py_Initialize();
PyRun_SimpleString("import sys");  

PyRun_SimpleString("sys.path.append('./')");  

PyObject * pModule = NULL;
PyObject * pFunc = NULL;
pModule =PyImport_ImportModule("Test001");
pFunc= PyObject_GetAttrString(pModule, "HelloWorld"); 
PyEval_CallObject(pFunc, NULL);
Py_Finalize();
}


int  Add(int a,int b)
{
Py_Initialize();
PyRun_SimpleString("import sys");  
PyRun_SimpleString("sys.path.append('./')");
PyObject * pModule = NULL;
PyObject * pFunc = NULL;
pModule =PyImport_ImportModule("Test001");
pFunc= PyObject_GetAttrString(pModule,"add");
PyObject *pArgs = PyTuple_New(2); 
PyTuple_SetItem(pArgs, 0, Py_BuildValue("i", a));
PyTuple_SetItem(pArgs, 1, Py_BuildValue("i", b));
PyObject *pReturn = NULL;
pReturn = PyEval_CallObject(pFunc, pArgs);
int result;
PyArg_Parse(pReturn, "i", &result);
cout << "a+b = " << result << endl;
Py_Finalize();
return result;
}


void TestTransferDict()
{
Py_Initialize();
PyRun_SimpleString("import sys");  

PyRun_SimpleString("sys.path.append('./')");
PyObject * pModule = NULL;
PyObject * pFunc = NULL;
pModule =PyImport_ImportModule("Test001");
pFunc= PyObject_GetAttrString(pModule, "TestDict"); 
PyObject *pArgs = PyTuple_New(1); 
PyObject *pDict = PyDict_New(); 
PyDict_SetItemString(pDict, "Name", Py_BuildValue("s", "WangYao")); 
PyDict_SetItemString(pDict, "Age", Py_BuildValue("i", 25)); 
PyTuple_SetItem(pArgs, 0, pDict);

PyObject *pReturn = NULL;
pReturn = PyEval_CallObject(pFunc, pArgs);

int size = PyDict_Size(pReturn);
cout << "size of dic: " << size << endl;
PyObject *pNewAge = PyDict_GetItemString(pReturn, "Age");
int newAge;
PyArg_Parse(pNewAge, "i", &newAge);
cout << "True Age: " << newAge << endl;

Py_Finalize();
}


void TestClass()
{
Py_Initialize();
PyRun_SimpleString("import sys");  

PyRun_SimpleString("sys.path.append('./')");
PyObject * pModule = NULL;
PyObject * pFunc = NULL;
pModule =PyImport_ImportModule("Test001");
pFunc= PyObject_GetAttrString(pModule, "TestDict"); 
PyObject *pClassPerson = PyObject_GetAttrString(pModule, "Person");
//PyObject *pInstancePerson = PyInstance_New(pClassPerson, NULL, NULL);
//PyObject_CallMethod(pInstancePerson, "greet", "s", "Hello Kitty"); 
Py_Finalize();
}


