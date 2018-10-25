#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__author__ = 'Justin'
__mtime__ = '2018-05-23'

"""

import unittest
from core import *
from preparation import *
import matplotlib.pyplot as plt


class TestPatchSampler(unittest.TestCase):

    def test_patch_20x_256(self):
        c = Params()
        c.load_config_file("D:/CloudSpace/WorkSpace/PatholImage/config/justin.json")
        imgCone = ImageCone(c)

        # 读取数字全扫描切片图像
        tag = imgCone.open_slide("17004930 HE_2017-07-29 09_45_09.kfb",
                                 '17004930 HE_2017-07-29 09_45_09.kfb.Ano', "17004930")
        self.assertTrue(tag)

        if tag:
            patch_size = 256
            edge_width = 64
            extract_scale = 20
            # patch_spacing = 128
            low_scale = c.GLOBAL_SCALE

            C_mask, S_mask, E_mask, L_mask = imgCone.create_mask_image(low_scale, edge_width)
            mask1 = imgCone.get_effective_zone(low_scale)
            S_mask = S_mask & mask1

            ps = PatchSampler(c)

            c_seeds = ps.generate_seeds4_high(C_mask, extract_scale, patch_size, patch_spacing=64)
            s_seeds = ps.generate_seeds4_high(S_mask, extract_scale, patch_size, patch_spacing=96)
            e_seeds = ps.generate_seeds4_high(E_mask, extract_scale, patch_size, patch_spacing=64)
            l_seeds = ps.generate_seeds4_high(L_mask, extract_scale, patch_size, patch_spacing=16)

            print("c_seeds = ",len(c_seeds),"s_seeds = ", len(s_seeds),"e_seeds = ", len(e_seeds), "l_seeds =", len(l_seeds))

            ps.extract_patches(imgCone, extract_scale, patch_size, c_seeds, seeds_name="cancer")
            ps.extract_patches(imgCone, extract_scale, patch_size, s_seeds, seeds_name="stroma")
            ps.extract_patches(imgCone, extract_scale, patch_size, e_seeds, seeds_name="edge")
            ps.extract_patches(imgCone, extract_scale, patch_size, l_seeds, seeds_name="lymph")

    def test_patch_5x_64(self):
        c = Params()
        c.load_config_file("D:/CloudSpace/WorkSpace/PatholImage/config/justin.json")
        imgCone = ImageCone(c)

        # 读取数字全扫描切片图像
        tag = imgCone.open_slide("17004930 HE_2017-07-29 09_45_09.kfb",
                                 '17004930 HE_2017-07-29 09_45_09.kfb.Ano', "17004930")
        self.assertTrue(tag)

        if tag:
            patch_size = 64
            edge_width = 64
            extract_scale = 5
            # patch_spacing = 128
            low_scale = c.GLOBAL_SCALE

            C_mask, S_mask, E_mask, L_mask = imgCone.create_mask_image(low_scale, edge_width)
            mask1 = imgCone.get_effective_zone(low_scale)
            S_mask = S_mask & mask1

            ps = PatchSampler(c)

            c_seeds = ps.generate_seeds4_high(C_mask, extract_scale, patch_size, patch_spacing=64)
            s_seeds = ps.generate_seeds4_high(S_mask, extract_scale, patch_size, patch_spacing=96)
            e_seeds = ps.generate_seeds4_high(E_mask, extract_scale, patch_size, patch_spacing=64)
            l_seeds = ps.generate_seeds4_high(L_mask, extract_scale, patch_size, patch_spacing=64)

            print("c_seeds = ",len(c_seeds),"n_seeds = ", len(s_seeds),"e_seeds = ", len(e_seeds), "l_seeds =", len(l_seeds))

            ps.extract_patches(imgCone, extract_scale, patch_size, c_seeds, seeds_name="cancer")
            ps.extract_patches(imgCone, extract_scale, patch_size, s_seeds, seeds_name="stroma")
            ps.extract_patches(imgCone, extract_scale, patch_size, e_seeds, seeds_name="edge")
            ps.extract_patches(imgCone, extract_scale, patch_size, l_seeds, seeds_name="lymph")

    def test_patch_5x_128(self):
        c = Params()
        c.load_config_file("D:/CloudSpace/WorkSpace/PatholImage/config/justin.json")
        imgCone = ImageCone(c)

        # 读取数字全扫描切片图像
        tag = imgCone.open_slide("17004930 HE_2017-07-29 09_45_09.kfb",
                                 '17004930 HE_2017-07-29 09_45_09.kfb.Ano', "17004930")
        self.assertTrue(tag)

        if tag:
            patch_size = 128
            edge_width = 64
            extract_scale = 5
            # patch_spacing = 128
            low_scale = c.GLOBAL_SCALE

            C_mask, S_mask, E_mask, L_mask = imgCone.create_mask_image(low_scale, edge_width)
            mask1 = imgCone.get_effective_zone(low_scale)
            S_mask = S_mask & mask1

            ps = PatchSampler(c)

            c_seeds = ps.generate_seeds4_high(C_mask, extract_scale, patch_size, patch_spacing=80)
            s_seeds = ps.generate_seeds4_high(S_mask, extract_scale, patch_size, patch_spacing=96)
            e_seeds = ps.generate_seeds4_high(E_mask, extract_scale, patch_size, patch_spacing=64)
            l_seeds = ps.generate_seeds4_high(L_mask, extract_scale, patch_size, patch_spacing=16)

            print("c_seeds = ",len(c_seeds),"s_seeds = ", len(s_seeds),"e_seeds = ", len(e_seeds), "l_seeds =", len(l_seeds))

            ps.extract_patches(imgCone, extract_scale, patch_size, c_seeds, seeds_name="cancer")
            ps.extract_patches(imgCone, extract_scale, patch_size, s_seeds, seeds_name="stroma")
            ps.extract_patches(imgCone, extract_scale, patch_size, e_seeds, seeds_name="edge")
            ps.extract_patches(imgCone, extract_scale, patch_size, l_seeds, seeds_name="lymph")