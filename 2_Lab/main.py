from grammar import Grammar, GrammarException


if __name__ == '__main__':
    __head = """
    ИУ7-23М
    Горин Дмитрий
    Вариант 3 (удаление eps-правил)
    """
    print(__head)

    print('Тест устранения епс-правил')
    g1 = Grammar.init_from_json_file('test_grammar_2_4_11.json')
    print(g1)
    print()
    g2 = g1.delete_eps_rules()
    print(g2)
    print()
    g_ans = Grammar.init_from_json_file('test_grammar_2_4_11_ans.json')
    print(g_ans)
    print()
    assert g2 == g_ans

    g1 = Grammar.init_from_json_file('test_grammar_2_23.json')
    print(g1)
    print()
    g2 = g1.delete_eps_rules()
    print(g2)
    print()
    g_ans = Grammar.init_from_json_file('test_grammar_2_23_ans.json')
    print(g_ans)
    print()
    assert g2 == g_ans

    print('Тест устранения левой рекурсии:')
    g1 = Grammar.init_from_json_file('test_grammar_4_9.json')
    print(g1)
    print()
    g2 = g1.delete_left_recursion()
    print(g2)
    print()
    g_ans = Grammar.init_from_json_file('test_grammar_4_9_ans.json')
    print(g_ans)
    print()
    assert g2 == g_ans

    print('Успешно')
