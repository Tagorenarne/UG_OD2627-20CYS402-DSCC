class process:
    def __init__(self,name):
        self.name=name
        self.clock=0
    def localEvent(self,eventId):
        self.clock+=1
        return {"process":self.name,"event":eventId,"type":"Local","timestamp":self.clock}
    def sendEvent(self,eventId,receiver):
        self.clock+=1
        message={"messageId":f"msg_{eventId}","sender":self.name,"receiver":receiver,"timestamp":self.clock}
        eventRecord={"process":self.name,"event":eventId,"type":"send","timestamp":self.clock}
        return message,eventRecord
    def receiveEvent(self,eventId,message):
        self.clock=max(self.clock,message["timestamp"])+1
        return {"process":self.name,"event":eventId,"type":"receive","timestamp":self.clock}

def main():
    p1=process("P1")
    p2=process("P2")
    p3=process("P3")

    events=[]

    events.append(p1.localEvent("E1"))
    
    m1,e2=p1.sendEvent("E2",p2.name)
    events.append(e2)

    events.append(p2.receiveEvent("E3",m1))

    events.append(p2.localEvent("E4"))

    m2,e5=p2.sendEvent("E5",p3.name)
    events.append(e5)

    events.append(p1.localEvent("E6"))

    m3,e7=p1.sendEvent("E7",p3.name)
    events.append(e7)

    events.append(p3.receiveEvent("E8",m2))

    events.append(p3.receiveEvent("E9",m3))

    print("====================================================")
    print("             LAMPORT LOGICAL CLOCK")
    print("====================================================")
    print("")
    print(f"{'Process':<10} {'Event':<8} {'Type':<12} {'Timestamp':>10}")
    print("-" * 52)
    
    for e in events:
        print(f"{e['process']:<10} {e['event']:<8} {e['type']:<12} {e['timestamp']:>10}")
        
    print("-" * 52)

if __name__ == "__main__":
    main()
    

    
    
        
