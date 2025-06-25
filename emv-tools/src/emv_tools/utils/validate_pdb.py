from typing import List


def _is_int(value):
    try:
        int(value)
        return True
    except ValueError:
        return False
    
def _is_float(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

def _validate_atom_line(line):
    
    prefix_valid = line[0:4] == "ATOM"
    serial_number_valid = _is_int(line[6:11])

    res_seq_num_valid = _is_int(line[22:26])

    x_coord_valid = _is_float(line[30:38])
    y_coord_valid = _is_float(line[38:46])
    z_coord_valid = _is_float(line[46:54])

    occupancy_valid = _is_float(line[54:60])

    temp_valid = _is_float(line[60:66])

    return (
        prefix_valid and
        serial_number_valid and
        res_seq_num_valid and
        x_coord_valid and
        y_coord_valid and
        z_coord_valid and
        occupancy_valid and
        temp_valid
    )

def _validate_ter_line(line):

    serial_number_valid = _is_int(line[6:11])
    res_seq_num_valid = _is_int(line[22:26])

    return serial_number_valid and res_seq_num_valid

def validate_pdb_lines(lines: List[str]):
    def _is_valid(line):
        if line.startswith("ATOM"):
            return _validate_atom_line(line)
        elif line.startswith("TER"):
            return _validate_ter_line(line)
        else:
            return True

    for idx, line in enumerate(lines):
        if not _is_valid(line):
            raise ValueError(f"PDB file has incorrect format at line {idx}")
    
