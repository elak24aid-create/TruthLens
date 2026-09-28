with open("backend/app/services/online_research.py", "r") as f:
    c = f.read()

c = c.replace('"supporting"', '"DIRECT_SUPPORT"')
c = c.replace('"conflicting"', '"DIRECT_CONTRADICTION"')
c = c.replace('"context"', '"CONTEXTUAL"')

with open("backend/app/services/online_research.py", "w") as f:
    f.write(c)
    
with open("backend/app/services/evidence_aggregator.py", "r") as f:
    ea = f.read()
ea = ea.replace('"supporting"', '"DIRECT_SUPPORT"')
ea = ea.replace('"conflicting"', '"DIRECT_CONTRADICTION"')

with open("backend/app/services/evidence_aggregator.py", "w") as f:
    f.write(ea)
