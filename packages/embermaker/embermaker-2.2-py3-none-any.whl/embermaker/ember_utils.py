from lxml.html import fromstring
from markdown import markdown
import re


def html_md(text: str, keepbr=False):
    """
    Quick conversion from the limited html used in EDB to markdown; all 'unexpected' tags are ignored.
    """
    if not keepbr:
        text = text.replace('\n', ' ')
    if text.strip():
        return htmlelement_md(fromstring(text.replace('− ', '- ')))
    else:
        return ''


def htmlelement_md(el, allowpar=False):
    """
    Convert a selection of HTML elements to markdown, supporting lists,  <em>, <i>, and subscripts.
    (subscripts are supported through a non-standard / TeX-like notation: CO_2)
    """
    text = ""
    if el.tag == 'br':
        text += "\n\n"
    if el.tag == 'ul':
        text += "\n"
    if el.tag == 'li':
        text = '\n- ' + text
    if el.text is not None:
        text += el.text.replace('\xa0', ' ')  # Had issues with UTF8 NBSP keeping html in md is not a good option either
        # Deal with 'old' way of marking text in EDB as well as potential new one:
        if el.tag == 'strong':
            text = ' **' + text.strip() + '** '
        elif el.tag == 'i' or el.tag == 'em':  # Added em because this is what *...* is actually converted to.
            text = '*' + text.strip() + '*'
        elif el.tag == 'sub':
            text = '_' + text.strip()
        elif el.tag == 'sup':
            text = '^' + text.strip()
        elif el.tag == 'a':
            text = f"[{text}]({el.attrib['href']})"
    if el.tag in ['p', 'div'] and allowpar:
        text = '\n\n' + text
    for d in el.iterchildren():
        if d is not None:
            # markdown should not contain empty paragraphs nor pargraph within bullet lists:
            text += htmlelement_md(d, allowpar=text.strip() and el.tag != 'li')
    if el.tail:
        text += el.tail.replace('\xa0', ' ')
    # print(el.tag, 'now at: ', text)
    return text


def md_html(text, allowtitles=False):
    """
    Standard markdown conversion to html + support for the old html 'marked' style and subscripts.
    """
    if not allowtitles:
        # Prevent insertion of md titles & fix any remaining UTF8 nbsp => html
        filtext = text.replace('#', '')
    else:
        filtext = text
    filtext.replace('\xa0', '&nbsp;')
    filtext = md_subsup(filtext)
    filtext = markdown(filtext)
    filtext = re.sub(r'<a(.*?)>', r'<a\1 target="_blank">', filtext)
    return filtext


def md_subsup(filtext):
    """
    Converts subscripts (_) and supscripts (^) to html tags
    """
    filtext = re.sub(r'(\(http.*?\))|_(.)', r'\1<sub>\2</sub>', filtext).replace('<sub></sub>', '')
    # To interpret _ as subscript (e.g. CO_2), but ignore the subscripts which are in urls.
    # Each match of the regex is either an url or a subscript, but I could not avoid the matches for urls.
    return re.sub(r'\^(.)', r'<sup>\1</sup>', filtext)  # To interpret ^ as superscript (e.g. m^2).


def preproc(text):
    """
    Pre-process old text from the db to 'format' list as appropriate for Markdown
    :param text:
    :return:
    """
    text = text.replace('–', '- ').replace('<br>', '\n')
    tlist = text.split('\n')
    text = ""
    pfr = ""
    for fr in tlist:
        sfr = fr.strip()
        if sfr and sfr[0] == '-' and pfr and pfr[0] != '-':
            text += '\n'
        text += fr + '\n'
        pfr = sfr
    return text
