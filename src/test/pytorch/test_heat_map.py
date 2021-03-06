#!/usr/bin/env python
# encoding: utf-8
'''
@author: Justin Ruan
@license: 
@contact: ruanjun@whut.edu.cn
@time: 2020-01-10
@desc:
'''

import warnings

with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=DeprecationWarning)

import os
import unittest
from core import *
from pytorch.heat_map import HeatMapBuilder


# JSON_PATH = "D:/CloudSpace/WorkSpace/PatholImage/config/justin2.json"
# JSON_PATH = "H:/Justin/PatholImage/config/justin3.json"
JSON_PATH = "E:/Justin/WorkSpace/PatholImage/config/justin_m.json"

class TestHeatMapBuilder(unittest.TestCase):

    def test_create_train_data(self):
        c = Params()
        c.load_config_file(JSON_PATH)

        hmb = HeatMapBuilder(c, model_name="Slide_FCN", patch_size=256)
        select = ["Tumor_{:0>3d}".format(i) for i in range(1, 112)]
        hmb.create_train_data(chosen=select)

    def test_train(self):

        c = Params()
        c.load_config_file(JSON_PATH)

        hmb = HeatMapBuilder(c, model_name="Slide_FCN", patch_size=256)
        hmb.train(batch_size=60, learning_rate=1e-3, begin_epoch=0, epochs=10)

    def test_evluate(self):
        c = Params()
        c.load_config_file(JSON_PATH)

        hmb = HeatMapBuilder(c, model_name="Slide_FCN", patch_size=256)
        # select = ["Tumor_{:0>3d}".format(i) for i in range(1, 112)]
        select = ["Tumor_{:0>3d}".format(i) for i in range(1, 10)]
        hmb.predict(chosen=select)