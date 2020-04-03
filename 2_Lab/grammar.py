import json
from typing import List, Dict, Tuple, Union, Iterable, Any, Set


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
        elif isinstance(other, NoTermSymbol):
            return False
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
        elif isinstance(other, TermSymbol):
            return False
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
                 rules: Dict[Union[str, NoTermSymbol], List[List[Union[str, TermSymbol, NoTermSymbol]]]]):
        if start_nterm not in nterms:
            raise GrammarException('Начального нетерминала нет в списке нетерминалов',
                                   start_nterm=start_nterm, nterms=nterms)
        if eps_terminal not in terms:
            raise GrammarException('Пустого символа нет в списке терминалов',
                                   eps_terminal=eps_terminal, terms=terms)
        if len(nterms) < len(rules.keys()):
            raise GrammarException('Нетерминалов больше, чем правил', nterms=nterms, rules=rules)
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

    @property
    def eps_rules(self) -> List[NoTermSymbol]:
        ans = []
        for lhs, rhs in self.rules.items():
            eps_rule_lst = [x for x in rhs if x == [self.eps_terminal]]
            if len(eps_rule_lst) > 0:
                ans.append(lhs)
        return ans

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

    def is_eps_rule(self, rule: NoTermSymbol) -> bool:
        """
        Является ли правило eps-правилом
        :param rule: Левая часть правила (нетерминал)
        """
        return rule in self.eps_rules

    def has_circuits(self) -> bool:
        """
        Есть ли цепные правила в грамматике
        <Нетерминал> -> <Нетерминал>
        """
        for lhs, rhs in self.rules.items():
            for single_rule in rhs:
                if len(single_rule) == 1 and isinstance(single_rule[0], NoTermSymbol) and lhs != self.initial_nterm:
                    return True
        return False

    def term_count_for_rule(self, rule: NoTermSymbol) -> int:
        """
        Количество терминалов в правой части правила
        :param rule: Левая часть правила (нетерминал)
        """
        return len(self.find_terms_and_nterms_in_rule(rule)[0])

    def nterm_count_for_rule(self, rule: NoTermSymbol) -> int:
        """
        Количество нетерминалов в правой части правила
        :param rule: Левая часть правила (нетерминал)
        """
        return len(self.find_terms_and_nterms_in_rule(rule)[1])

    def find_rules_with_term_or_nterm_in_it(self, term: Union[NoTermSymbol, TermSymbol]) -> List[NoTermSymbol]:
        """
        Поиск правил, в правой части которых есть нетерминал или терминал
        :param term: Нетерминал или терминал
        """
        ans = []
        for lhs, rhs in self.rules.items():
            for single_rule in rhs:
                if term in single_rule:
                    ans.append(lhs)
        return ans

    def find_terms_and_nterms_in_rule(self, rule: NoTermSymbol) -> Tuple[List[TermSymbol], List[NoTermSymbol]]:
        """
        Поиск терминальных и нетерминальных символов в правой части
        """
        terms, nterms = [], []
        for single_rule in self.rules[rule]:
            terms.extend([x for x in single_rule if x in self.terms])
            nterms.extend([x for x in single_rule if x in self.nterms])
        return terms, nterms

    def find_rules_with_only_terms(self, with_empty: bool = True) -> List[NoTermSymbol]:
        """
        Поиск правил где в правой части только терминалы
        """
        ans = []
        for nterm in self.rules.keys():
            terms, nterms = self.find_terms_and_nterms_in_rule(nterm)
            if len(nterms) == 0:
                if len(terms) == 0 or ((len(terms) == 1) and with_empty):
                    ans.append(nterm)
        return ans

    def find_rules_with_only_nterms(self) -> List[NoTermSymbol]:
        """
        Поиск правил где в правой части только нетерминалы
        :return:
        """
        ans = []
        for nterm in self.rules.keys():
            terms, _ = self.find_terms_and_nterms_in_rule(nterm)
            if len(terms) == 0:
                ans.append(nterm)
        return ans

    def find_eps_generative_nterms(self) -> List[NoTermSymbol]:
        """
        Поиск eps-порождающих нетерминалов
        :return: Список нетерминалов
        """
        ans = set(self.eps_rules)
        i = 0
        while i < len(self.rules.items()):
            lhs, rhs = list(self.rules.items())[i]
            if lhs in ans:
                i += 1
                continue
            for single_rule in rhs:
                single_rule_set = set(single_rule)
                if len(single_rule_set.difference(ans)) == 0:
                    ans.add(lhs)
                    i = 0
                    break
            else:
                i += 1
        return list(ans)

    def __generate_all_possibke_comb_of_objs(self, objs: List, len_of_comb: int) -> List[List]:
        """
        Рекурсивная часть генерации комбинации (без пустого)
        """
        if len_of_comb == 0:
            return []
        ans = []
        i_st, i_end = 0, len_of_comb
        while i_end != len(objs) + 1:
            ans.append(objs[i_st:i_end])
            i_st += 1
            i_end += 1
        ans.extend(self.__generate_all_possibke_comb_of_objs(objs, len_of_comb-1))
        return ans

    def __generate_all_possible_comb_of_nterms(self, i_st, i_end, seq, single_rule) -> List[Union[TermSymbol, NoTermSymbol]]:
        """
        Генерация всех возможных комбинаций епс-нетерминалов (для удаления епс-правил)
        """
        all_combs = self.__generate_all_possibke_comb_of_objs(seq, len(seq)-1)
        all_combs.append([])
        ans = []
        for comb in all_combs:
            appendee = single_rule[:i_st] + comb + single_rule[i_end:]
            if len(appendee) != 0:
                ans.append(appendee)
        return ans

    def __find_all_nterm_eps_seq(self, single_rule, eps_gen_nterms) -> List[Tuple[List[NoTermSymbol], int, int]]:
        """
        Поиск всех последовательностей епс-нетерминалов в одном выводе
        """
        ans = []
        cur_seq = []
        i_st, i_end = 0, 0
        for i, sym in enumerate(single_rule):
            if sym in eps_gen_nterms:
                cur_seq.append(sym)
                i_end = i
            else:
                if len(cur_seq) == 0:
                    i_st += 1
                    continue
                # i_st = 0 if i_st == 0 else i_st + 1
                i_end += 1  # Указывает на следующий после последнего в последовательности епс-нетерминалов
                ans.append((cur_seq, i_st, i_end))
                cur_seq = []
                i_st = i_end+1
        if len(cur_seq) > 0:
            # i_st = 0 if i_st == 0 else i_st + 1
            i_end += 1  # Указывает на следующий после последнего в последовательности епс-нетерминалов
            ans.append((cur_seq, i_st, i_end))
        return ans

    def __generate_new_rhs(self, rhs, eps_gen_nterms) -> List[List[Union[TermSymbol, NoTermSymbol]]]:
        """
        Генерация новых выводов при удалении епс-правил
        """
        ans = set()
        already_computed = set()
        for single_rule in rhs:
            ans.add(tuple(single_rule))
            queue = [single_rule]
            while len(queue) > 0:
                current_rule = queue.pop()
                if tuple(current_rule) in already_computed:
                    continue
                already_computed.add(tuple(current_rule))
                all_nterm_seq = self.__find_all_nterm_eps_seq(current_rule, eps_gen_nterms)
                for nterm_seq in all_nterm_seq:
                    to_add = self.__generate_all_possible_comb_of_nterms(nterm_seq[1], nterm_seq[2], nterm_seq[0],
                                                                         current_rule)
                    for addee in to_add:
                        if tuple(addee) not in already_computed:
                            queue.append(addee)
                        ans.add(tuple(addee))
        return [list(x) for x in ans]

    def delete_eps_rules(self):
        """
        Удаление eps-правил
        :return: Грамматика без епс-правил
        """
        eps_gen_nterms = self.find_eps_generative_nterms()
        new_rules = self.rules.copy()
        new_nterms = set([x for x in self.nterms])
        new_initial = self.initial_nterm
        for lhs, rhs in self.rules.items():
            new_rules[lhs] = self.__generate_new_rhs(rhs, eps_gen_nterms)
            # Удаляем епс-переход
            new_rules[lhs] = [x for x in new_rules[lhs] if x != [self.eps_terminal]]
        # Если из старта можно получить eps, то заменяем стартовое состояние
        if self.initial_nterm in eps_gen_nterms:
            new_nterms.remove(self.initial_nterm)
            new_nterms.add(NoTermSymbol(self.initial_nterm.symbol, is_initial=False))
            new_initial = NoTermSymbol(f'{self.initial_nterm.symbol}\'', is_initial=True)
            new_nterms.add(new_initial)
            new_rules[new_initial] = [[NoTermSymbol(self.initial_nterm.symbol)], [TermSymbol(self.eps_terminal.symbol)]]
        return Grammar(name=f'{self.name} без eps-правил', terms=self.terms, nterms=new_nterms,
                       eps_terminal=self.eps_terminal, start_nterm=new_initial, rules=new_rules)

    def __str__(self):
        return f'Грамматика "{self.name}":\n{self.pretty_string()}'
