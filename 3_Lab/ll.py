from graphviz import Digraph
from grammar import Grammar, NoTermSymbol, TermSymbol


# def build_tree(grammar: Grammar, current_symbol, string_to_read) -> (bool, str):
#     flag = False
#     new_str = string_to_read
#     for production in grammar.rules[current_symbol]:
#         for prod_sym in production:
#             if isinstance(prod_sym, NoTermSymbol):
#                 flag, new_str = build_tree(grammar, prod_sym, new_str)
#             else:
#                 cur_term_sym = prod_sym.symbol
#                 if cur_term_sym == grammar.eps_terminal.symbol:
#                     flag = True
#                 elif cur_term_sym == new_str[:len(cur_term_sym)]:
#                     flag = True
#                     new_str = new_str[len(cur_term_sym):]
#                 else:
#                     flag = False
#             if not flag:
#                 break
#         if flag:
#             break
#     return flag, new_str


class TreeNode:
    def __init__(self, value: str, children: list = None):
        self.value = value
        self.children = children or []

    def clear_children(self):
        self.children = []

    def append_child(self, node: 'TreeNode'):
        self.children.append(node)

    def __str__(self):
        return f'{self.value} -> {self.children}'

    def __repr__(self):
        return str(self)


def build_tree(grammar: Grammar, current_symbol, string_to_read) -> (TreeNode, str):
    if isinstance(current_symbol, TermSymbol):  # Если терминал
        if current_symbol == grammar.eps_terminal:  # Если эпс-символ, то просто возвращаем его
            return TreeNode(current_symbol.symbol), string_to_read
        elif current_symbol.symbol == string_to_read[:len(current_symbol)]:  # Если в начале строки есть терминал, то ок
            return TreeNode(current_symbol.symbol), string_to_read[len(current_symbol):]
        else:  # Иначе ошибка, возвращаем None
            return None, string_to_read
    else:  # Если нетерминал
        for rule in grammar.rules[current_symbol]:  # По каждому правилу из грамматики по переданному нетерминалу
            new_str = string_to_read
            ret_node = TreeNode(current_symbol.symbol)
            for symbol in rule:  # По каждому символу в правиле
                symbol_children, new_str = build_tree(grammar, symbol, new_str)
                if symbol_children is None:  # Если хотя бы по одному символу ошибка -- правило не подходит
                    break
                ret_node.append_child(symbol_children)
            else:  # Если вышли без бряка, то нашли нужное поддерево
                return ret_node, new_str
    return None, string_to_read  # Если не нашлось верного правила, значит ошибка


def graph_tree(root_node: TreeNode, filename='tree'):
    d = Digraph()
    cnt = 0
    stack = [(root_node, cnt)]
    while len(stack) > 0:
        node, num = stack.pop()
        d.node(node.value + str(num), label=node.value)
        for child in node.children:
            cnt += 1
            stack.append((child, cnt))
            d.edge(node.value + str(num), child.value + str(cnt))
    d.save(filename)
    d.render(filename, view=True)
