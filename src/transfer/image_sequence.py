#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__author__ = 'Justin'
__mtime__ = '2018-10-30'

"""

from tensorflow.keras.utils import Sequence, to_categorical
from skimage.io import imread
from skimage.transform import resize
import numpy as np
import math


# Here, `x_set` is list of path to the images
# and `y_set` are the associated classes.

class ImageSequence(Sequence):

    def __init__(self, x_set, y_set, batch_size):
        self.x, self.y = x_set, y_set
        self.batch_size = batch_size

    def __len__(self):
        return math.ceil(len(self.x) / self.batch_size)

    def __getitem__(self, idx):
        batch_x = self.x[idx * self.batch_size:(idx + 1) *
                                               self.batch_size]
        batch_y = self.y[idx * self.batch_size:(idx + 1) *
                                               self.batch_size]

        return np.array([
            # resize(imread(file_name),(299,299))
            imread(file_name)
            for file_name in batch_x]), to_categorical(batch_y, 2)