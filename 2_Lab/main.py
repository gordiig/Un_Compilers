from grammar import Grammar, GrammarException


if __name__ == '__main__':
    g1 = Grammar.init_from_json_file('test_grammar.json')
    print(g1.pretty_string())