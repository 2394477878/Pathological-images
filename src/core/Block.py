#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__author__ = 'Justin'
__mtime__ = '2018-10-13'

"""

import numpy as np
from PIL import Image
import io

# Block坐标中心化，不同是以前的左上角，以方便在多分辨率中进行对应
class Block(object):
    # x is col, y is row
    def __init__(self, snumber="", x=0, y=0, scale=0, opcode=0, w=0, h=0):
        '''
        初始化图块信息
        :param snumber: 切片的编号
        :param x: 图块中心点x
        :param y: 图块中心点y
        :param scale: 所在倍镜
        :param opcode: 操作码
        :param w: 图块宽度
        :param h: 图块高度
        '''
        self.slice_number = snumber
        self.x = x
        self.y = y
        self.scale = scale
        self.opcode = opcode
        self.w = w
        self.w = h
        # self.img_file = None
        self.img = None

    def decoding(self, filename, w, h):
        '''
        根据文件名的编码，解析出图块的信息
        :param filename:  文件名
        :param w: 图块宽
        :param h: 高
        :return:
        '''
        left = filename.rfind("/")
        right = filename.index(".")
        file_code = filename[left + 1 : right]
        code = file_code.split("_")

        if len(code) > 5:
            pos = file_code.find(code[-5])
            self.slice_number = file_code[:pos + len(code[-5])]
        else:
            self.slice_number = code[0]
        self.x = int(code[-4])
        self.y = int(code[-3])
        self.scale = float(code[-2])/100
        self.opcode = int(code[-1])
        self.w = w
        self.h = h

        return

    def encoding(self):
        '''
        根据 模板生成图块所对应编码
        :return:
        '''
        intScale = np.rint(self.scale * 100).astype(np.int)
        return "{0}_{1:0>6}_{2:0>6}_{3:0>4}_{4:0>1}".format(self.slice_number,
                                                            self.x, self.y, intScale, self.opcode)

    # def set_img_file(self, image_file):
    #     '''
    #     设定图块的文件流
    #     :param image_file 文件流:
    #     :return:
    #     '''
    #     self.img_file = image_file

    def set_img(self, img):
        '''
        设定图块的图像
        :param img: 图像矩阵
        :return:
        '''
        self.img = img[:,:,:3] #如果是RGBA图像，则取前三个通道

    def get_img(self):
        '''
        提取图块图像
        :return: 图块图像
        '''
        # if self.img == None:
        #     # 从文件流中得到图像矩阵
        #     self.img = np.array(Image.open(io.BytesIO(self.img_file)))

        return self.img

    def save_img(self, path):
        '''
        图块存盘
        :param path: 存盘的路径
        :return:
        '''
        filename = '/{}.jpg'.format(self.encoding())
        save_image = Image.fromarray(np.uint8(self.img))
        save_image.save(path + filename)
        # if self.img_file == None:
        #     self.img.save(path + filename)
        # else:
        #    self.img_file.tofile(path + filename)
        return

    def load_img(self, filename):
        '''
        从jpg文件加载图块
        :param filename: 图块jpg文件名
        :return:
        '''
        self.img = Image.open(filename)
        (w, h) = self.img.size
        self.decoding(filename, w, h)
        return