from typing import Tuple, List, Union, Dict
from FSM import DFSMState, MinDFSMState


def format_table_for_tabulate_nka(tbl: Dict[str, Dict[str, List[str]]], alphabet) ->\
        Tuple[List[Union[str, List]], List[str]]:
    headers = ['eps'] + alphabet
    rows = []
    for state, row in tbl.items():
        cur_row = [str(state)] + list(row.values())
        rows.append(cur_row)
    return rows, headers


def format_table_for_tabulate_dka(dka: Union[List[DFSMState], List[MinDFSMState]], alphabet) ->\
        Tuple[List[str], List[str]]:
    headers = alphabet
    rows = []
    for state in dka:
        cur_row = [str(state)]
        for symbol in alphabet:
            state_lst = [x[0] for x in state.outputs if x[1] == symbol]
            if len(state_lst) == 0:
                cur_row.append('')
            elif len(state_lst) == 1:
                cur_row.append(state_lst[0])
            else:
                raise ValueError('Not DKA was given')
        rows.append(cur_row)
    return rows, headers
