import json
from typing import List, Dict, Tuple, Union, Iterable, Any


class GrammarException(Exception):
    def __init__(self, msg: str='Неизвестная ошибка грамматики', *args, **kwargs):
        self.msg = msg
        self.given_args = args
        self.given_kwargs = kwargs

    def __str__(self):
        return f'{self.msg}, args = {self.given_args}, kwargs = {self.given_kwargs}'

    def __repr__(self):
        return str(self)


class TermSymbol:
    """
    Класс для терминального символа
    """
    def __init__(self, symbol: str):
        if symbol.lower() != symbol:
            raise GrammarException('Символ для терминала должен быть в нижнем регистре', symbol)
        self.symbol = symbol

    def __eq__(self, other):
        if isinstance(other, str):
            return self.symbol == other
        elif isinstance(other, TermSymbol):
            return self.symbol == other.symbol
        else:
            raise TypeError('TermSymbol можно сравнивать только со строками и другими объектами класса TermSymbol')

    def __hash__(self):
        return hash(self.symbol)

    def __str__(self):
        return self.symbol

    def __repr__(self):
        # return f'Терминал "{self.symbol}"'
        return f'{self.symbol}(t)'


class NoTermSymbol:
    """
    Класс для нетерминального символа
    """
    def __init__(self, symbol: str, is_initial: bool = False):
        if symbol.upper() != symbol:
            raise GrammarException('Символ для нетерминала должен быть в верхнем регистре', symbol)
        self.symbol = symbol
        self.is_initial = is_initial

    def __eq__(self, other):
        if isinstance(other, str):
            return self.symbol == other
        elif isinstance(other, NoTermSymbol):
            return self.symbol == other.symbol
        else:
            raise TypeError('NoTermSymbol можно сравнивать только со строками и другими объектами класса NoTermSymbol')

    def __hash__(self):
        return hash(self.symbol)

    def __str__(self):
        return self.symbol

    def __repr__(self):
        # return f'Нетерминал {self.symbol}, is_initial: {self.is_initial}'
        return f'{self.symbol}(nt{"i" if self.is_initial else ""})'


class Grammar:
    """
    Класс для грамматики
    """
    def __init__(self, name: str,
                 terms: Iterable[Union[str, TermSymbol]],
                 nterms: Iterable[Union[str, NoTermSymbol]],
                 eps_terminal: Union[str, TermSymbol],
                 start_nterm: Union[str, NoTermSymbol],
                 rules: Dict[Union[str, NoTermSymbol], List[List[Union[str, TermSymbol]]]]):
        if start_nterm not in nterms:
            raise GrammarException('Начального нетерминала нет в списке нетерминалов',
                                   start_nterm=start_nterm, nterms=nterms)
        if eps_terminal not in terms:
            raise GrammarException('Пустого символа нет в списке терминалов',
                                   eps_terminal=eps_terminal, terms=terms)
        self.name = name
        self.terms = set([x if isinstance(x, TermSymbol) else TermSymbol(x) for x in terms])
        self.nterms = set([x if isinstance(x, NoTermSymbol) else NoTermSymbol(x, x == start_nterm) for x in nterms])
        self.eps_terminal = eps_terminal if isinstance(eps_terminal, TermSymbol) else TermSymbol(eps_terminal)
        self.rules = dict()
        for lhs, rhs in rules.items():
            nterm = [x for x in self.nterms if x == lhs]
            if len(nterm) == 0:
                raise GrammarException('Правило вывода содержит нетерминал, которого нет в списке нетерминалов',
                                       lhs=lhs, rhs=rhs, nterms=self.nterms)
            cur_lhs = nterm[0]
            cur_rhs = []
            for rhs_part in rhs:
                cur_part = []
                for operand in rhs_part:
                    if operand in self.terms:
                        cur_part.append([x for x in self.terms if x == operand][0])
                    elif operand in self.nterms:
                        cur_part.append([x for x in self.nterms if x == operand][0])
                    else:
                        raise GrammarException('Правило вывода содержит символ, которого нет в грамматике',
                                               lhs=lhs, rhs=rhs, rhs_part=rhs_part, nterms=self.nterms, terms=self.terms)
                cur_rhs.append(cur_part)
            self.rules[cur_lhs] = cur_rhs

    @property
    def initial_nterm(self):
        return [x for x in self.nterms if x.is_initial][0]

    @staticmethod
    def init_from_json_file(filename: str):
        """
        Создание грамматики из json-файла
        :param filename: Имя файла
        :return: Грамматика
        """
        with open(filename, 'r') as f:
            data = json.loads(f.read())
        try:
            return Grammar(name=data['name'], terms=data['terms'], nterms=data['nterms'],
                           eps_terminal=data['eps_terminal'], start_nterm=data['start_nterm'], rules=data['rules'])
        except KeyError:
            raise GrammarException('Неправильный формат входного файла')

    def save_to_file(self, filename: str):
        """
        Сохранение грамматики в файл
        :param filename: Имя файла
        """
        data = {
            'name': self.name,
            'terms': [x.symbol for x in self.terms],
            'nterms': [x.symbol for x in self.nterms],
            'eps_terminal': self.eps_terminal.symbol,
            'start_nterm': self.initial_nterm.symbol,
            'rules': dict()
        }
        for lhs, rhs in self.rules.items():
            data['rules'][lhs.symbol] = [[y.symbol for y in x] for x in self.rules[lhs]]
        with open(filename, 'w') as f:
            f.write(json.dumps(data, indent=4))

    def pretty_string(self):
        ans = ''
        for lhs, rhs in self.rules.items():
            ans += f'{lhs} -> '
            for rule in rhs:
                ans += f'{"".join([x.symbol for x in rule])} | '
            ans = ans[:-2] + '\n'
        ans = ans[:-1]
        return ans
