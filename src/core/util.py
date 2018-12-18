#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__author__ = 'Justin'
__mtime__ = '2018-06-02'

"""
import numpy as np
from skimage import color, morphology
from skimage.morphology import square
import os
import pandas as pd

def get_seeds(MaskLow, lowScale, highScale, patch_size_high, spacingHigh, margin = -8):
    '''
    得到Mask图像中为True位置在高分辨率下的坐标值
    :param MaskLow: 低分辨率Mask图像
    :param lowScale: 低分辨率值
    :param highScale: 种子点坐标所在的高分辨率值
    :param patch_size_high: 在高分辨率图块的大小
    :param spacingHigh: 种子点在高分辨率图像之间的间隔spacingHigh
    :param margin: 边界参数
    :return: 在高分辨率中的种子点坐标
    '''

    amp = highScale / lowScale
    patch_size = int(patch_size_high / amp)  # patch size low

    if margin < 0:
        # 灰度图像腐蚀，图像中物体会收缩/细化：https://wenku.baidu.com/view/c600c8d1360cba1aa811da73.html
        seed_img = morphology.binary_erosion(MaskLow, square(patch_size))
        seed_img = morphology.binary_erosion(seed_img, square(abs(margin)))  # 收缩边界
    elif margin > 0:
        seed_img = morphology.binary_dilation(MaskLow, square(patch_size))
        seed_img = morphology.binary_dilation(seed_img, square(margin))  # 扩展边界

    space_patch = spacingHigh / amp
    pos = seed_img.nonzero()
    y = (np.rint(pos[0] / space_patch + 0.5) * spacingHigh).astype(np.int32)  # row
    x = (np.rint(pos[1] / space_patch + 0.5) * spacingHigh).astype(np.int32)  # col

    resultHigh = set()
    for xx, yy in zip(x, y):
        resultHigh.add((xx, yy))

    return list(resultHigh)


def read_csv_file(root_path, csv_path):
    filenames_list = []
    labels_list = []

    f = open(csv_path, "r")
    lines = f.readlines()
    for line in lines:
        items = line.split(" ")

        tag = int(items[1])
        labels_list.append(tag)

        patch_file = "{}/{}".format(root_path, items[0])
        filenames_list.append(patch_file)
    return filenames_list, labels_list

def latest_checkpoint(search_dir):

    filename = []
    epoch = []
    loss = []
    accuracy = []

    for ckpt_name in os.listdir(search_dir):
        file_name = os.path.splitext(ckpt_name)[0]
        value = file_name.split("-")
        if len(value) == 4:
            filename.append(ckpt_name)
            epoch.append(int(value[1]))
            loss.append(float(value[2]))
            accuracy.append(float(value[3]))

    if len(filename) ==  0: return None

    data = {'filename':filename, 'epoch':epoch, 'loss':loss, 'accuracy':accuracy}
    df = pd.DataFrame(data, columns=['filename','epoch','loss','accuracy'])
    result = df.sort_values(['loss', 'accuracy', 'epoch'], ascending=[True, False, False])

    path = "{}/{}".format(search_dir, result.iloc[0,0])
    return path