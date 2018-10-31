#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__author__ = 'Justin'
__mtime__ = '2018-05-23'

"""

import unittest
from core import *
from preparation import *

class TestPatchPack(unittest.TestCase):

    def test_pack_refine_sample_tags_SC(self):
        c = Params()
        c.load_config_file("D:/CloudSpace/WorkSpace/PatholImage/config/justin.json")

        pack = PatchPack(c)
        pack.refine_sample_tags_SVM({"S500_128_cancer":1,"S500_128_stroma":0}, "R_SC_5x128")


    def test_extract_refine_sample_SC(self):
        c = Params()
        c.load_config_file("D:/CloudSpace/WorkSpace/PatholImage/config/justin.json")

        pack = PatchPack(c)
        dir_map = {"S500_128_cancer":1,"S500_128_stroma":0}
        pack.extract_refine_sample_SC(5, dir_map, "R_SC_5x128", 128)

        # dir_map = {"S500_128_edge": 1, "S500_128_lymph": 0}
        # pack.extract_refine_sample_LE(5, dir_map,  "R_SC_5x128", 128)

    def test_packing_refined_samples(self):
        c = Params()
        c.load_config_file("D:/CloudSpace/WorkSpace/PatholImage/config/justin.json")

        pack = PatchPack(c)
        pack.packing_refined_samples(5, 128)

    def test_pack_samples_256(self):
        c = Params()
        c.load_config_file("D:/CloudSpace/WorkSpace/PatholImage/config/justin.json")

        pack = PatchPack(c)
        data_tag = pack.initialize_sample_tags({"S2000_256_cancer":1,"S2000_256_stroma":0})
        # pack.create_data_txt(data_tag, "SC_20x256")
        pack.create_train_test_data(data_tag, 0.8, 0.2, "T_SC_2000_256")
