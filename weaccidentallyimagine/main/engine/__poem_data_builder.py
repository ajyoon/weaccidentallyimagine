#!/usr/bin/env python

from random import randint

from pprint import pformat

from blur import rand

from poems_original import poems

for poem in poems:
    if poem['mutable_chance'] == 0 and poem['name'] != 'eight':
        poem['mutable_chance'] = rand.weighted_rand(
            [(0, 100), (0.03, 10), (0.15, 0)]
        )
    elif poem['mutable_chance'] == 0.5:
        poem['mutable_chance'] = rand.weighted_rand(
            rand.normal_distribution(0.5, 0.8, 0, 1)
        )
    elif poem['mutable_chance'] == 1:
        poem['mutable_chance'] = rand.weighted_rand(
            [(0.85, 0), (0.9, 10), (1, 100)]
        )
    poem['position_weight'] = rand.weighted_rand(
        rand.normal_distribution(poem['position_weight'], 3)
    )
    # Build distance weights
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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
    # Force strong bias toward distance 1
    distance_weights[1] = (max(distance_weights.values()) *
                           (len(distance_weights) * 0.75))
    poem['distance_weights'] = distance_weights
    # Build x_gap_frequency_weights
    poem['x_gap_freq_weights'] = rand.normal_distribution(-1, 0.23, 0, 1)

out_file = open('poems.py', 'w')
out_file.write('poems = ' + pformat(poems))
