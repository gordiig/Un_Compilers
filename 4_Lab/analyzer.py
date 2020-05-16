from typing import Tuple, List, Optional, Union


def _get_next_symbol(input_str: str) -> Tuple[str, str]:
    """
    Получение следующего символа в строке
    Символы >= <= == <> выдаются как один символ
    """
    cur_symbol = input_str[0]
    if cur_symbol in ('>', '=') and len(input_str) > 1 and input_str[1] == '=':
        cur_symbol += input_str[1]
        input_str = input_str[2:]
    elif cur_symbol == '<' and len(input_str) > 1 and input_str[1] in ('=', '>'):
        cur_symbol += input_str[1]
        input_str = input_str[2:]
    else:
        input_str = input_str[1:]
    return input_str, cur_symbol


def _get_priority(stack_symbol: str, next_symbol: str) -> Optional[str]:
    """
    Приоритеты
    """
    sum_ops = ('+', '-')
    mul_ops = ('*', '/', '%', '^')
    rel_ops = ('<', '<=', '>', '>=', '<>', '==')
    numbers = tuple(str(i) for i in range(10))

    if stack_symbol in sum_ops:
        return '>' if next_symbol in sum_ops + rel_ops + (')', '$') else '<'
    if stack_symbol in mul_ops:
        return '>' if next_symbol in sum_ops + mul_ops + rel_ops + (')', '$') else '<'
    if stack_symbol in rel_ops:
        return '>' if next_symbol in rel_ops + (')', '$') else '<'
    if stack_symbol in numbers:
        return '>' if next_symbol in sum_ops + mul_ops + rel_ops + (')', '$') else None
    if stack_symbol == '(':
        return '<' if next_symbol in sum_ops + mul_ops + rel_ops + numbers + ('(', ')') else None
    if stack_symbol == ')':
        return '>' if next_symbol in sum_ops + mul_ops + rel_ops + (')', '$') else None
    if stack_symbol == '$':
        return '<' if next_symbol in sum_ops + mul_ops + rel_ops + numbers + ('(', ) else None
    return None


def _get_nterm_of_rule(stack_slice: List) -> Optional[str]:
    """
    Получаем левую часть правила по правой
    """
    sum_ops = ('+', '-')
    mul_ops = ('*', '/', '%', '^')
    rel_ops = ('<', '<=', '>', '>=', '<>', '==')
    numbers = tuple(str(i) for i in range(10))
    if len(stack_slice) == 3:
        if ''.join(stack_slice) == '(E)':
            return 'E'
        if stack_slice[0] == 'E' and stack_slice[2] == 'E' and stack_slice[1] in sum_ops + mul_ops + rel_ops:
            return 'E'
    elif len(stack_slice) == 1:
        if stack_slice[0] in numbers:
            return 'E'
    return None


def analyze_string(input_str: str) -> Optional[str]:
    """
    ПС-анализатор
    """
    numbers = tuple(str(i) for i in range(10))
    numbers_stack = []
    input_str = ''.join([symbol for symbol in input_str if symbol not in [' ', '\n']]) + '$'
    stack = ['$']
    postfix = ''
    while stack != ['$', 'E'] or input_str != '$':
        # Получаем следующий символ в строке
        input_str, cur_symbol = _get_next_symbol(input_str)
        if cur_symbol in numbers:
            numbers_stack.append(cur_symbol)

        # Получаем приоритет
        last_term = [x for x in stack if x != 'E'][-1]
        pr = _get_priority(last_term, cur_symbol)
        if pr is None:
            return None

        if pr == '>':
            input_str = cur_symbol + input_str
            # Свертка
            for i in range(1, len(stack)):
                stack_slice = stack[-i:]
                lhs_nterm = _get_nterm_of_rule(stack_slice)
                if lhs_nterm is not None:
                    stack = stack[:-i]
                    stack.append(lhs_nterm)
                    if len(stack_slice) == 3 and stack_slice[0] != '(':
                        while len(numbers_stack) > 0:
                            postfix += numbers_stack.pop(0)
                        postfix += stack_slice[1]
                    break
            else:
                return None
        else:
            # Укладка в стек
            stack.append(cur_symbol)
    return postfix
