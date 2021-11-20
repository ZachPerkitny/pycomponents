import textwrap

from pycomponents.context import Context
from pycomponents.html import HTMLSection


def test_textline_expr():
    source = textwrap.dedent('''
    li(class="test", id="test"):
        - Hello {msg}! 
        - {msg} was the message
    ''')
    context = Context({'msg': 'world'})
    result = HTMLSection(source).render(context)
    assert result == '<li class="test" id="test">Hello world! world was the message</li>'


def test_if_stmt():
    source = textwrap.dedent('''
    test = True
    if test:
        - {test}
    else:
        - Something
    ''')
    context = Context()
    result = HTMLSection(source).render(context)
    assert result == 'True'


def test_elif_stmt():
    source = textwrap.dedent('''
        test = False
        test2 = True
        if test:
            - {test}
        elif test2:
            - {test2}
        else:
            - Something
        ''')
    context = Context()
    result = HTMLSection(source).render(context)
    assert result == 'True'


def test_else_stmt():
    source = textwrap.dedent('''
        test = False
        if test:
            - {test}
        else:
            - Something
        ''')
    context = Context()
    result = HTMLSection(source).render(context)
    assert result == 'Something'


def test_forloop_stmt():
    source = textwrap.dedent('''
    for i in ["hello", "world"]:
        li(class="test"):
            - test {i}
    ''')
    context = Context()
    result = HTMLSection(source).render(context)
    assert result == '<li class="test">test hello</li><li class="test">test world</li>'


def test_variable_assignment():
    source = textwrap.dedent('''
    my_variable = "test"
    - my_variable is {my_variable}
    ''')
    context = Context()
    result = HTMLSection(source).render(context)
    assert result == 'my_variable is test'


def test_expression():
    source = textwrap.dedent('''
    - my value is {(10 + 25) * 30}
    ''')
    context = Context()
    result = HTMLSection(source).render(context)
    assert result == 'my value is 1050'
