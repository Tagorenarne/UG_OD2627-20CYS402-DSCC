clocks=[[0, 0, 0], [0, 0, 0], [0, 0, 0]]
e=0
event=[]

def local(pn):
    global e
    p=pn-1
    clocks[p][p]+=1
    e+=1
    timestamp=list(clocks[p])
    event.append([f"P{pn}",f"E{e}", "LOCAL   ",str(timestamp)])

def send(px, py):
    global e
    p=px-1
    clocks[p][p]+=1
    e+=1
    timestamp=list(clocks[p])
    event.append([f"P{px}",f"E{e}", "SEND    ",str(timestamp)])
    return timestamp

def receive(py, px, msg_vector):
    global e
    p=py-1
    for i in range(len(clocks[p])):
        clocks[p][i]=max(clocks[p][i], msg_vector[i])
    clocks[p][p] += 1
    e += 1
    timestamp = list(clocks[p])
    event.append([f"P{py}", f"E{e}", "RECEIVE ", str(timestamp)])

local(1)
m1 = send(1, 2)
receive(2, 1, m1)
local(2)
m2 = send(2, 3)
local(1)
m3 = send(1, 3)
receive(3, 2, m2)
receive(3, 1, m3)

print("========================================================")
print("                       VECTOR CLOCK LOG")
print("========================================================")

print("Process\tEvent\tType\tTimestamp")
print("--------------------------------------------------------")
for e in event:
    print(e)
print("--------------------------------------------------------\n")