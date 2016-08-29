#!/usr/bin/env python

"""
Script to generate persistent behaviors of poems.

This isn't needed to actually run the server --- it's an automatic
configuration script that's already been run (the results of which are
stored in ``poems.py``). If you'd like to generate a new set of persistent
behaviors for the poems, simply run this script.
"""

from pprint import pformat
from random import randint

from blur import rand

# import basic (manually entered) data on the poems
from __poems_basic_preconfig import poems

if __name__ == '__main__':
    for poem in poems:
        # Decide the likelihood that a poem will be markov-ed on view
        # Manually entered data had mutable chances of 0, 0.5, and 1
        # For 3 basic categories of preference
        # (All but poem eight have a chance to be mutable)
        if poem['mutable_chance'] == 0 and poem['name'] != 'eight':
            poem['mutable_chance'] = rand.weighted_rand(
                [(0, 100), (0.03, 10), (0.15, 0)]
            )
        elif poem['mutable_chance'] == 0.5:
            poem['mutable_chance'] = rand.weighted_rand(
                rand.normal_distribution(0.5, 0.8, 0, 1)
            )
        else:
            poem['mutable_chance'] = rand.weighted_rand(
                [(0.85, 0), (0.9, 10), (1, 100)]
            )
        poem['position_weight'] = rand.weighted_rand(
            rand.normal_distribution(poem['position_weight'], 3)
        )
        # Build distance weights for markov graph derivation
        keys = [rand.weighted_rand(
                    rand.normal_distribution(4, 30), True)
                for i in range(randint(10, 20))]
        distance_weights = dict(
            [(key,
              rand.weighted_rand(
                rand.normal_distribution(20 - abs(2 - key), 5, 0)
                )
              )
             for key in keys])
        # Force strong bias toward distance 1, meaning words will often
        # be followed by those that follow them in the source text
        distance_weights[1] = (max(distance_weights.values()) *
                               (len(distance_weights) * 0.75))
        poem['distance_weights'] = distance_weights
        # Build x_gap_frequency_weights - the probability curve used to
        # decide at render-time how frequently horizontal gaps will be
        # inserted between words
        poem['x_gap_freq_weights'] = rand.normal_distribution(-1, 0.23, 0, 1)

    # Output poem data to file using pformat (who needs JSON!)
    out_file = open('poems.py', 'w')
    out_file.write('poems = ' + pformat(poems))
