from typing import List


# TEST_ALPHABET = [chr(x) for x in range(ord('a'), ord('z')+1)] + [chr(x) for x in range(ord('A'), ord('Z')+1)] + \
#                 [str(x) for x in range(10)]
TEST_ALPHABET = ['a', 'b']
TEST_OPS_PRECEDENCE = {
    '|': 0,
    '+': 2,
    '*': 2,
    '(': -1,
    ')': -1,
    '.': 1,
}
TEST_OPS = list(TEST_OPS_PRECEDENCE.keys())
ALL_TEST_SYMBOLS = TEST_ALPHABET + TEST_OPS
CONCAT_OP = TEST_OPS[-1]


class RegexpError(Exception):
    def __init__(self, message: str):
        self.message = message

    def __str__(self):
        return self.message


def get_postfix_regexp(regexp: str) -> List[str]:
    return __create_postfix_notation_regexp(__normalize_regexp(regexp))


def __normalize_regexp(regexp: str) -> str:
    """
    Добавление знака конкатенации к регулярке
    :param regexp: Регулярка
    :return: Регулярка со знаками конкатенации
    """
    nregexp = ''
    for i in range(len(regexp)-1):
        if regexp[i] not in ALL_TEST_SYMBOLS:
            raise RegexpError(message=f'Неизвестный символ "{regexp[i]}"')
        nregexp += regexp[i]
        if regexp[i] in TEST_ALPHABET and regexp[i+1] in TEST_ALPHABET:
            nregexp += CONCAT_OP
        elif regexp[i] in ('*', '+') and regexp[i+1] in TEST_ALPHABET:
            nregexp += CONCAT_OP
        elif regexp[i] in TEST_ALPHABET and regexp[i+1] == '(':
            nregexp += CONCAT_OP
    if regexp[-1] not in ALL_TEST_SYMBOLS:
        raise RegexpError(message=f'Неизвестный символ "{regexp[-1]}"')
    nregexp += regexp[-1]
    return nregexp


def __create_postfix_notation_regexp(normalized_regexp: str) -> List[str]:
    """
    Перевод регекспа из инфиксной записи в постфиксную
    :param normalized_regexp: Регулярка с символами конкатенации
    :return: Постфиксная нотация регекспа
    """
    queue = []
    stack = []
    while len(normalized_regexp) != 0:
        sym = normalized_regexp[0]
        normalized_regexp = normalized_regexp[1:]
        if sym in TEST_ALPHABET:
            queue.append(sym)
        elif sym == '(':
            stack.append('(')
        elif sym == ')':
            while len(stack) > 0 and stack[-1] != '(':
                queue.append(stack.pop())
            try:
                stack.pop()
            except IndexError:
                raise RegexpError('Не хватает открывающей скобки')
        elif sym in TEST_OPS:
            while len(stack) > 0 and TEST_OPS_PRECEDENCE[stack[-1]] >= TEST_OPS_PRECEDENCE[sym]:
                queue.append(stack.pop())
            stack.append(sym)
        else:
            raise RegexpError('Неизвестный символ в построении постфиксной формы')
    while len(stack) > 0:
        stack_sym = stack.pop()
        if stack_sym == '(':
            raise RegexpError('Не хватает закрывающей скобки')
        queue.append(stack_sym)
    return queue
