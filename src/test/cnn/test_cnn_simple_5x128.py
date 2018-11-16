#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__author__ = 'Justin'
__mtime__ = '2018-11-10'

"""

import unittest
from core import *
from cnn import cnn_simple_5x128

JSON_PATH = "D:/CloudSpace/WorkSpace/PatholImage/config/justin2.json"
# JSON_PATH = "C:/RWork/WorkSpace/PatholImage/config/justin2.json"

class Test_cnn_simple_5x128(unittest.TestCase):

    def test_training(self):
        c = Params()
        c.load_config_file(JSON_PATH)

        cnn = cnn_simple_5x128(c, "simplenet128")
        cnn.train_model("CNN_R_500_128", batch_size = 100, augmentation = (True, False))

    def test_predict(self):
        c = Params()
        c.load_config_file("D:/CloudSpace/WorkSpace/PatholImage/config/justin.json")
        cnn = cnn_simple_5x128(c, "simplenet128")

        imgCone = ImageCone(c)

        # 读取数字全扫描切片图像
        tag = imgCone.open_slide("17004930 HE_2017-07-29 09_45_09.kfb",
                                 '17004930 HE_2017-07-29 09_45_09.kfb.Ano', "17004930")
        seeds = [(7600, 4160), (3440, 3840), (9888, 7968)] # C, C, S
        result = cnn.predict(imgCone, 5, 128, seeds)
        print(result)

        result = cnn.predict_on_batch(imgCone, 5, 128, seeds, 20)
        print(result)

    def test_predict_test_file(self):
        c = Params()
        c.load_config_file(JSON_PATH)
        cnn = cnn_simple_5x128(c, "simplenet128")

        # cnn.predict_test_file("simple5x128_R-0098-0.03-0.99.ckpt",
        #                       ["S500_128_False_cancer.txt", "S500_128_False_normal.txt"])

        # cnn.predict_test_file("simple5x128_R-0098-0.03-0.99.ckpt",
        #                       ["T_NC_500_128_test.txt"])

        cnn.predict_test_file("simple5x128-0100-0.12-0.97.ckpt",
                              ["T_NC_500_128_test.txt"])

        # cnn.predict_test_file("simple5x128-0100-0.12-0.97.ckpt",
        #                       ["S500_128_False_cancer.txt", "S500_128_False_normal.txt"])