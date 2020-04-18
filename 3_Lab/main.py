from grammar import Grammar
from ll import build_tree, graph_tree


if __name__ == '__main__':
    g = Grammar.init_from_json_file('grammar_g3_no_lrec_c.json')
    print(g, end='\n\n')

    initial = g.initial_nterm

    expr = '{x=2<2}'
    print(expr)
    is_ok, _ = build_tree(grammar=g, current_symbol=initial, string_to_read=expr)
    if is_ok is not None:
        graph_tree(is_ok, filename='2l2')
    print(f'{is_ok is not None}, должно быть True\n')

    expr = '{x=2*3>=2/4}'
    print(expr)
    is_ok, _ = build_tree(grammar=g, current_symbol=initial, string_to_read=expr)
    if is_ok is not None:
        graph_tree(is_ok, filename='2m3ge2d4')
    print(f'{is_ok is not None}, должно быть True\n')

    expr = '{x=(2+3)<2}'
    print(expr)
    is_ok, _ = build_tree(grammar=g, current_symbol=initial, string_to_read=expr)
    if is_ok is not None:
        graph_tree(is_ok, filename='p2p3pl2')
    print(f'{is_ok is not None}, должно быть True\n')

    expr = '{x=2===2}'
    print(expr)
    is_ok, _ = build_tree(grammar=g, current_symbol=initial, string_to_read=expr)
    if is_ok is not None:
        graph_tree(is_ok, filename='2eee2')
    print(f'{is_ok is not None}, должно быть False\n')

    expr = '{x=2=3/4==2}'
    print(expr)
    is_ok, _ = build_tree(grammar=g, current_symbol=initial, string_to_read=expr)
    if is_ok is not None:
        graph_tree(is_ok, filename='2a3d5ee2')
    print(f'{is_ok is not None}, должно быть False\n')
