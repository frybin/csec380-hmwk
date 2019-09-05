import simplerequest
import socket

r = simplerequest.SimpleRequest('csec380-core.csec.rit.edu:82', 'POST', resource='/getSecure')

req = r.render()
print(req)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('csec380-core.csec.rit.edu', 82))

s.sendall(req.encode('utf-8'))

data = s.recv(4096).decode('ASCII')

print(data)

token = request.parse_value(data, 'Token is:').strip('"')
#print(value)

r = request.Request('csec380-core.csec.rit.edu:82', 'POST', resource='/createAccount', body=f'username=oneNutW0nder&token={token}')
req = r.render()
print(req)
s.sendall(req.encode('utf-8'))

data = s.recv(4096).decode('ASCII')
print(data)

password = request.parse_value(data, "your password is")
print(password)


r = request.Request('csec380-core.csec.rit.edu:82', 'POST', resource='/login', body=f'username=oneNutW0nder&password={request.url_encode(password)}&token={token}')
req = r.render()
print(req)
s.sendall(req.encode('utf-8'))

data = s.recv(4096).decode('ASCII')
print(data)




"""
#PART 3

r = request.Request('csec380-core.csec.rit.edu:82', 'POST', resource='/getFlag3Challenge', body=f'token={token}')
req = r.render()
#print(req)

s.sendall(req.encode('utf-8'))

data = s.recv(4096).decode('ASCII')
print(data)
value = request.parse_value(data, 'solve the following:').strip('"')
#print(value)


operators = ['+', '-', '//', '*']
op = list(filter(lambda operator: (operator in value), operators))
op = op[0]
value = value.split(op)
if op == '//':
    value = int(value[0]) // int(value[1]) 
elif op == '+':
    value = int(value[0]) + int(value[1])
elif op == '-':
    value = int(value[0]) - int(value[1])
elif op == '*':
    value = int(value[0]) * int(value[1])
else:
    print("Operator unknown....")

#print(value)

r = request.Request('csec380-core.csec.rit.edu:82', 'POST', resource='/getFlag3Challenge', body=f'solution={value}&token={token}')
req = r.render()
print(req)

s.sendall(req.encode('utf-8'))

data = s.recv(4096).decode('ASCII')
print(data)
"""