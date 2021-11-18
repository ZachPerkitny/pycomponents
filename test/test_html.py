import textwrap

from pycomponents.context import Context
from pycomponents.html import HTMLSection


def test_textline_expr():
    section = textwrap.dedent(r'''
    li(class="test", id="test"):
        - Hello {msg}! 
        - {msg} was the message
    ''')
    context = Context({'msg': 'world'})
    result = HTMLSection().parse(section).render(context)
    assert result == '<li class="test" id="test">Hello world! world was the message</li>'


def test_html_section_outputs_html():
    section = textwrap.dedent(r'''
    for i in ["hello", "world"]:
        li(class="test"):
            - test {i}
    ''')
    context = Context()
    result = HTMLSection().parse(section).render(context)
    assert result == '<li class="test">test hello</li><li class="test">test world</li>'
