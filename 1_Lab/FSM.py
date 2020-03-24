from typing import List, Dict, Set, Tuple, Iterable, Union
from graphviz import Digraph


# MARK: - NFMS

class FiniteStateMachineNode:
    """
    Состояние конечного автомата
    outputs в формате [(node1, <символ перехода>), ...]
    """

    def __init__(self, state, outputs=None):
        if outputs is None:
            outputs = list()
        self.state = state
        self.outputs = outputs

    @property
    def is_end_state(self):
        return len(self.outputs) == 0

    def outputs_append(self, node, symbol='eps'):
        self.outputs.append((node, symbol))

    def __str__(self):
        return str(self.state)

    def __repr__(self):
        return str(self)


class NKA:
    """
    Класс для НКА
    """
    state_num = 0

    def __init__(self, root_state: FiniteStateMachineNode = None, symbol: str = 'eps'):
        if root_state:
            self.root_state = root_state
        else:
            st_node = FiniteStateMachineNode(state=NKA.state_num + 1)
            end_node = FiniteStateMachineNode(state=NKA.state_num + 2)
            st_node.outputs_append(end_node, symbol=symbol)
            self.root_state = st_node
            NKA.state_num += 2

    def copy(self):
        return NKA(self.root_state)

    @property
    def end_state(self):
        node = self.root_state
        while not node.is_end_state:
            node = node.outputs[0][0]
        return node

    def concat(self, nka):
        """
        (self) -eps-> (nka)
        """
        onode_1, onode_2 = self.copy(), nka.copy()
        onode_1.end_state.outputs_append(onode_2.root_state)
        return NKA(root_state=onode_1.root_state)

    def oorr(self, nka):
        """
            //eps->(self)-\
        (S)-|             |-eps->(F)
            \\eps->(nka)-/

        """
        st_node = FiniteStateMachineNode(state=NKA.state_num + 1)
        end_node = FiniteStateMachineNode(state=NKA.state_num + 2)
        onode_1, onode_2 = self.copy(), nka.copy()
        onode_1.end_state.outputs_append(end_node)
        onode_2.end_state.outputs_append(end_node)
        st_node.outputs_append(onode_1.root_state)
        st_node.outputs_append(onode_2.root_state)
        NKA.state_num += 2
        return NKA(root_state=st_node)

    def plus(self):
        """
            /<--------eps---------\
        (S) -eps-> (self) -eps-> (PF) -eps-> (F)
        """
        st_node = FiniteStateMachineNode(state=NKA.state_num + 1)
        pre_end_node = FiniteStateMachineNode(state=NKA.state_num + 2)
        end_node = FiniteStateMachineNode(state=NKA.state_num + 3)
        onode = self.copy()
        pre_end_node.outputs_append(end_node)
        pre_end_node.outputs_append(st_node)
        onode.end_state.outputs_append(pre_end_node)
        st_node.outputs_append(onode.root_state)
        NKA.state_num += 3
        return NKA(root_state=st_node)

    def star(self):
        """
            /<--------eps---------\
        (S) -eps-> (self) -eps-> (PF) -eps-> (F)
            \\--------eps-------->/
        """
        st_node = FiniteStateMachineNode(state=NKA.state_num + 1)
        pre_end_node = FiniteStateMachineNode(state=NKA.state_num + 2)
        end_node = FiniteStateMachineNode(state=NKA.state_num + 3)
        onode = self.copy()
        pre_end_node.outputs_append(end_node)
        pre_end_node.outputs_append(st_node)
        onode.end_state.outputs_append(pre_end_node)
        st_node.outputs_append(end_node)
        st_node.outputs_append(onode.root_state)
        NKA.state_num += 3
        return NKA(root_state=st_node)

    def __get_table_row(self, alphabet: List[str]) -> Dict[str, List[str]]:
        ans = {'eps': []}
        for sym in alphabet:
            ans[sym] = []
        return ans

    def get_as_table(self, alphabet: List[str]) -> Dict[str, Dict[str, List[str]]]:
        """
        Автомат в виде таблицы
        """
        ans = {}
        already_seen = []
        stack = [self.root_state]
        while len(stack) > 0:
            node = stack.pop()
            if str(node.state) in already_seen:
                continue
            already_seen.append(str(node.state))
            for nd, sym in node.outputs:
                stack.append(nd)
                try:
                    row = ans[str(node.state)]
                except KeyError:
                    ans[str(node.state)] = self.__get_table_row(alphabet)
                    row = ans[str(node.state)]
                row[sym].append(str(nd.state))
        ans['f'] = self.__get_table_row(alphabet)
        return ans


