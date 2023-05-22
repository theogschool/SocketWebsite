#!/usr/bin/python3
#NAME: Theo Gerwing

import socket
import time
import json
import sqlite3
import sys

portNum = 8129

if(len(sys.argv) < 2):
 print("Please input a port number")
 quit()
else:
 portNum = sys.argv[1]
 portNum = int(portNum)

#Hard coded usernames/passwords
hardCodeUsernames = ["Bob", "Alice"]
hardCodePasswords = ["password1", "password2"]
#open socket and start listening
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
hostname = socket.gethostname()
print("listening on interface " + hostname)
serversocket.bind((socket.gethostname(), portNum))

while(1):
 serversocket.listen(5)

 conn, addr = serversocket.accept()
 with conn:
  try:
   print('Connected by', addr)
   data = conn.recv(1024)
   dataDump = data.decode('UTF-8').split('\n')
   dataMethod = 'inv'
   dataCommand = 'inv'
   cookies = 'none'
   jsonString = ''
   isJsonLine = False
   authorizedCookie = 'false'
   usernameCookie = 'null'
   #Gets the method, command, cookies and any json body
   for i in range(len(dataDump)):
    dataLine = dataDump[i].split(' ')
    if(dataLine[0] == 'GET'):
     dataMethod = 'GET'
     dataCommand = dataLine[1]
    elif(dataLine[0] == 'POST'):
     dataMethod = 'POST'
     dataCommand = dataLine[1]
    elif(dataLine[0] == 'Cookie:'):
     cookies = dataDump[i]
    elif(dataLine[0] == '{'):
     isJsonLine = True
    elif(dataLine[0] == '}'):
     isJsonLine = False
     jsonString = jsonString + '}'

    
    if(isJsonLine):
     jsonString = jsonString + dataDump[i] + '\n'

   #If cookies exist, store them in variables
   if(cookies != 'none'):
    cookies = cookies[8:]
    cookies = cookies.split('; ')
    for i in range(len(cookies)):
     tempString = cookies[i].split('=')
     if(tempString[0] == 'authorized'):
      authorizedCookie = tempString[1]
      if(authorizedCookie[len(authorizedCookie) - 1] == '\n'):
       authorizedCookie = authorizedCookie[:-1]
      authorizedCookie = authorizedCookie.rstrip()
     elif(tempString[0] == 'username'):
      usernameCookie = tempString[1]
      if(usernameCookie[len(usernameCookie) - 1] == '\n'):
       usernameCookie = usernameCookie[:-1]
      usernameCookie = usernameCookie.rstrip()
     
   #Send the html file
   if(dataMethod == 'GET' and dataCommand == '/'):
    index = open("index.html", "r")
    returnString = 'HTTP/1.1 200 OK\nContent-Type: text/html\n\n' + index.read()
    returnString = returnString.encode('UTF-8')
    conn.sendall(returnString)
   #If login is requested check for cookies and return them
   elif(dataMethod == 'GET' and dataCommand == '/login'):
    returnString = 'HTTP/1.1 200 OK\nContent-Type: text/html\n\n{"authorized": "false", "username": "null"}'
    if(authorizedCookie == 'true'):
     returnString = '''HTTP/1.1 200 OK\nContent-Type: text/html\n\n{"authorized": "true", "username": "''' + usernameCookie +'''"}'''
    returnString = returnString.encode('UTF-8')
    conn.sendall(returnString)
   #If login is posted, verify they exist in hard coded values and set cookies to them
   elif(dataMethod == 'POST' and dataCommand == '/login'):
    returnString = 'HTTP/1.1 401 BAD-REQUEST\n\n<html><body></body></html>'
    if(jsonString != ''):
     info = json.loads(jsonString)
     for i in range(len(hardCodeUsernames)):
      if((info["username"] == hardCodeUsernames[i]) and (info["password"] == hardCodePasswords[i])):
       returnString = 'HTTP/1.1 200 OK\nContent-Type: text/html\nSet-Cookie: authorized=true\nSet-Cookie: username=' + info["username"] + '\n\n<html><body></body></html>'
    returnString = returnString.encode('UTF-8')
    conn.sendall(returnString)
   #Send back the feed from database.txt
   elif(dataMethod == 'GET' and dataCommand == '/feed'):
    returnString = 'HTTP/1.1 200 OK\nContent-Type: text/html\n\n['
    myDatabase = open("database.txt", "r")
    isFirst = True
    for i in myDatabase:
     if(not isFirst):
      returnString = returnString + ',\n'
     returnString = returnString + '{' + i + '}'
     isFirst = False
    returnString = returnString + ']'
    returnString = returnString.encode('UTF-8')
    conn.sendall(returnString)
   #Add a tweet to the database by getting the cookies of the sender and storing that in database.txt
   elif(dataMethod == 'POST' and dataCommand == '/feed'):
    returnString = 'HTTP/1.1 401 BAD-REQUEST\n\n<html><body></body></html>'
    if(jsonString != ''):
     tweet = json.loads(jsonString)
     writeString = '"user": "' + usernameCookie + '", "tweet": "' + tweet["tweet"] + '"\n'
     myDatabase = open("database.txt", "a")
     myDatabase.write(writeString)
     myDatabase.close()
     returnString = 'HTTP/1.1 200 OK\n\n<html><body></body></html>'
    returnString = returnString.encode('UTF-8')
    conn.sendall(returnString)
   #Set cookies to default values when logout is requested
   elif(dataMethod == 'POST' and dataCommand == '/logout'):
    returnString = 'HTTP/1.1 200 OK\nSet-Cookie: authorized=false\nSet-Cookie: username=null\n\n'
    returnString = returnString.encode('UTF-8')
    conn.sendall(returnString)
   else:
    conn.sendall(b'''HTTP/1.1 404 PAGE-NOT-FOUND\n\n<html><body></body></html>''')
  except Exception as e:
   print(e) 
