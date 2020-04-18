from grammar import Grammar
from ll import build_tree


if __name__ == '__main__':
    g = Grammar.init_from_json_file('grammar_g3_no_lrec_c.json')
    print(g, end='\n\n')

    initial = g.initial_nterm

    expr = '{x=2==2}'
    print(expr)
    is_ok, _ = build_tree(grammar=g, current_symbol=initial, string_to_read=expr)
    print(f'{is_ok}, должно быть True\n')

    expr = '{x=2*3>=2/4}'
    print(expr)
    is_ok, _ = build_tree(grammar=g, current_symbol=initial, string_to_read=expr)
    print(f'{is_ok}, должно быть True\n')

    expr = '{x=(2+3)<2}'
    print(expr)
    is_ok, _ = build_tree(grammar=g, current_symbol=initial, string_to_read=expr)
    print(f'{is_ok}, должно быть True\n')

    expr = '{x=2===2}'
    print(expr)
    is_ok, _ = build_tree(grammar=g, current_symbol=initial, string_to_read=expr)
    print(f'{is_ok}, должно быть False\n')

    expr = '{x=2=3/4==2}'
    print(expr)
    is_ok, _ = build_tree(grammar=g, current_symbol=initial, string_to_read=expr)
    print(f'{is_ok}, должно быть False\n')

