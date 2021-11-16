import textwrap

from pycomponents.html import HTMLSection


def test_html_section_outputs_html():
    section = textwrap.dedent(r'''
    for i in [1,2,3]:
        li(key=i)
    ''')
    renderable = HTMLSection().parse(section)
