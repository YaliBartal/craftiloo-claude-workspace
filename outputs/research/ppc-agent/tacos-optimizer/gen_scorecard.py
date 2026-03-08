import json, sys
sys.stdout.reconfigure(encoding="utf-8")
data = json.loads(open("outputs/research/ppc-agent/tacos-optimizer/30d-parsed-corrected.json","r",encoding="utf-8").read())
print("data loaded")
