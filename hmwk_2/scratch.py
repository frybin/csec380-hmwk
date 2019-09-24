import simplerequest

r = simplerequest.SimpleRequest('csec380-core.csec.rit.edu', port=82, type="GET", resource="/getFlag5")
r.render()
r.send()

print(r.data)