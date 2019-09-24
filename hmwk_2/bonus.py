import simplerequest
import math
import time



e = time.time()

r = simplerequest.SimpleRequest(
    "csec380-core.csec.rit.edu", port=82, type="POST", resource="/getSecure"
)

r.render()
r.send()

key = simplerequest.parse_value(r.data, "Token is:")

r = simplerequest.SimpleRequest(
    "csec380-core.csec.rit.edu", port=82, type="GET", resource="/getFlag5"
)

r.render()
r.send()

xidx = r.data.find("var x =")
yidx = r.data.find("var y =")

x = int(r.data[xidx + 8 : xidx + 12].strip(";").strip('"'))
y = int(r.data[yidx + 8 : yidx + 10].strip(";"))

i = complex(x, 3)
n = complex(5, y)
print(i)
print(n)

out2 = i * n
out1 = e * (math.pi * i)

x = out1 + out2
a = time.time()

print(x)

r = simplerequest.SimpleRequest(
    "csec380-core.csec.rit.edu",
    port=82,
    type="POST",
    resource="/flag5redir",
    body=f"a={x.imag}&b={x.real}&c={a-e}&d={key}",
)

r.render()
r.send()

print(r.request)
print(r.data)
