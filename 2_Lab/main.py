from grammar import Grammar, GrammarException


if __name__ == '__main__':
    g1 = Grammar.init_from_json_file('test_grammar.json')
    print(g1)
    print(g1.eps_rules)
    print(g1.find_eps_generative_rules())
