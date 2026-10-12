P1=0
P2=0
P3=0
def local(process,clock,event):
    clock=clock+1
    print(process,event,"LOCAL",clock)
    return clock
def send(process,clock,event,receiver, message):
    clock=clock+1
    print(process,event,"SEND",clock,"->",receiver, message)
    return clock,message,clock
def receive(process,clock,event,message, sender, timestamp):
    clock=max(clock,timestamp)+1
    print(process,event,"RECEIVE",clock,"<-",sender,message)
    return clock


print("="*50)
print("LAMPORT LOGICAL CLOCK")
print("="*50)
P1=local("P1",P1,"E1")


P1,M1,T1=send("P1",P1,"E2","P2","M1")
P2=receive("P2",P2,"E3",M1,"P1",T1)
P2=local("P2",P2,"E4")
P2,M2,T2=send("P2",P2,"E5","P3","M2")
P1=local("P1",P1,"E6")


P1,M3,T3=send("P1",P1,"E7","P3","M3")
P3=receive("P3",P3,"E8",M2,"P2",T2)
P3=receive("P3",P3,"E9",M3,"P1",T3)


print("="*50)
print("Clocks:")
print("P1=",P1)
print("P2=",P2)
print("P3=",P3)
