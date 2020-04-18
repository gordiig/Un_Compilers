from grammar import Grammar, NoTermSymbol, TermSymbol


def build_tree(grammar: Grammar, current_symbol, string_to_read) -> (bool, str):
    flag = False
    new_str = string_to_read
    for production in grammar.rules[current_symbol]:
        for prod_sym in production:
            if isinstance(prod_sym, NoTermSymbol):
                flag, new_str = build_tree(grammar, prod_sym, new_str)
            else:
                cur_term_sym = prod_sym.symbol
                if cur_term_sym == grammar.eps_terminal.symbol:
                    flag = True
                elif cur_term_sym == new_str[:len(cur_term_sym)]:
                    flag = True
                    new_str = new_str[len(cur_term_sym):]
                else:
                    flag = False
            if not flag:
                break
        if flag:
            break
    return flag, new_str