def generate_nfsm_from_pregexp(pregexp: List[str], alphabet: List) -> NKA:
    """
    Генерация НКА из постфиксной регулярки
    :param alphabet: Допустимый алфавит
    :param pregexp: Постфиксная регулярка
    :return: Начальное состояние НКА
    """
    stack = []
    while len(pregexp) > 0:
        cur_symbol = pregexp.pop(0)
        if cur_symbol in alphabet:
            stack.append(NKA(symbol=cur_symbol))
        elif cur_symbol == '.':
            nka2 = stack.pop()
            nka1 = stack.pop()
            new_nka = nka1.concat(nka2)
            stack.append(new_nka)
        elif cur_symbol == '|':
            nka2 = stack.pop()
            nka1 = stack.pop()
            new_nka = nka1.oorr(nka2)
            stack.append(new_nka)
        elif cur_symbol == '*':
            nka = stack.pop()
            new_nka = nka.star()
            stack.append(new_nka)
        elif cur_symbol == '+':
            nka = stack.pop()
            new_nka = nka.plus()
            stack.append(new_nka)
    start_node = FiniteStateMachineNode(state='s')
    end_node = FiniteStateMachineNode(state='f')
    nka = stack.pop()
    nka.end_state.outputs_append(end_node)
    start_node.outputs_append(nka.root_state)
    return NKA(root_state=start_node)


def draw_nka_gz(nka: NKA):
    d = Digraph()
    stack = [nka.root_state]
    already_was = []
    while len(stack) > 0:
        node = stack.pop()
        if node.state in already_was:
            continue
        already_was.append(node.state)
        for tpl in node.outputs:
            d.edge(f'{node.state}', f'{tpl[0].state}', label=tpl[1])
            stack.append(tpl[0])
    with open('nka', 'w') as f:
        f.write(d.source)
    d.render('nka', view=True)


# MARK: - DFMS

class DFSMState:
    """
    Класс для состояния ДКА
    """

    def __init__(self, state: str, nka_states: Set[str], outputs: List[Tuple[str, str]] = None, is_final=False):
        """
        :param state: Состояние
        :param nka_states: Множество состояний НКА, соответствующих данному состоянию ДКА
        :param outputs: Переходы в другие состояния в формате (state, symbol)
        :param is_final: Является ли состояние финальным
        """
        self.state = state
        self.nka_states = nka_states
        self.outputs = outputs or []
        self.is_final = is_final
        if self.is_final:
            self.state += 'f'

    def append_output(self, state: str, symbol: str):
        self.outputs.append((state, symbol))

    def __str__(self):
        return self.state

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return self.nka_states == other.nka_states

    def __hash__(self):
        return hash(frozenset(self.nka_states))


def generate_dfsm_from_nfsm(nfsm: Dict[str, Dict[str, List[str]]], alphabet: List[str]) -> List[DFSMState]:
    """
    Преобразование НКА (табличного представления) в ДКА (по сути тоже в табличное) по алгоритму из Ульмана
    :param nfsm: НКА
    :param alphabet: Допустимый алфавит
    :return: ДКА
    """
    ans = []
    __ec = __eps_closure_for_nka_state(nfsm, 's')
    stack = [DFSMState('s', __ec, is_final='f' in __ec)]
    marked_states = [(stack[0].nka_states, 's')]
    states_cnt = 1
    while len(stack) > 0:
        dstate = stack.pop()
        for asymbol in alphabet:
            move_by_asymbol = __move_closure_for_set_of_nka_states(nfsm, dstate.nka_states, asymbol)
            u = __eps_closure_for_set_of_nka_states(nfsm, move_by_asymbol)
            new_dstate = DFSMState(state=str(states_cnt), nka_states=u, is_final='f' in u)
            if new_dstate not in ans and new_dstate not in stack:
                stack.append(new_dstate)
                states_cnt += 1
                marked_states.append((new_dstate.nka_states, new_dstate.state))
            dstate.append_output(state=[x[1] for x in marked_states if x[0] == u][0], symbol=asymbol)
        ans.append(dstate)
    return __remove_states_without_inputs(ans)


