from tabulate import tabulate
from utils import format_table_for_tabulate_dka, format_table_for_tabulate_nka
from regexp_process import get_postfix_regexp, TEST_ALPHABET, ALL_TEST_SYMBOLS, RegexpError
from FSM import generate_nfsm_from_pregexp, draw_nka_gz, \
    generate_dfsm_from_nfsm, draw_dka_gz, \
    generate_min_dka_from_dka, \
    generate_min_dka_from_pregexp, \
    dka_job

# TEST_REGEXP = 'ab|baba(abb*)+'
# TEST_REGEXP = '(b|ab*ab*)*'
# TEST_REGEXP = '(ab)*|ba'
# TEST_REGEXP = '(a|b)*abb'
# TEST_REGEXP = 'a|b|c'
# TEST_REGEXP = 'ab'
# TEST_REGEXP = 'a*'


if __name__ == '__main__':
    # Ввод регулярки
    TEST_REGEXP = input('Введите выражение, для которого необходимо построить автомат: ')
    if [x for x in TEST_REGEXP if x not in ALL_TEST_SYMBOLS]:
        print('Выражение не соответствует допустимому алфавиту')
        exit(1)

    # Построение постфиксной формы
    postfix_regexp = ''
    try:
        postfix_regexp = get_postfix_regexp(TEST_REGEXP)
        print(f'Постфиксная запись регулярного выражения: {"".join(postfix_regexp)}')
    except RegexpError as e:
        print(e)
        exit(1)

    # Генерация НКА и вывод
    nka = generate_nfsm_from_pregexp(postfix_regexp, TEST_ALPHABET)
    table, headers = format_table_for_tabulate_nka(nka.get_as_table(TEST_ALPHABET), TEST_ALPHABET)
    print('\nНКА:')
    print(tabulate(table, headers=headers))
    draw_nka_gz(nka)

    # Генерация ДКА и вывод
    dka = generate_dfsm_from_nfsm(nka.get_as_table(TEST_ALPHABET), TEST_ALPHABET)
    table, headers = format_table_for_tabulate_dka(dka, TEST_ALPHABET)
    print('\nДКА:')
    print(tabulate(table, headers=headers))
    draw_dka_gz(dka)

    # Генерация минимального ДКА и вывод
    min_dka = generate_min_dka_from_dka(dka, TEST_ALPHABET)
    table, headers = format_table_for_tabulate_dka(min_dka, TEST_ALPHABET)
    print('\nМинимальный ДКА:')
    print(tabulate(table, headers=headers))
    draw_dka_gz(min_dka, is_min=True)

    # Цикл моделирования работы КА
    to_check = ''
    while to_check != '$':
        to_check = input('\nВведите слово, которое нужно проверить ($ для завершения): ')
        try:
            is_ok = dka_job(min_dka, to_check)
        except ValueError as e:
            if to_check == '$':
                break
            print(e)
            continue
        if is_ok:
            print('Автомат допускает введенное слово')
        else:
            print('Автомат не допускает введенное слово')

    # Конец
    print('Пока-пока :)')
