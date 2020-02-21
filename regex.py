from enum import Enum

class Token(Enum):
    char = 0
    plus = 1
    star = 2
    dot = 3
    g_start = 4
    g_end = 5

def tokenize(prog_text):
    tokens = []
    for c in prog_text:
        if c.isalpha() or c.isnumeric():
            tokens.append((Token.char, c))
        elif c == '.':
            tokens.append((Token.dot, c))
        elif c == '+':
            tokens.append((Token.plus, c))
        elif c == '*':
            tokens.append((Token.star, c))
        elif c == '(':
            tokens.append((Token.g_start, c))
        elif c == ')':
            tokens.append((Token.g_end, c))
    return tokens

class Node(Enum):
    plus = 0
    group = 1
    char = 2
    dot = 3
    star = 4
    concat = 5

def list_rindex(li, x):
    for i in reversed(range(len(li))):
        if li[i] == x:
            return i
    raise ValueError("{} is not in list".format(x))

def parse_RE(tokens):
    group = 0
    for c in reversed(tokens):
        if c[0] == Token.g_start:
            group += 1
        elif c[0] == Token.g_end:
            group -= 1
        elif group == 0 and c[0] == Token.plus:
            return parse_union(tokens)

    return parse_simple_RE(tokens)


def parse_union(tokens):
    plus_index = list_rindex(tokens, (Token.plus, '+'))
    beg = tokens[:plus_index]
    end = tokens[plus_index:]
    end.pop(0)
    return (Node.plus, parse_RE(beg), parse_simple_RE(end))


def parse_simple_RE(tokens):
    if is_basic_RE(tokens):
        return parse_basic_RE(tokens)
    return parse_concat(tokens)

def parse_concat(tokens):
    if tokens[-1][0] == Token.star:
        if tokens[-2][0] != Token.g_end:
            return (Node.concat, parse_simple_RE(tokens[:-2]), parse_basic_RE(tokens[-2:]))
        else:
            group = 0
            index = 0
            for i in range(len(tokens) - 2, 0, -1):
                if tokens[i][0] == Token.g_start:
                    group += 1
                elif tokens[i][0] == Token.g_end:
                    group -= 1
                if group == 0:
                    index = i
                    break
            return (Node.concat, parse_simple_RE(tokens[:index]), parse_basic_RE(tokens[index:]))
    elif tokens[-1][0] == Token.g_end:
        group = 0
        index = 0
        for i in range(len(tokens) - 1, 0, -1):
            if tokens[i][0] == Token.g_start:
                group += 1
            elif tokens[i][0] == Token.g_end:
                group -= 1
            if group == 0:
                index = i
                break
        return (Node.concat, parse_simple_RE(tokens[:index]), parse_basic_RE(tokens[index:]))
    else:
        return (Node.concat, parse_simple_RE(tokens[:-1]), parse_basic_RE(tokens[-1:]))


def parse_basic_RE(tokens):
    if is_star(tokens):
        return parse_star(tokens)
    return parse_elementary_RE(tokens)

def parse_star(tokens):
    return (Node.star, parse_elementary_RE(tokens[:-1]))

def parse_elementary_RE(tokens):
    if is_group(tokens):
        return parse_group(tokens)
    assert(len(tokens) == 1)
    if tokens[0][0] == Token.dot:
        return (Node.dot, '.')
    return (Node.char, tokens[0][1])

def parse_group(tokens):
    return (Node.group, parse_RE(tokens[1:-1]))

def is_group(tokens):
    return tokens[0][0] == Token.g_start and tokens[-1][0] == Token.g_end

def is_elementary_RE(tokens):
    return len(tokens) == 1 or is_group(tokens)

def is_star(tokens):
    return tokens[-1][0] == Token.star and is_elementary_RE(tokens[:-1])

def is_basic_RE(tokens):
    return is_elementary_RE(tokens) or is_star(tokens)

# <RE>              ::= <union> | <simple-RE>
# <union>           ::= <RE> "+" <simple-RE>
# <simple-RE>       ::= <concat> | <basic-RE>
# <concat>          ::= <simple-RE><basic-RE>
# <basic-RE>        ::= <star> | <elementary-RE>
# <star>            ::= <elementary-RE> "*"
# <elementary-RE>   ::= <group> | <any> | <char>
# <group>           ::= "(" <RE> ")"
# <any>             ::= "."
# <char>            ::= any numeric or alpha character






def eval_tree(tree):
    if tree[0] == Node.plus:
        return eval_plus(tree)
    elif tree[0] == Node.group:
        return eval_group(tree)
    elif tree[0] ==  Node.char:
        return eval_char(tree)
    elif tree[0] ==  Node.dot:
        return eval_dot(tree)
    elif tree[0] ==  Node.star:
        return eval_star(tree)
    elif tree[0] ==  Node.concat:
        return eval_concat(tree)


def eval_plus(tree):
    global txt_index
    old_txt_index = txt_index
    if not eval_tree(tree[1]):
        txt_index = old_txt_index
        return eval_tree(tree[2])
    return True

def eval_group(tree):
    return eval_tree(tree[1])

def eval_char(tree):
    global txt_index
    if text[txt_index] == tree[1]:
        txt_index += 1
        return True
    return False

def eval_dot(tree):
    global txt_index
    txt_index += 1
    return True

def eval_star(tree):
    global txt_index
    while True:
        if not eval_tree(tree[1]) or txt_index >= len(text):
            break
    return True

def eval_concat(tree):
    if eval_tree(tree[1]):
        return eval_tree(tree[2])
    return False

text = "maaaaaaaaaan"
txt_index = 0
tokens = tokenize('me+ma*n')
parse_tree = parse_RE(tokens)
if eval_tree(parse_tree):
    print("Match!")
    print(text[:txt_index])
else:
    print("No Match!")
