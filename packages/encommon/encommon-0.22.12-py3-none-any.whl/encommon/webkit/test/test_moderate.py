"""
Functions and routines associated with Enasis Network Common Library.

This file is part of Enasis Network software eco-system. Distribution
is permitted, for more information consult the project license file.
"""



from typing import TYPE_CHECKING

from selenium.webdriver.remote.webdriver import WebDriver

from . import _executejs

if TYPE_CHECKING:
    from ..content import Content



def test_moderate(
    content: 'Content',
    driver: WebDriver,
) -> None:
    """
    Perform various tests associated with relevant routines.

    :param content: Primary class instance for the content.
    :param driver: Selenium driver provided by the library.
    """


    driver.get(
        f"""
        data:text/html;
        charset=utf-8,
        <html>
          <head>
            <script>
        {content.scripts('default')}
        {content.scripts('helpers')}
        {content.scripts('image')}
        {content.scripts('moderate')}
            </script>
          </head>
          <body></body>
        </html>
        """)


    outcome = _executejs(
        driver,
        'let element ='
        ' moderate(...arguments);'
        'return'
        ' element[0].outerHTML;',
        'This is a Label',
        'success',
        'some_kind_short',
        wrap=False)


    assert outcome == (
        '<div class="encommon_moderate">'
        '<div class="_icon">'
        '<div class="encommon_svgicon"'
        ' data-image="success"></div>'
        '</div>'
        '<div class="_value">'
        '<div class="_label">'
        'This is a Label</div>'
        '<div class="_small">'
        'some_kind_short</div>'
        '</div>'
        '</div>')
