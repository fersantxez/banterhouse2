#!/usr/bin/env python3
"""RLE encode the fully verified input tape. Never encodes game state."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
data=(ROOT/'build/campaign-inputs.bin').read_bytes()
pairs=[]
for value in data:
 if pairs and pairs[-1][1]==value and pairs[-1][0]<255:pairs[-1][0]+=1
 else:pairs.append([1,value])
raw=bytes(v for pair in pairs for v in pair)
assert bytes(v for count,v in pairs for _ in range(count))==data
(ROOT/'src/generated/campaign_replay.h').write_text('/* Generated input-only demo; no game-state writes. */\n#define DEMO_TICKS %d\nstatic const u8 demo_inputs[%d] = {\n'%(len(data),len(raw))+'\n'.join('  '+','.join(map(str,raw[i:i+24]))+',' for i in range(0,len(raw),24))+'\n};\n')
(ROOT/'tests/fixtures/campaign-replay.json').write_text(json.dumps({'ticks':len(data),'sha256':hashlib.sha256(data).hexdigest(),'rle_bytes':len(raw),'rle_sha256':hashlib.sha256(raw).hexdigest(),'expected_terminal':{'stage':23,'mode':4,'score':36375}},indent=2)+'\n')
print(len(data),'input ticks ->',len(raw),'RLE bytes')
