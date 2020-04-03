from grammar import Grammar, GrammarException


if __name__ == '__main__':
    __head = """
    ИУ7-23М
    Горин Дмитрий
    Вариант 3 (удаление eps-правил)
    """
    print(__head)

    g1 = Grammar.init_from_json_file('test_grammar.json')
    print(g1)
    print(g1.eps_rules)
    print(g1.find_eps_generative_nterms())
    print()

    g2 = g1.delete_eps_rules()
    print(g2)
    print()

    if g2.has_circuits():
        print('Грамматика без eps-правил содержит цепи, построить новую без левой рекурсии не получится')
        print('Вариант такой, я не виноват')
        exit(0)