def __remove_states_without_inputs(dka: List[DFSMState]) -> List[DFSMState]:
    seen_in_output = {'s', 'sf'}
    for state in dka:
        for ostate, _ in state.outputs:
            seen_in_output.add(ostate)
    ans = []
    for state in dka:
        if state.state in seen_in_output:
            ans.append(state)
    return ans


def __eps_closure_for_nka_state(nfsm, state: str) -> Set[str]:
    """
    Поиск эпсилон-замыкания из множества state
    :param nfsm: НКА
    :param state: Состояние
    :return: Множество состояний, достижимых из данного только по eps-переходам
    """
    ans = {state}
    stack = [state]
    was_seen = []
    while len(stack) > 0:
        cur_state = stack.pop()
        if cur_state in was_seen:
            continue
        was_seen.append(cur_state)
        ans.add(state)
        to_ext = nfsm[cur_state]['eps']
        ans.update(to_ext)
        stack.extend(to_ext)
    return ans


def __eps_closure_for_set_of_nka_states(nfsm, states) -> Set[str]:
    """
    Поиск эпсилон-замыкания из множества состояний states
    :param nfsm: НКА
    :param states: Состояния
    :return: Множество состояний, достижимых из данного множества состояний только по eps-переходам
    """
    ans = set()
    for state in states:
        eps_closure_for_state = __eps_closure_for_nka_state(nfsm, state)
        ans.update(eps_closure_for_state)
    return ans


def __move_closure_for_nka_state(nfsm, state: str, symbol: str) -> Set[str]:
    """
    Поиск состояний, напрямую достижимых из данного по символу
    :param nfsm: НКА
    :param state: Состояние
    :param symbol: Символ
    :return: Множество состояний, достижимых из данного по символу symbol
    """
    return set(nfsm[state][symbol])


def __move_closure_for_set_of_nka_states(nfsm, states, symbol: str) -> Set[str]:
    """
    Поиск состояний, напрямую достижимых из данного множества по символу
    :param nfsm: НКА
    :param states: Состояния
    :param symbol: Символ
    :return: Множество состояний, достижимых из данного множества состояний по символу symbol
    """
    ans = set()
    for state in states:
        cur_move_closure = __move_closure_for_nka_state(nfsm, state, symbol)
        ans.update(cur_move_closure)
    return ans


# MARK: - Min DFMS

class MinDFSMState:
    """
    Класс для состояния минимального ДКА
    """

    def __init__(self, state: str, dka_states: Set[DFSMState], outputs: List[Tuple[str, str]] = None, is_final=False):
        """
        :param state: Состояние
        :param dka_states: Множество состояний ДКА, соответствующих данному состоянию минимального ДКА
        :param outputs: Переходы в другие состояния в формате (state, symbol)
        :param is_final: Является ли состояние финальным
        """
        self.state = state
        self.dka_states = dka_states
        self.outputs = outputs or []
        self.is_final = is_final
        if is_final:
            self.state += 'f'

    @property
    def dka_states_names(self) -> Set[str]:
        return set([x.state for x in self.dka_states])

    def append_output(self, state: str, symbol: str):
        self.outputs.append((state, symbol))

    def set_as_final(self):
        self.is_final = True
        if self.state[-1] != 'f':
            self.state += 'f'

    def state_as_not_final(self):
        self.is_final = False
        if self.state[-1] == 'f':
            self.state = self.state[:-1]

    def is_start_state(self):
        return 's' in self.state

    def __str__(self):
        return self.state

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return self.dka_states == other.dka_states

    def __hash__(self):
        return hash(frozenset(self.dka_states))


def generate_min_dka_from_dka(dka: List[DFSMState], alphabet: List[str]) -> List[MinDFSMState]:
    """
    Генерация минимального ДКА из ДКА
    :param dka: ДКА
    :param alphabet: Допустимый алфавит
    :return: Минимальный ДКА
    """
    # Применение алгоритма Хопкрофта
    new_states_sets = __hopcroft_main_job(dka, alphabet)
    # Создание состояний минимального ДКА без переходов
    new_states = []
    for i, states_set in enumerate(new_states_sets):
        dka_states_set = set([x for x in states_set])
        dka_states_names = set([x.state for x in states_set])
        is_final = any([x.is_final for x in states_set])
        state_name = f'{i}{"s" if len(dka_states_names.intersection({"s", "sf"})) != 0 else ""}'
        new_state = MinDFSMState(state=state_name, dka_states=dka_states_set, is_final=is_final)
        new_states.append(new_state)
    # Создание переходов
    for state in new_states:
        outputs = __create_outputs_for_min_dka_state(new_states, state)
        state.outputs = outputs
    return new_states


