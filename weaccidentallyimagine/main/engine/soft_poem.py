import os

from blur import rand
from blur import soft
from blur.markov.graph import Graph

from . import html_utils

# Uncomment to fix the seed for reproducible rendering for debugging
# import random
# random.seed(12345)


class SoftPoem(soft.SoftObject):
    """A poem with stochastic contents."""

    source_dir = os.path.join(os.path.dirname(__file__), 'texts')
    cutoff_char_length = 20
    _default_distance_weights = {-5: 30, -2: 30,
                                 1 : 1000, 2: 40, 3: 20, 4: 10, 5: 10,
                                 6 : 15, 7: 10, 8: 10, 9: 8, 10: 5,
                                 11: 2, 12: 2, 13: 5, 14: 5, 15: 50}
    _default_position_weight = (0, 0)
    _default_word_count_weight = [(10, 0), (60, 4),
                                  (100, 10), (130, 3), (500, 0)]
    _default_gap_before_weights = [(1, 3), (3, 5), (6, 10), (30, 2)]
    _default_left_pad_weights = [(0, 10), (20, 2), (40, 0)]
    _default_x_gap_weights = [(0, 100), (5, 20), (9, 6), (30, 0)]
    _default_y_gap_weights = [(0, 0), (1, 1), (2, 10), (4, 1), (10, 0)]
    _default_dash_length_weights = [(0.5, 25), (2, 1), (10, 0)]
    _default_x_gap_freq_weights = [(0.05, 1), (0.12, 5)]
    PUNCTUATIONS = [',', '.', ':', '!', '?', '"', ';']

    def __init__(self,
                 filename,
                 name=None,
                 immutable_id=None,
                 mutable_chance=None,
                 position_weight=None,
                 distance_weights=None,
                 word_count_weights=None,
                 gap_before_weights=None,
                 left_pad_weights=None,
                 x_gap_freq_weights=None,
                 x_gap_weights=None,
                 y_gap_weights=None,
                 dash_length_weights=None,
                 ):
        """
        Args:
            filename (str): Name of text file containing the poem source
                located in ``SoftPoem.source_dir``
            name (str): Name of the poem
            immutable_id (int): The immutable unique ID of this poem.
                Unlike ``name``, this should not be subject to change by
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
                to calculate ``self.x_gap_freq``, which is the 0-1 probability
                for an x-axis gap to be inserted between any two given words.
            x_gap_weights (list[tuple): List of weight tuples for the length
                of inserted x-axis gaps, in em's.
            y_gap_weights (list[tuple): List of weight tuples for how tall
                inserted y-axis gaps should be, in em's.
            dash_length_weights (list[tuple]): List of weight tuples for
                the length of dashes triggered by ``---`` marks in the
                source text.
        """
        self.immutable_id = immutable_id
        self.name = name if name else str(self.immutable_id)
        self.filepath = os.path.join(SoftPoem.source_dir, filename)
        self.mutable_chance = mutable_chance
        self.distance_weights = (distance_weights if distance_weights
                                 else self._default_distance_weights)
        self.position_weight = (position_weight if position_weight
                                else self._default_position_weight)
        self.word_count_weights = (word_count_weights if word_count_weights
                                   else self._default_word_count_weight)
        self.x_gap_weights = (x_gap_weights if x_gap_weights
                              else self._default_x_gap_weights)
        self.y_gap_weights = (y_gap_weights if y_gap_weights
                              else self._default_y_gap_weights)
        self.dash_length_weights = (dash_length_weights if dash_length_weights
                                    else self._default_dash_length_weights)
        # Some args are used to calculate attributes on init
        self.gap_before = rand.weighted_rand(
                gap_before_weights if gap_before_weights
                else self._default_gap_before_weights)
        self.left_pad = rand.weighted_rand(
                left_pad_weights if left_pad_weights
                else self._default_left_pad_weights)
        self.x_gap_freq = rand.weighted_rand(
                x_gap_freq_weights if x_gap_freq_weights
                else self._default_x_gap_freq_weights)

    def process_markups_and_line_breaks_as_html(self, word_list):
        """
        Render a list of words and markups to html with auto line breaks.

        Convert ``---`` to stochastic length dashes in the form of empty
        ``<span class="variable-length-dash"></span>`` tags.

        Convert ``|||`` to stochastic height line breaks in the form of empty
        ``<span class="variable-height-break"></span>`` tags.

        Spontaneously insert horizontal blank space between words in the form
        of empty ``<span class="horizontal-blank-space"></span>`` tags.

        Create a ``<div class="poem-line"> ... </div>`` around every line.

        Line breaks are triggered after every word which exceeds
        ``cutoff_char_length``. This character limit ignores HTML tags,
        allowing lines containing spans (variable-length-dash or
        horizontal-blank-space) to intentionally visually exceed the apparent
        right edge of the poem.

        Args:
            word_list (list[str]): The list of words (as well as punctuation
                marks and markups) to render.

        Returns:
            str: The contents of ``word_list`` rendered as HTML
        """
        # Copy word_list to avoid side-effects
        working_text = word_list[:]
        visible_char_count = 0
        lines = []
        current_line = []
        for word in working_text:
            if word == '---':
                dash_length = rand.weighted_rand(self.dash_length_weights)
                word = html_utils.variable_length_dash(dash_length)
            elif word == '|||':
                y_gap = rand.weighted_rand(
                        self.y_gap_weights)
                word = html_utils.variable_height_break(y_gap)
            else:
                visible_char_count += len(word)
            # Roll to insert x-axis gaps
            if rand.prob_bool(self.x_gap_freq):
                x_gap = rand.weighted_rand(self.x_gap_weights)
                # Sometimes place space before word, sometimes after (50/50)
                word = html_utils.horizontal_blank_space(x_gap) + word
            # Break lines when cutoff_char_length is exceeded
            if visible_char_count > self.cutoff_char_length:
                visible_char_count = 0
                lines.append(''.join(current_line))
                current_line = []
            # Handle spaces appropriately for punctuation marks
            if word in self.PUNCTUATIONS:
                current_line.append(word)
            else:
                current_line.append(' ' + word)
        # Attach final line
        if current_line:
            lines.append(''.join(current_line))

        return (''.join((html_utils.surround_with_tag(
                            line,
                            'div',
                            'class="poem-line"')
                         for line in lines)))

    def get(self):
        """
        Render the poem as an HTML string.

        Returns:
            str: the body of the poem in HTML
        """
        if rand.prob_bool(self.mutable_chance):
            word_list = []
            word_count = rand.weighted_rand(
                self.word_count_weights, round_result=True)

            word_graph = Graph.from_file(self.filepath, self.distance_weights)
            for i in range(word_count):
                word = word_graph.pick().get_value()
                word_list.append(word)
        else:
            source_file = open(self.filepath, 'r')
            word_list = source_file.read().split()

        return self.process_markups_and_line_breaks_as_html(word_list)
