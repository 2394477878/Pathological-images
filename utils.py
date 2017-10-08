#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: Justin

"""
   1. 最高分辨率图像使用scale = 20进行采集，这时每个Patch边长为256
   2. 全图使用scale = 2.5进行采集，对应的Patch的边长为32
"""
# googleNet
EXTRACT_SCALE = 20
PATCH_SIZE_HIGH = 256
PATCH_SIZE_LOW = 32

# lenet
# EXTRACT_SCALE = 10
# PATCH_SIZE_HIGH = 32
# PATCH_SIZE_LOW = 8


GLOBAL_SCALE = PATCH_SIZE_LOW / PATCH_SIZE_HIGH * EXTRACT_SCALE  # 2.5
AMPLIFICATION_SCALE = PATCH_SIZE_HIGH / PATCH_SIZE_LOW  # 8

PATCH_PATH_CANCER = "D:/Study/breast/Patches/cancer"
PATCH_PATH_NORMAL = "D:/Study/breast/Patches/normal"

# Cancer = 1
# Normal = 0
