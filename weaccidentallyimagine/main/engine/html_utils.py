"""Utility functions for manipulating and generating HTML strings"""


def surround_with_tag(string, tag, *args):
    """
    Surround a string literal with an HTML tag with optional attributes.

    Args:
        string (str): The string to be enclosed in the tag
        tag (str): The HTML tag to use
        args: Any number of string literal HTML tag attributes,

    Example:
        >>> surround_with_tag('hello world', 'h1',
        ...                   'class="classvalue"', 'id="idvalue"')
        '<h1 class="classvalue" id="idvalue">hello world</h1>'
    """
    return '<{tag} {attributes}>{string}</{tag}>'.format(
        tag=tag,
        attributes=' '.join(args),
        string=string)


def horizontal_blank_space(width):
    """
    Return a string literal HTML empty span with `width` in em's.

    The HTML `class` attribute of this span will be
    `horizontal-blank-space`.

    Args:
        width (float): the width (length) of the space in em's.

    Returns: str
    """
    return surround_with_tag(
        '',
        'span',
        'class="horizontal-blank-space"',
        'style="width: {}em; display: inline-block;"'.format(width)
    )


def variable_length_dash(length):
    """
    Return a string literal HTML empty span with `length` in em's.

    The HTML `class` attribute of this span will be
    `variable-length-dash`.

    Args:
        length (float): The length of the dash in em's.

    Returns: str
    """
    return surround_with_tag(
        '',
        'span',
        'class="variable-length-dash"',
        'style="width: {}em;"'.format(length)
    )


def variable_height_break(height):
    """
    Return a string literal HTML empty span with `height` in em's.

    The HTML `class` attribute of this span will be
    `varable-height-break`.

    Args:
        height (float): The height of the break in em's.

    Returns: str
    """
    return surround_with_tag(
        '',
        'span',
        'class="variable-height-break"',
        'style="height: {}em;"'.format(height)
    )
