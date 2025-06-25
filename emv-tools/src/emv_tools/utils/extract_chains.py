import json
from .proxy import proxify
from .validate_pdb import _validate_atom_line

from collections import namedtuple

Atom = namedtuple("Atom", ["name", "res_seq_name", "res_seq_number", "chain", "value"])


@proxify
def extract_chains(input_path):
    with open(input_path) as file:
        
        chains_dict = {}
        for line in file.readlines():
            if not line.startswith("ATOM"):
                continue


            _validate_atom_line(line)

            atom_name = line[12:16].strip()
            res_seq_name = line[17: 20]
            res_seq_number = int(line[22:26])
            chain_id = line[21]
            value = line[54:60]
            
            atom = Atom(atom_name, res_seq_name=res_seq_name, res_seq_number=res_seq_number, chain=chain_id, value=value)
            chains_dict[chain_id] = (chains_dict[chain_id] + [atom] if chain_id in chains_dict else [atom])

            
        chains = []
        for name, values in chains_dict.items():
            chain = {
                "name": name,
                "seqData": [{"resSeqName": v.res_seq_name, "resSeqNumber": v.res_seq_number, "scoreValue": v.value} for v in values]
            }

            chains.append(chain)

        outputs = {
            "resource": "DeepRes-Scores",
            "entry": {
                "volume_map": "",
                "atomic_model": "",
                "date": "" 
            },
            "chains": chains
        }


        with open("../data/converted.json", "w") as f:
            json.dump(outputs, f)
        

def main():
    
    
    extract_chains(
        "/home/max/Documents/val-server/EMV-Script-fork/emv-tools/data/output.atom.pdb"
    )    


if __name__ == "__main__":
    main()