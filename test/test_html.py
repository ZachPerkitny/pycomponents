import textwrap

from pycomponents.context import Context
from pycomponents.html import HTMLSection


def test_textline_expr():
    source = textwrap.dedent(r'''
    li(class="test", id="test"):
        - Hello {msg}! 
        - {msg} was the message
    ''')
    context = Context({'msg': 'world'})
    result = HTMLSection(source).render(context)
    assert result == '<li class="test" id="test">Hello world! world was the message</li>'


def test_html_section_outputs_html():
    source = textwrap.dedent(r'''
    for i in ["hello", "world"]:
        li(class="test"):
            - test {i}
    ''')
    context = Context()
    result = HTMLSection(source).render(context)
    assert result == '<li class="test">test hello</li><li class="test">test world</li>'


def test_variable_assignment():
    source = textwrap.dedent('''
    var my_variable = "test"
    - my_variable is {my_variable}
    ''')
    context = Context()
    result = HTMLSection(source).render(context)
    assert result == 'my_variable is test'


def test_expression():
    source = textwrap.dedent('''
    - my variable is {(10 + 25) * 30}
    ''')
    context = Context()
    result = HTMLSection(source).render(context)
    assert result == 'my variable is 1050'
