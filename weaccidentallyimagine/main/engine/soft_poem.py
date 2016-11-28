import os

from blur import rand
from blur import soft
from blur.markov.graph import Graph

from .html_utils import (surround_with_tag, horizontal_blank_space,
                         variable_length_dash, variable_height_break)

# Uncomment to fix the seed for reproducible rendering for debugging
# import random
# random.seed(12345)

PUNCTUATIONS = [',', '.', ':', '!', '?', '"', ';']

SOURCE_DIR = os.path.join(os.path.dirname(__file__), 'texts')
LINE_LENGTH = 20

_default_mutable_chance       = 0.5
_default_distance_weights     = {-5: 30, -2: 30,
                                 1 : 1000, 2: 40, 3: 20, 4: 10, 5: 10,
                                 6 : 15, 7: 10, 8: 10, 9: 8, 10: 5,
                                 11: 2, 12: 2, 13: 5, 14: 5, 15: 50}
_default_position_weight      = (0, 0)
_default_word_count_weights   = [(10, 0), (60, 4),
                                 (100, 10), (130, 3), (500, 0)]
_default_gap_before_weights   = [(1, 3), (3, 5), (6, 10), (30, 2)]
_default_left_pad_weights     = [(0, 10), (20, 2), (40, 0)]
_default_x_gap_length_weights = [(0, 100), (5, 20), (9, 6), (30, 0)]
_default_y_gap_height_weights = [(0, 0), (1, 1), (2, 10), (4, 1), (10, 0)]
_default_dash_length_weights  = [(0.5, 25), (2, 1), (10, 0)]
_default_x_gap_freq_weights   = [(0.05, 1), (0.12, 5)]


