clock=[0,0,0]
timestamp=0
e=0
event=[]
def local(pn):
    global e
    pn-=1
    clock[pn]+=1
    e+=1
    timestamp=clock[pn]
    event.append([f"P{pn+1}", f"E{e}", "LOCAL   ", str(timestamp)])

def send(px,py):
    global e
    px-=1
    clock[px]+=1
    e+=1
    timestamp=clock[px]
    event.append([f"P{px+1}", f"E{e}", "SEND    ", f"{timestamp}"])
    return timestamp

def receive(py,msg):
    global e
    py-=1
    clock[py]=max(clock[py],msg)+1
    e+=1
    timestamp=clock[py]
    event.append([f"P{py+1}", f"E{e}", "RECEIVE ", f"{timestamp}"])

local(1)
print(clock)

m1=send(1,2)
print(clock)

receive(2,m1)
print(clock)

local(2)
print(clock)

m2=send(2,3)
print(clock)

local(1)
print(clock)

m3=send(1,3)
print(clock)

receive(3,m2)
print(clock)

receive(3,m3)
print(clock)

print("==========================================")
print("          LAMPORT LOGICAL CLOCK           ")
print("==========================================")
print("Process\tEvent\tType\tTimestamp")
print("------------------------------------------")
for e in event:
    print(e)
print("------------------------------------------")
