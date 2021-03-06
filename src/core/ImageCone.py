#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__author__ = 'Justin'
__mtime__ = '2018-10-13'

"""
from core import Block
from core.KFB_slide import KFB_Slide
import numpy as np
from skimage import draw
from skimage import color, morphology
from skimage.morphology import square
import io
from core.util import get_seeds, transform_coordinate

class ImageCone(object):

    def __init__(self, params, slide):
        # self._slide = KFB_Slide(params.KFB_SDK_PATH)
        self._slide = slide
        self._params = params

    def open_slide(self, filename, ano_filename, id_string):
        '''
        打开切片文件
        :param filename: 切片文件名
        :param ano_filename: 切片所对应的标注文件名
        :param id_string: 切片编号
        :return: 是否成功打开切片
        '''
        self.slice_id = id_string
        root_path = self._params.SLICES_ROOT_PATH + "/"
        tag = self._slide.open_slide(root_path + filename, id_string)

        if tag:
            if not ano_filename is None:
                self._slide.read_annotation(root_path + ano_filename)
                self.ano_filename = ano_filename
            else:
                self.ano_filename = None
            return True

        return False

    def get_fullimage_byScale(self, scale):
        '''
        得到指定倍镜下的全图
        :param scale: 倍镜数
        :return:
        '''
        return self._slide.get_thumbnail(scale)

    def get_image_width_height_byScale(self, scale):
        '''
        得到指定倍镜下，全图的大小
        :param scale: 倍镜数
        :return: 全图的宽，高
        '''
        if scale > 3:
            print("\a", "The size of image is too large")
            return

        w, h = self._slide.get_image_width_height_byScale(scale)
        return w, h

    def get_image_block(self, fScale, c_x, c_y, nWidth, nHeight):
        '''
        在指定坐标和倍镜下，提取切片的图块
        :param fScale: 倍镜数
        :param c_x: 中心x
        :param c_y: 中心y
        :param nWidth: 图块的宽
        :param nHeight: 图块的高
        :return: 返回一个图块对象
        '''
        data = self._slide.get_image_block(fScale, c_x, c_y, nWidth, nHeight)

        newBlock = Block(self.slice_id, c_x, c_y, fScale, 0, nWidth, nHeight)
        newBlock.set_img(data)
        return newBlock

    def get_image_blocks_itor(self, fScale, seeds, nWidth, nHeight, batch_size):
        '''
        获得以种子点为图块的迭代器
        :param fScale: 倍镜数
        :param seeds: 中心点集合
        :param nWidth: 图块的宽
        :param nHeight: 图块的高
        :param batch_size: 每批的数量
        :return: 返回图块集合的迭代器
        '''
        n = 0
        images = []
        for x, y in seeds:
            block = self.get_image_block(fScale, x, y, nWidth, nHeight)
            images.append(block.get_img())
            n = n + 1
            if n >= batch_size:
                yield images

                images = []
                n = 0

        if n > 0:
            return images

    def create_mask_image(self, scale, width):
        '''
        在设定的倍镜下，生成四种标注区的mask图像（NECL）
        :param scale: 指定的倍镜数
        :param width: 边缘区单边宽度
        :return: 对应的Mask图像
        '''
        return self._slide.create_mask_image(scale, width)

    def get_effective_zone(self, scale):
        '''
        得到切片中，有效处理区域的Mask图像
        :param scale: 指定的倍镜
        :return: Mask图像
        '''
        fullImg = self.get_fullimage_byScale(scale)

        img = color.rgb2hsv(fullImg)

        mask1 = (img[:, :, 2] < 0.80) & (img[:, :, 2] > 0.20)
        mask2 = (img[:, :, 1] > 0.1)
        result = mask1 & mask2
        # mask3 = (img[:, :, 0] < 0.9) & (img[:, :, 0] > 0.05)
        # result = mask1 & mask2 & mask3


        result = morphology.binary_closing(result, square(4))
        result = morphology.binary_erosion(result, square(4))
        # result = morphology.binary_dilation(result, square(8))
        return result


    def get_mask_min_rect(self, mask_image):
        k = 4
        clip_mask = np.copy(mask_image)
        clip_mask[0:k, ...] = False
        clip_mask[-k:-1, ...] = False
        clip_mask[..., 0:k] = False
        clip_mask[ ..., -k:-1] = False

        pos = clip_mask.nonzero()
        y = np.array(pos[0])
        x = np.array(pos[1])
        xmin = np.min(x)
        xmax = np.max(x)
        ymin = np.min(y)
        ymax = np.max(y)
        # （x1, y1）, 左上角坐标， （x2, y2） 右下角坐标
        return xmin, ymin, xmax, ymax

    def get_uniform_sampling_blocks(self, extract_scale, patch_size, ):
        low_scale = self._params.GLOBAL_SCALE
        eff_region = self.get_effective_zone(low_scale)
        area = np.sum(eff_region)
        sampling_interval = 2000
        seeds = get_seeds(eff_region, low_scale, extract_scale, patch_size, spacingHigh=sampling_interval, margin=0)

        result = []
        for (x, y) in seeds:
            block = self.get_image_block(extract_scale, x, y, patch_size, patch_size)
            result.append(block.get_img())

        return result