class SoftPoem(soft.SoftObject):
    """A poem with stochastic contents."""

    def __init__(self,
                 filename,
                 immutable_id,
                 title='',
                 mutable_chance=None,
                 position_weight=None,
                 distance_weights=None,
                 word_count_weights=None,
                 gap_before_weights=None,
                 left_pad_weights=None,
                 x_gap_freq_weights=None,
                 x_gap_length_weights=None,
                 y_gap_height_weights=None,
                 dash_length_weights=None,
                 ):
        """
        Args:
            filename (str): Name of text file containing the poem source
                located in `SOURCE_DIR`
            title (str): Title of the poem
            immutable_id (int): The immutable unique ID of this poem.
                Unlike `title`, this should not be subject to change by
                random processes.
            mutable_chance (float): 0-1 probability to be mutable
            distance_weights (dict): Dict of distance weights to be
                used in rand.from_file()
            position_weight (list[tuple]): Weight for position in the
                book order. Higher values relative to the values in the other
                poems indicates a stronger likelihood to appear near the
                beginning
            word_count_weights (list[tuple]): List of weight tuples for
                how many words will appear in the poem if the poem is mutable
            gap_before_weights (list[tuple]): List of weight tuples for
                how much space should appear before the poem, in em's.
            left_pad_weights (list[tuple]): List of weight tuples for
                how far the poem should be padded on the left,
                in device-width %.
            x_gap_freq_weights (list[tuple]): List of weight tuples for how
                frequently x-axis gaps should be inserted between words in
                the rendered poem. On initialization, this value is used
                to calculate `self.x_gap_freq`, which is the 0-1 probability
                for an x-axis gap to be inserted between any two given words.
            x_gap_length_weights (list[tuple): List of weight tuples for the
                length of inserted x-axis gaps, in em's.
            y_gap_height_weights (list[tuple): List of weight tuples for how
                tall inserted y-axis gaps should be, in em's.
            dash_length_weights (list[tuple]): List of weight tuples for
                the length of dashes triggered by `---` marks in the
                source text.
        """
        self.immutable_id = immutable_id
        self.title = title
        self.filepath = os.path.join(SOURCE_DIR, filename)
        self.mutable_chance       = (mutable_chance
                                     if mutable_chance
                                     else _default_mutable_chance)
        self.distance_weights     = (distance_weights
                                     if distance_weights
                                     else _default_distance_weights)
        self.position_weight      = (position_weight
                                     if position_weight
                                     else _default_position_weight)
        self.word_count_weights   = (word_count_weights
                                     if word_count_weights
                                     else _default_word_count_weights)
        self.x_gap_length_weights = (x_gap_length_weights
                                     if x_gap_length_weights
                                     else _default_x_gap_length_weights)
        self.y_gap_height_weights = (y_gap_height_weights
                                     if y_gap_height_weights
                                     else _default_y_gap_height_weights)
        self.dash_length_weights  = (dash_length_weights
                                     if dash_length_weights
                                     else _default_dash_length_weights)
        # Some args are used to calculate attributes on init
        self.gap_before = rand.weighted_rand(
                gap_before_weights if gap_before_weights
                else _default_gap_before_weights)
        self.left_pad = rand.weighted_rand(
                left_pad_weights if left_pad_weights
                else _default_left_pad_weights)
        self.x_gap_freq = rand.weighted_rand(
                x_gap_freq_weights if x_gap_freq_weights
                else _default_x_gap_freq_weights)

    def render_markups(self, word_list):
        """
        Render a list of words and markups to html with automatic line breaks.

        This method performs several processing steps preparing the poem text
        for HTML delivery. It:
            * Converts `---` to stochastic length dashes in the form of empty
              `<span class="variable-length-dash"></span>` tags
            * Converts `|||` to stochastic height line breaks in the form of
              empty `<span class="variable-height-break"></span>` tags
            * Spontaneously inserts horizontal blank space between words in the
              form of empty `<span class="horizontal-blank-space"></span>` tags
            * Calculates the position of line breaks and renders them as divs
              in the form `<div class="poem-line"> ... </div>`

        Line breaks are triggered after every word which exceeds
        `LINE_LENGTH`. This character limit ignores HTML tags,
        allowing lines containing spans (variable-length-dash or
        horizontal-blank-space) to intentionally visually exceed the apparent
        right edge of the poem.

        Args:
            word_list (list[str]): The list of words (as well as punctuation
                marks and markups) to render.

        Returns:
            str: The contents of `word_list` rendered as HTML
        """
        working_text = word_list[:]  # Copy of word_list to avoid side-effects
        lines = []                   # List of lines in the generated poem
        current_line = []            # List of words in the current line
        visible_char_count = 0       # Number of visible chars in current line

        for word in working_text:
            if word == '---':
                # Render triple dashes to variable length visible dashes
                # (in the form of inline-block spans)
                dash_length = rand.weighted_rand(self.dash_length_weights)
                word = variable_length_dash(dash_length)
            elif word == '|||':
                # Render triple pipes as variable height breaks
                # (in the form of fixed-height spans)
                y_gap = rand.weighted_rand(
                        self.y_gap_height_weights)
                word = variable_height_break(y_gap)
            else:
                # Otherwise, the word will be rendered literally as visible
                # text, so count it toward the visible character count used
                # in placing line breaks
                visible_char_count += len(word)

            # Roll to insert x-axis gaps
            if rand.prob_bool(self.x_gap_freq):
                x_gap = rand.weighted_rand(self.x_gap_length_weights)
                # Sometimes place space before word, sometimes after (50/50)
                word = horizontal_blank_space(x_gap) + word
            # Break lines when LINE_LENGTH is exceeded
            if visible_char_count > LINE_LENGTH:
                visible_char_count = 0
                lines.append(''.join(current_line))
                current_line = []
            # Handle spaces appropriately for punctuation marks
            if word in PUNCTUATIONS:
                current_line.append(word)
            else:
                current_line.append(' ' + word)
        # Attach final line
        if current_line:
            lines.append(''.join(current_line))

        return (''.join((surround_with_tag(line, 'div', 'class="poem-line"')
                         for line in lines)))

    def get(self):
        """
        Render the poem as an HTML string.

        Returns:
            str: the body of the poem in HTML
        """
        if rand.prob_bool(self.mutable_chance):
            # Render text from a markov graph derived from the source text
            word_list = []
            word_count = rand.weighted_rand(
                self.word_count_weights, round_result=True)
            word_graph = Graph.from_file(self.filepath, self.distance_weights)
            for i in range(word_count):
                word = word_graph.pick().get_value()
                word_list.append(word)
        else:
            # Otherwise, copy source contents literally
            source_file = open(self.filepath, 'r')
            word_list = source_file.read().split()
        # Combine words, process markups, and return HTML
        return self.render_markups(word_list)
