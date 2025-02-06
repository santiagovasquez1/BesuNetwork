#!/usr/bin/env python3
import json
import rlp
import os

# 1. Leer el genesis.json
with open('/besu-config/networkFiles/genesis.json', 'r') as f:
    genesis = json.load(f)

extradata_hex = genesis["extraData"]  

extradata_bytes = bytes.fromhex(extradata_hex[2:])

decoded = rlp.decode(extradata_bytes)

validators_rlp = decoded[1]

validators = []
for val in validators_rlp:
    validators.append("0x" + val.hex())

print(validators)  

for i, address in enumerate(validators):
    old_folder = f"/besu-config/networkFiles/keys/{address}"
    new_folder = f"/besu-config/networkFiles/keys/{i}-{address}"
    os.rename(old_folder, new_folder)
