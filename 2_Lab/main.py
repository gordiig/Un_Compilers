from grammar import Grammar, GrammarException


if __name__ == '__main__':
    __head = """
    ИУ7-23М
    Горин Дмитрий
    Вариант 3 (удаление eps-правил)
    """
    print(__head)

    g1 = Grammar.init_from_json_file('test_grammar_4_9.json')
    print(g1)
    print()

    g2 = g1.delete_eps_rules()
    print(g2)
    print()

    g3 = g2.delete_direct_left_recursion()
    print(g3)
    print()

    g4 = g2.delete_left_recursion()
    print(g4)
    print()

    g5 = g4.delete_eps_rules()
    print(g5)
    print()