def __hopcroft_main_job(dka: List[DFSMState], alphabet: List[str]) -> List[Set[DFSMState]]:
    """
    Функция алгоритма Хопкрофта
    """
    fins, non_fins = __find_finals_and_rest(dka)
    w = [fins]
    p = [fins]
    if len(non_fins) != 0:  # Может быть такое, что все состояния ДКА -- финальные, и пустого множества нам не надо
        w.append(non_fins)
        p.append(non_fins)
    while len(w) > 0:
        s = w.pop(0)
        for asym in alphabet:
            inputs = __find_all_inputs_for_states(dka, s, asym)
            for r in p:
                if len(r.intersection(inputs)) == 0 or r.issubset(inputs):
                    continue
                r1 = r.intersection(inputs)
                r2 = r.difference(r1)
                p.remove(r)
                p.append(r1)
                p.append(r2)
                if r in w:
                    w.remove(r)
                    w.append(r1)
                    w.append(r2)
                else:
                    r_min = r1 if len(r1) < len(r2) else r2
                    w.append(r_min)
    return p


def __find_finals_and_rest(dka: Iterable[DFSMState]) -> Tuple[Set[DFSMState], Set[DFSMState]]:
    """
    Поиск всех финальных и нефинальных состояний ДКА
    :param dka: ДКА
    :return: Списки финальных и нефинальных состояний
    """
    fin = set()
    non_fin = set()
    for state in dka:
        if state.is_final:
            fin.add(state)
        else:
            non_fin.add(state)
    return fin, non_fin


def __find_all_inputs_for_state(dka: List[DFSMState], dka_state: DFSMState, sym: str) -> Set[DFSMState]:
    """
    Поиск состояний, входящих в данное
    :param dka: ДКА
    :param dka_state: Состояние, входы в которое мы ищем
    :param sym: По данному символу
    :return: Названия входящих состояний
    """
    ans = set()
    for state in dka:
        if (dka_state.state, sym) in state.outputs:
            ans.add(state)
    return ans


def __find_all_inputs_for_states(dka: List[DFSMState], dka_states: Iterable[DFSMState], sym: str) -> Set[DFSMState]:
    """
    То же самое, но для множества состояний
    """
    ans = set()
    for state in dka_states:
        ans.update(__find_all_inputs_for_state(dka, state, sym))
    return ans


def __create_outputs_for_min_dka_state(min_dka: List[MinDFSMState], state: MinDFSMState) -> List[Tuple[str, str]]:
    """
    Создание списка выходов для состояния минимального ДКА
    """
    outputs = []
    dka_outputs = next(iter(state.dka_states)).outputs
    for dka_state_name, sym in dka_outputs:
        state_to_go = [x for x in min_dka if dka_state_name in x.dka_states_names][0]
        outputs.append((state_to_go.state, sym))
    return outputs


def draw_dka_gz(dka: Union[List[DFSMState], List[MinDFSMState]], is_min=False):
    d = Digraph()
    filename = 'dka_min' if is_min else 'dka'
    for state in dka:
        for output_state, symbol in state.outputs:
            d.edge(state.state, output_state, label=symbol)
    with open(filename, 'w') as f:
        f.write(d.source)
    d.render(filename, view=True)


def dka_job(dka: List[MinDFSMState], word: str) -> bool:
    """
    Функция, моделирующая КА
    """
    cur_state = [x for x in dka if x.is_start_state()][0]
    while len(word) > 0:
        sym = word[0]
        word = word[1:]
        try:
            state_to_go = [x[0] for x in cur_state.outputs if x[1] == sym][0]
        except IndexError:
            raise ValueError(f'Символа {sym} нет в допустимом алфавите!')
        cur_state = [x for x in dka if x.state == state_to_go][0]
    return cur_state.is_final


# MARK: - All in one
def generate_min_dka_from_pregexp(pregexp, alphabet) -> List[MinDFSMState]:
    """
    Получение минимального ДКА для постфиксного регекспа
    """
    nka = generate_nfsm_from_pregexp(pregexp, alphabet)
    dka = generate_dfsm_from_nfsm(nka.get_as_table(alphabet), alphabet)
    min_dka = generate_min_dka_from_dka(dka, alphabet)
    return min_dka
