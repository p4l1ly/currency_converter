from lxml import html
from .helpers import get
import os

up = os.path.dirname
STATIC_PATH = os.path.join(
    up(up(os.path.realpath(__file__))), 'resources', 'symbols.html')

def from_all(symbol):
    """
    Convert currency symbol into currency code. Try to find it by scraping
    http://www.xe.com/symbols.php, use static table as fallback.

    :param symbol: symbol to convert
    :type symbol: `str`

    :returns: currency code
    :rtype: `str`
    """
    for dict_fn in [from_xe, from_static]:
        try:
            return dict_fn(symbol)
        except Exception as e:
            err = e

    raise err

def from_xe(symbol):
    """
    Scrap page http://www.xe.com/symbols.php containing a currency table to
    convert the symbol into currency code.

    :param symbol: symbol to convert
    :type symbol: `str`

    :returns: currency code
    :rtype: `str`
    """
    text = get('http://www.xe.com/symbols.php').text
    root = html.fromstring(text)
    return root.xpath("""
        .//table[@class="currencySymblTable"]
        /tr[@class="row1" or @class="row2"]
        /td[6][text()="{}"]/..
        /td[2]/text()
        """.format(symbol_ords(symbol)))[0]

def symbol_ords(symbol):
    """
    Convert utf8 string into string of decimal ordinal representations of each
    character separated by comma.

    :param symbol: string to convert
    :type symbol: `str`

    :returns: decimal ordinal representations of each input character
    :rtype: `str` (integers separated by commas)
    """
    return ', '.join(str(ord(x)) for x in symbol)

def xe_to_dict(root):
    """
    Convert the static page downloaded (downloaded from
    http://www.xe.com/symbols.php on 13th June 2017) into symbol to code table
    in form of Python `dict` for simplicity and performance.

    :param root: root node of html page
    :type root: `lxml.html.HtmlElement`

    :returns: dictionary that maps currency symbols to currency codes
    :rtype: `dict`<`str`: `str`>
    """
    rows = root.xpath("""
        .//table[@class="currencySymblTable"]
        /tr[@class="row1" or @class="row2"]""")

    def symbol(tr):
        bs = tr.xpath('td[6]/text()')[0].split(', ')
        return ''.join(chr(int(x)) for x in bs)

    def code(tr):
        return tr.xpath('td[2]/text()')[0]

    def keyval(tr):
        try:
            return symbol(tr), code(tr)
        except IndexError: # some data are missing in the table
            return None

    return {kv[0]: kv[1] for kv in map(keyval, rows) if kv}

def from_static(symbol):
    """
    Use static table (downloaded from http://www.xe.com/symbols.php on 13th June
    2017) to convert the symbol into currency code.

    :param symbol: symbol to convert
    :type symbol: `str`

    :returns: currency code
    :rtype: `str`
    """
    return static_dict[symbol]

static_dict = xe_to_dict(html.parse(STATIC_PATH))