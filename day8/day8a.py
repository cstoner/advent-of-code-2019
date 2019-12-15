#!/usr/bin/env python3
import collections
from typing import List


class SpaceFormattedImage:
    def __init__(self, height: int, width: int, image: List[int]):
        self.pixel_per_layer = (height * width)

        assert (len(image) % self.pixel_per_layer == 0)
        self.num_layers = len(image) // self.pixel_per_layer

        self.height = height
        self.width = width
        self.image = image

    def get_layer(self, i: int):
        assert (i < self.num_layers)

        start_idx = i * self.pixel_per_layer
        end_idx = start_idx + self.pixel_per_layer

        layer = self.image[start_idx:end_idx]
        if len(layer) != self.pixel_per_layer:
            print(f"Incorrect number of pixels returned for layer {i}: {len(layer)}")
            assert(False)
        return layer

    def layer_with_fewest_zeros(self) -> int:
        fewest_zeros = len(self.image)+1
        layers = []

        for i in range(self.num_layers):
            counter = collections.Counter(self.get_layer(i))
            zero_count = counter[0]
            if zero_count < fewest_zeros:
                fewest_zeros = zero_count
                layers = [i]
            elif zero_count == fewest_zeros:
                layers.append(i)

        assert(len(layers) == 1)
        # print(f"Layer with fewest zeros ({fewest_zeros}): {layers[0]}")
        return layers[0]

    def ones_times_twos(self, i):
        counter = collections.Counter(self.get_layer(i))
        return counter[1] * counter[2]


test_image = SpaceFormattedImage(2, 3, [1, 2, 3, 4, 5, 6, 7, 8, 9, 0, 1, 2])
assert(1 == test_image.ones_times_twos(
    test_image.layer_with_fewest_zeros()
))


with open('input.txt') as INPUT:
    input = [int(x) for x in INPUT.read().strip()]

day8_image = SpaceFormattedImage(6, 25, input)
answer = day8_image.ones_times_twos(day8_image.layer_with_fewest_zeros())
print(f"count(twos) x count(ones) for layer with fewest zeros: {answer}")
