class process:
    def __init__(self,name,index,n):
        self.name=name
        self.index=index
        self.clock=[0]*n
    def localEvent(self,eventId):
        self.clock[self.index]+=1
        return {"process":self.name,"event":eventId,"type":"LOCAL","message":"-","timestamp":self.clock.copy()}
    def sendEvent(self,eventId,receiver):
        self.clock[self.index]+=1
        message={"messageId":f"msg_{eventId}","sender":self.name,"receiver":receiver,"timestamp":self.clock.copy()}
        eventRecord={"process":self.name,"event":eventId,"type":"SEND","message":f"{self.name}->{receiver}","timestamp":self.clock.copy()}
        return message,eventRecord
    def receiveEvent(self,eventId,message):
        self.clock=[max(a,b) for a,b in zip(self.clock,message["timestamp"])]
        self.clock[self.index]+=1
        return {"process":self.name,"event":eventId,"type":"RECEIVE","message":f"{message['sender']}->{self.name}","timestamp":self.clock.copy()}

def compareVectors(v1,v2):
    less_or_equal=all(a<=b for a,b in zip(v1,v2))
    greater_or_equal=all(a>=b for a,b in zip(v1,v2))
    if less_or_equal and greater_or_equal:
        return "SAME"
    if less_or_equal:
        return "V1 -> V2"
    if greater_or_equal:
        return "V2 -> V1"
    return "V1 || V2"

def fmt(v):
    return "["+",".join(map(str,v))+"]"

def main():
    n=3
    p1=process("P1",0,n)
    p2=process("P2",1,n)
    p3=process("P3",2,n)

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
    print("             VECTOR LOGICAL CLOCK")
    print("====================================================")
    print("")
    print(f"{'Process':<10} {'Event':<8} {'Type':<12} {'Message':<10} {'Timestamp':>12}")
    print("-" * 56)

    for e in events:
        print(f"{e['process']:<10} {e['event']:<8} {e['type']:<12} {e['message']:<10} {fmt(e['timestamp']):>12}")

    print("-" * 56)

    ts={e["event"]:e["timestamp"] for e in events}

    print("")
    print("====================================================")
    print("             CAUSAL RELATIONSHIPS")
    print("====================================================")
    print("")
    print(f"{'Event A':<9} {'Event B':<9} {'Vector A':>10} {'Vector B':>10}   Relationship")
    print("-" * 66)

    pairs=[
        ("E1","E2","Same process ordering"),
        ("E2","E3","Message based causality"),
        ("E1","E9","Transitive causality"),
        ("E5","E8","Message based causality"),
        ("E6","E4","Concurrent events"),
        ("E7","E5","Concurrent events"),
        ("E8","E9","Same process ordering"),
    ]

    for a,b,note in pairs:
        result=compareVectors(ts[a],ts[b])
        result=result.replace("V1",a).replace("V2",b)
        print(f"{a:<9} {b:<9} {fmt(ts[a]):>10} {fmt(ts[b]):>10}   {result:<12} ({note})")

    print("-" * 66)

if __name__ == "__main__":
    main()
