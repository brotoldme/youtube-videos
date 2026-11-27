#!/usr/bin/env python3
import json, re, sys
R = {
 r"\blive[sd]?\b":"live->liv", r"\blead\b":"lead", r"\bwind\b":"wind", r"\bwound\b":"wound", r"\btear\b":"tear",
 r"\bclose\b":"close", r"\buse\b":"use", r"\bbass\b":"bass", r"\brow\b":"row", r"\bread\b":"read", r"\bminute\b":"minute",
 r"\bpresent\b":"present", r"\bcontent\b":"content", r"\bproject\b":"project", r"\brecord\b":"record", r"\bpermit\b":"permit",
 r"\bdesert\b":"desert", r"\bpolish\b":"polish", r"\bsubject\b":"subject", r"\bresume\b":"resume", r"\bbow\b":"bow", r"\bsow\b":"sow", r"\bdove\b":"dove"}
lines=[l for l in open(sys.argv[1]).read().split('\n') if l.strip()]
bad=0
for i,t in enumerate(lines):
    for rx,m in R.items():
        for x in re.finditer(rx,t,re.I): bad+=1; print(f"[{i+1}] {x.group(0)} -> {m} :: {t[:90]}")
print(f"RESULTAT: {bad} mot(s) a risque sur {len(lines)} phrases")
