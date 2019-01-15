#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__author__ = 'Justin'
__mtime__ = '2018-10-26'

"""
import numpy as np
from sklearn import metrics
from skimage.draw import rectangle # 需要skimage 0.14及以上版本
from core.util import get_seeds, transform_coordinate
from pytorch.transfer_cnn import Transfer
from pytorch.cnn_classifier import CNN_Classifier
from pytorch.segmentation import Segmentation
import cv2
from scipy.interpolate import griddata

# N = 500

class Detector(object):

    def __init__(self, params, src_image):
        '''
        初始化
        :param params: 参数
        :param src_image: 切片图像
        '''
        self._params = params
        self._imgCone = src_image

        w, h = self._imgCone.get_image_width_height_byScale(self._params.GLOBAL_SCALE)
        self.ImageWidth = w
        self.ImageHeight = h
        self.valid_map = np.zeros((h, w), dtype=np.bool)
        self.enable_transfer = False
        return

    def setting_detected_area(self, x1, y1, x2, y2, scale):
        '''
        设置需要检测的区域
        :param x1: 左上角x坐标
        :param y1: 左上角y坐标
        :param x2: 右下角x坐标
        :param y2: 右下角y坐标
        :param scale: 以上坐标的倍镜数
        :return: 生成检测区的mask
        '''
        GLOBAL_SCALE = self._params.GLOBAL_SCALE
        xx1, yy1, xx2, yy2 = np.rint(np.array([x1, y1, x2, y2 ])* GLOBAL_SCALE / scale).astype(np.int)
        rr, cc = rectangle((yy1, xx1), end=(yy2, xx2))
        self.valid_map[rr, cc] = 1
        self.valid_area_width = xx2 - xx1
        self.valid_area_height = yy2 - yy1
        return

    def reset_detected_area(self):
        '''
        清空检测区域的标记
        :return:
        '''
        self.valid_map =  np.zeros((self.ImageHeight, self.ImageWidth), dtype=np.bool)
        return

    def get_points_detected_area(self, extract_scale, patch_size_extract, interval):
        '''
        得到检测区域的图块中心点在高分辨率下的坐标
        :param extract_scale: 提取图时时，所使用的高分辨率对应的倍镜数
        :param patch_size_extract: 高分辨率下的图块大小
        :param interval: 高分辨率下的图块之间的距离
        :return: （x，y）种子点的集合
        '''
        return get_seeds(self.valid_map, self._params.GLOBAL_SCALE, extract_scale,patch_size_extract, interval, margin=8)

    def detect_region(self, x1, y1, x2, y2, coordinate_scale, extract_scale, patch_size, interval):
        '''
        进行区域内的检测
        :param x1: 左上角x坐标
        :param y1: 左上角y坐标
        :param x2: 右下角x坐标
        :param y2: 右下角y坐标
        :param coordinate_scale:以上坐标的倍镜数
        :param extract_scale: 提取图块所用的倍镜
        :param patch_size: 图块大小
        :return: 图块中心点集，预测的结果
        '''
        self.setting_detected_area(x1, y1, x2, y2, coordinate_scale)
        seeds = self.get_points_detected_area(extract_scale, patch_size, interval)

        if self.enable_transfer:
        #####################################################################################################
        #    Transfer Learning
        #####################################################################################################
            cnn = Transfer(self._params, "densenet121", "500_128")
        #########################################################################################################
        else:
        ########################################################################################################\
        #    DenseNet 22
        #########################################################################################################
            cnn = CNN_Classifier(self._params, "densenet_22", "500_128")
        #########################################################################################################
        predictions = cnn.predict_on_batch(self._imgCone, extract_scale, patch_size, seeds, 32)

        return seeds, predictions

    def detect_region_detailed(self, seeds, predictions, seeds_scale, original_patch_size, new_scale, new_patch_size):
        new_seeds = self.get_seeds_under_high_magnification(seeds, predictions, seeds_scale, original_patch_size,
                                                            new_scale, new_patch_size)

        if self.enable_transfer:
        #####################################################################################################
        #    Transfer Learning
        #####################################################################################################
            if (new_scale == 20):
                cnn = Transfer(self._params, "densenet121", "2000_256")
            else: # (new_scale == 40):
                cnn = Transfer(self._params, "densenet121", "4000_256")
        #########################################################################################################
        else:
        ########################################################################################################\
        #    DenseNet 22
        #########################################################################################################
            if (new_scale == 20):
                cnn = CNN_Classifier(self._params, "densenet_22", "2000_256")
            else: # (new_scale == 40):
                cnn = CNN_Classifier(self._params, "densenet_22", "4000_256")
        #########################################################################################################
        predictions = cnn.predict_on_batch(self._imgCone, new_scale, new_patch_size, new_seeds, 32)
        return new_seeds, predictions

    def get_seeds_under_high_magnification(self, seeds, predictions, seeds_scale, original_patch_size, new_scale, new_patch_size):
        '''
        获取置信度不高的种子点在更高倍镜下的图块中心点坐标
        :param seeds: 低倍镜下的种子点集合
        :param predictions: 低倍镜下的种子点所对应的检测结果
        :param seeds_scale: 种子点的低倍镜数
        :param original_patch_size: 低倍镜下的图块大小
        :param new_scale: 高倍镜数
        :param new_patch_size: 在高倍镜下的图块大小
        :return: 高倍镜下，种子点集合
        '''
        amplify = new_scale / seeds_scale
        partitions = original_patch_size * amplify / new_patch_size
        bias = int(original_patch_size * amplify / (2 * partitions))
        result = []
        print(">>> Number of patches detected at low magnification: ", len(predictions))

        for (x, y), (class_id, probability) in zip(seeds, predictions):
            if probability < 0.95:
                xx = int(x * amplify)
                yy = int(y * amplify)
                result.append((xx, yy))
                result.append((xx - bias, yy - bias))
                result.append((xx - bias, yy + bias))
                result.append((xx + bias, yy - bias))
                result.append((xx + bias, yy + bias))

                # result.append((xx, yy - bias))
                # result.append((xx, yy + bias))
                # result.append((xx + bias, yy))
                # result.append((xx - bias, yy))
        print(">>> Number of patches to be detected at high magnification: ", len(result))
        return result

    def create_cancer_map(self, x1, y1, coordinate_scale, seeds_scale, target_scale, seeds,
                          predictions, seeds_patch_size, pre_prob_map = None, pre_count_map = None):
        '''
        生成癌变可能性Map
        :param x1: 检测区域的左上角x坐标
        :param y1: 检测区域的左上角y坐标
        :param coordinate_scale: 以上坐标的倍镜数
        :param seeds_scale: 图块中心点（种子点）的倍镜
        :param target_scale: 目标坐标系所对应的倍镜
        :param seeds: 图块中心点集
        :param predictions: 每个图块的预测结果
        :param seeds_patch_size: 图块的大小
        :param seed_interval:
        :param pre_prob_map: 上次处理生成癌变概率图
        :param pre_count_map; 上次处理生成癌变的检测计数图
        :return: 癌变可能性Map
        '''
        new_seeds = transform_coordinate(x1, y1, coordinate_scale, seeds_scale, target_scale, seeds)
        target_patch_size = int(seeds_patch_size * target_scale / seeds_scale)
        half = int(target_patch_size>>1)

        cancer_map = np.zeros((self.valid_area_height, self.valid_area_width), dtype=np.float)
        prob_map = np.zeros((self.valid_area_height, self.valid_area_width), dtype=np.float)
        count_map = np.zeros((self.valid_area_height, self.valid_area_width), dtype=np.float)

        update_mode = not (pre_prob_map is None or pre_count_map is None)
        if update_mode:
            vaild_map = np.zeros((self.valid_area_height, self.valid_area_width), dtype=np.bool)

        for (x, y), (class_id, probability)  in zip(new_seeds, predictions):
            xx = x - half
            yy = y - half

            for K in np.logspace(0,2,3, base=2): # array([1., 2., 4.])
                w = int(target_patch_size / K)
                if w == 0:
                    continue

                rr, cc = rectangle((yy, xx), extent=(w, w))

                select_y = (rr >= 0) & (rr < self.valid_area_height)
                select_x = (cc >= 0) & (cc < self.valid_area_width)
                select = select_x & select_y

                if class_id == 1 :
                    prob_map[rr[select], cc[select]] = prob_map[rr[select], cc[select]] + probability
                else:
                    prob_map[rr[select], cc[select]] = prob_map[rr[select], cc[select]] + (1 - probability)

                count_map[rr[select], cc[select]] = count_map[rr[select], cc[select]] + 1

                if update_mode:
                    vaild_map[rr[select], cc[select]] = True

        if update_mode:
            pre_cancer_map = np.zeros((self.valid_area_height, self.valid_area_width), dtype=np.float)
            tag = pre_count_map > 0
            pre_cancer_map[tag] = pre_prob_map[tag] / pre_count_map[tag]

            # 更新平均概率
            keep_tag = (~vaild_map) | (pre_cancer_map >= 0.8) # 提高低倍镜分类器性能，将可以提高这个阈值
            prob_map[keep_tag] = pre_prob_map[keep_tag]
            count_map[keep_tag] = pre_count_map[keep_tag]

        tag = count_map > 0
        cancer_map[tag] = prob_map[tag] / count_map[tag]
        return cancer_map, prob_map, count_map

    def get_img_in_detect_area(self, x1, y1, x2, y2, coordinate_scale, img_scale):
        '''
        得到指定的检测区域对应的图像
        :param x1: 左上角x坐标
        :param y1: 左上角y坐标
        :param x2: 右下角x坐标
        :param y2: 右下角y坐标
        :param coordinate_scale:以上坐标的倍镜数
        :param img_scale: 提取图像所对应的倍镜
        :return:指定的检测区域对应的图像
        '''
        xx1, yy1, xx2, yy2 = np.rint(np.array([x1, y1, x2, y2]) * img_scale / coordinate_scale).astype(np.int)
        w = xx2 - xx1
        h = yy2 - yy1
        block = self._imgCone.get_image_block(img_scale, int(xx1 + (w >> 1)), int(yy1 + (h >> 1)), w, h)
        return block.get_img()

    def get_true_mask_in_detect_area(self, x1, y1, x2, y2, coordinate_scale, img_scale):
        '''
        生成选定区域内的人工标记的Mask
        :param x1: 左上角x
        :param y1: 左上角y
        :param x2: 右下角x
        :param y2: 右下角y
        :param coordinate_scale 以上坐标的倍镜数:
        :param img_scale: 生成Mask图像的倍镜数
        :return: mask图像
        '''
        xx1, yy1, xx2, yy2 = np.rint(np.array([x1, y1, x2, y2]) * img_scale / coordinate_scale).astype(np.int)
        w = xx2 - xx1
        h = yy2 - yy1

        all_mask = self._imgCone.create_mask_image(img_scale, 0)
        cancer_mask = all_mask['C']
        return cancer_mask[yy1:yy2, xx1:xx2]

    def evaluate(self, threshold, cancer_map, true_mask):
        '''
        癌变概率矩阵进行阈值分割后，与人工标记真值进行 评估
        :param threshold: 分割的阈值
        :param cancer_map: 癌变概率矩阵
        :param true_mask: 人工标记真值
        :return: ROC曲线
        '''
        cancer_tag = np.array(cancer_map).ravel()
        mask_tag = np.array(true_mask).ravel()
        predicted_tags = cancer_tag >= threshold

        print("Classification report for classifier:\n%s\n"
              % (metrics.classification_report(mask_tag, predicted_tags)))
        print("Confusion matrix:\n%s" % metrics.confusion_matrix(mask_tag, predicted_tags))

        false_positive_rate, true_positive_rate, thresholds = metrics.roc_curve(mask_tag, cancer_tag)
        roc_auc = metrics.auc(false_positive_rate, true_positive_rate)
        print("\n ROC auc: %s" % roc_auc)

        dice = self.calculate_dice_coef(mask_tag, cancer_tag)
        print("dice coef = {}".format(dice))
        print("############################################################")
        return false_positive_rate, true_positive_rate, roc_auc

    def calculate_dice_coef(self, y_true, y_pred):
        smooth = 1.
        y_true_f = y_true.flatten()
        y_pred_f = y_pred.flatten()
        intersection = np.sum(y_true_f * y_pred_f)
        dice = (2. * intersection + smooth) / (np.sum(y_true_f * y_true_f) + np.sum(y_pred_f * y_pred_f) + smooth)
        return dice

    def create_superpixels(self, x1, y1, x2, y2, coordinate_scale, feature_extract_scale):
        '''
        在指定区域内，提取特征，并进行超像素分割
        :param x1: 左上角x
        :param y1: 左上角y
        :param x2: 右下角x
        :param y2: 右下角y
        :param coordinate_scale: 以上坐标的倍镜数
        :param feature_extract_scale: 提取特征所用的倍镜数
        :return: 超像素分割后的标记矩阵
        '''
        seg = Segmentation(self._params, self._imgCone)
        f_map = seg.create_feature_map(x1, y1, x2, y2, coordinate_scale, feature_extract_scale)
        label_map = seg.create_superpixels(f_map, 0.4, iter_num = 3)

        return label_map

    def create_cancer_map_superpixels(self, cancer_map, label_map):
        '''
        根据超像素分割，生成癌变概率图
        :param cancer_map: 输入的癌变概率图
        :param label_map:超像素分割的结果
        :return: 融合后生成的癌变概率图
        '''
        label_set = set(label_map.flatten())

        result_cancer = np.zeros(cancer_map.shape, dtype=np.float)
        for label_id in label_set:
            roi = (label_map == label_id)
            cancer_roi = cancer_map[roi]
            mean = np.mean(cancer_roi, axis=None)
            std = np.std(cancer_roi, axis=None)

            result_cancer[roi] = mean

        return result_cancer

    def adaptive_detect_region(self, x1, y1, x2, y2, coordinate_scale, extract_scale, patch_size,
                               max_iter_nums, batch_size):
        self.setting_detected_area(x1, y1, x2, y2, coordinate_scale)
        cnn = CNN_Classifier(self._params, "densenet_22", "2000_256")

        # 生成坐标网格
        grid_y, grid_x = np.mgrid[0: self.valid_area_height: 1, 0: self.valid_area_width: 1]

        sobel_img = None
        interpolate_img = None
        history = {}
        N = 400

        seeds_scale = self._params.GLOBAL_SCALE
        amplify = extract_scale / seeds_scale
        bias = int(0.25 * patch_size / amplify)

        for i in range(max_iter_nums):
            print("iter %d" % (i + 1))
            seeds = self.get_random_seeds(N, x1, x2, y1, y2, sobel_img)

            new_seeds = self.remove_duplicates(x1, y1, seeds, set(history.keys()))
            print("the number of new seeds: ", len(new_seeds))

            if len(new_seeds) / N < 0.9:
                break

            high_seeds = transform_coordinate(0, 0, coordinate_scale, seeds_scale, extract_scale, new_seeds)
            predictions = cnn.predict_on_batch(self._imgCone, extract_scale, patch_size, high_seeds, batch_size)
            probs = self.get_cancer_probability(predictions)

            for (x,y), pred in zip(new_seeds, probs):
                xx = x - x1
                yy = y - y1

                if  not history.__contains__((xx, yy)):
                    history[(xx, yy)] = pred
                # else:
                #     history[(xx, yy)].append(pred)

                # all_seeds_preds[(xx - bias, yy - bias)] = pred
                # all_seeds_preds[(xx + bias, yy - bias)] = pred
                # all_seeds_preds[(xx - bias, yy + bias)] = pred
                # all_seeds_preds[(xx + bias, yy + bias)] = pred


            value = list(history.values())
            point = list(history.keys())
            interpolate_img, sobel_img = self.inter_sobel(point, value,
                                                          (grid_x, grid_y), method='cubic')

        return interpolate_img


    def get_random_seeds(self, N, x1, x2, y1, y2, sobel_img):
        n = 2 * N
        x = np.random.randint(x1, x2 - 1, size=n, dtype='int')
        y = np.random.randint(y1, y2 - 1, size=n, dtype='int')
        if sobel_img is not None:
            prob = sobel_img[y - y1, x - x1]
            index = prob.argsort()
            index = index[-N:]
            x = x[index]
            y = y[index]
        return tuple(zip(x, y))

    def get_cancer_probability(self, predictions):
        probs = []
        for pred, prob in predictions:
            if pred == 0:
                probs.append(1 - prob)
            else:
                probs.append(prob)

        return probs

    def inter_sobel(self, point, value,  grid_x_y, method='nearest', fill_value=0.0):
        interpolate = griddata(point, value, grid_x_y, method=method, fill_value=fill_value)
        sobel_img = cv2.Sobel(interpolate, -1, 2, 2)
        return interpolate, sobel_img

    def remove_duplicates(self, x1, y1,  new_seeds, old_seeds):
        shift_seeds = set((xx - x1, yy - y1) for xx, yy in new_seeds)
        result = shift_seeds - old_seeds
        revert_seeds = set((xx + x1, yy + y1) for xx, yy in result)
        return revert_seeds



