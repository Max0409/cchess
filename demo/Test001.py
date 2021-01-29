#Test001.py  
import tensorflow as tf
def HelloWorld():
    print(tf.test.is_gpu_available())
    print ("Hello World")  
def add(a, b):  
    return a+b  
def TestDict(dict):  
    print (dict)  
    dict["Age"] = 17  
    return dict  
class Person:  
    def greet(self, greetStr):  
        print (greetStr)  
HelloWorld()
