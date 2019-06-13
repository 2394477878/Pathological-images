#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__author__ = 'Justin'
__mtime__ = '2019-06-12'

"""

import numpy as np
import os
from skimage import measure
from skimage.measure import find_contours, approximate_polygon, \
    subdivide_polygon
from sklearn import metrics
from skimage import morphology
import csv

class Evaluation(object):
    def __init__(self,):
        pass

    @staticmethod
    def output_result_csv(project_root):
        save_path = "{}/results".format(project_root)
        for result_file in os.listdir(save_path):
            ext_name = os.path.splitext(result_file)[1]
            slice_id = result_file[:-14]
            if ext_name == ".npz":
                result = np.load("{}/{}".format(save_path, result_file))
                x1 = result["x1"]
                y1 = result["y1"]
                coordinate_scale = result["scale"]
                assert coordinate_scale==1.25, "Scale is Error!"

                cancer_map = result["cancer_map"]
                # print("max :", np.max(cancer_map), "min :", np.min(cancer_map))

                # thresh_list = [0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2]
                thresh_list = [0.6, 0.5, 0.4]
                points = Evaluation.search_max_points(cancer_map, thresh_list, x1, y1)

                csv_filename = "{0}/{1}.csv".format(save_path, slice_id)
                with open(csv_filename, 'w', newline='')as f:
                    f_csv = csv.writer(f)
                    for item in points:
                        f_csv.writerow([item["prob"], item["x"], item["y"]])

                print("完成 ", slice_id)
        return

    @staticmethod
    def search_max_points(cancer_map, thresh_list, x_letftop, y_lefttop):
        candidated_result = []
        last_thresh = 1.0
        for thresh in thresh_list:
            region = cancer_map > thresh
            candidated_tag, num_tag = morphology.label(region, neighbors=8, return_num=True)

            for index in range(1, num_tag + 1):
                invert_region = candidated_tag != index
                new_map = np.copy(cancer_map)
                new_map[invert_region] = 0

                max_value = np.max(new_map)
                if max_value < last_thresh:
                    pos = np.nonzero(new_map == max_value)
                    k = len(pos) // 2
                    x = pos[1][k] + x_letftop
                    y = pos[0][k] + y_lefttop
                    candidated_result.append({"x":32 * x, "y":32 * y, "prob":max_value})

            last_thresh = thresh

        return candidated_result

    @staticmethod
    def save_result_xml(GLOBAL_SCALE, PROJECT_ROOT, slice_id, x1, y1, coordinate_scale, cancer_map, threshold_list,):
        scale = int(40 / GLOBAL_SCALE)
        scale2 = int(40 / coordinate_scale)

        contours_set = {}
        for threshold in threshold_list:
            cancer_tag = np.array(cancer_map > threshold)
            contours = measure.find_contours(cancer_tag, 0.5)

            contours_x40 = []
            for n, contour in enumerate(contours):
                contour = approximate_polygon(np.array(contour), tolerance=0.01)
                c = scale * np.array(contour)  + np.array([y1, x1]) * scale2
                contours_x40.append(c)

            contours_set[threshold] = contours_x40

        Evaluation.write_xml(contours_set, PROJECT_ROOT, slice_id)

    @staticmethod
    def write_xml(contours_set, PROJECT_ROOT, slice_id):
        from xml.dom import minidom
        doc = minidom.Document()
        rootNode = doc.createElement("ASAP_Annotations")
        doc.appendChild(rootNode)

        AnnotationsNode = doc.createElement("Annotations")
        rootNode.appendChild(AnnotationsNode)

        colors = ["#00BB00", "#00FF00", "#FFFF00", "#BB0000", "#FF0000"]
        for k, (key, contours) in enumerate(contours_set.items()):
            Code = "{:.2f}".format(key)
            for i, contour in enumerate(contours):
                # one contour
                AnnotationNode = doc.createElement("Annotation")
                AnnotationNode.setAttribute("Name", str(i))
                AnnotationNode.setAttribute("Type", "Polygon")
                AnnotationNode.setAttribute("PartOfGroup", Code)
                AnnotationNode.setAttribute("Color", colors[k])
                AnnotationsNode.appendChild(AnnotationNode)

                CoordinatesNode = doc.createElement("Coordinates")
                AnnotationNode.appendChild(CoordinatesNode)

                for n, (y, x) in enumerate(contour):
                    CoordinateNode = doc.createElement("Coordinate")
                    CoordinateNode.setAttribute("Order", str(n))
                    CoordinateNode.setAttribute("X", str(x))
                    CoordinateNode.setAttribute("Y", str(y))
                    CoordinatesNode.appendChild(CoordinateNode)

        AnnotationGroups_Node = doc.createElement("AnnotationGroups")
        rootNode.appendChild(AnnotationGroups_Node)

        for k, (key, _) in enumerate(contours_set.items()):
            Code = "{:.2f}".format(key)
            GroupNode = doc.createElement("Group")
            GroupNode.setAttribute("Name", Code)
            GroupNode.setAttribute("PartOfGroup", "None")
            GroupNode.setAttribute("Color", colors[k])
            AnnotationGroups_Node.appendChild(GroupNode)

        f = open("{}/results/{}_output.xml".format(PROJECT_ROOT, slice_id), "w")
        doc.writexml(f, encoding="utf-8")
        f.close()

    staticmethod
    def calculate_dice_coef(y_true, y_pred):
        smooth = 1.
        y_true_f = y_true.flatten()
        y_pred_f = y_pred.flatten()
        intersection = np.sum(y_true_f * y_pred_f)
        dice = (2. * intersection + smooth) / (np.sum(y_true_f * y_true_f) + np.sum(y_pred_f * y_pred_f) + smooth)
        return dice

    @staticmethod
    def evaluate_slice_map(cancer_map, true_mask, levels):
        '''
        癌变概率矩阵进行阈值分割后，与人工标记真值进行 评估
        :param threshold: 分割的阈值
        :param cancer_map: 癌变概率矩阵
        :param true_mask: 人工标记真值
        :return: ROC曲线
        '''
        mask_tag = np.array(true_mask).ravel()

        dice_result = []
        for threshold in levels:
            cancer_tag = np.array(cancer_map > threshold).ravel()
            predicted_tags = cancer_tag >= threshold
            dice = Evaluation.calculate_dice_coef(mask_tag, cancer_tag)

            print("Threshold = {:.3f}, Classification report for classifier: \n{}".format(threshold,
                                            metrics.classification_report(mask_tag, predicted_tags, digits=4)))
            print("############################################################")
            # print("Confusion matrix:\n%s" % metrics.confusion_matrix(mask_tag, predicted_tags))

            dice_result.append((threshold, dice))

        for t, value in dice_result:
            print("when threshold = {:.3f}, dice coef = {:.6f}".format(t, value))
        print("############################################################")
        # 计算ROC曲线
        false_positive_rate, true_positive_rate, thresholds = metrics.roc_curve(mask_tag, np.array(cancer_map).ravel())
        roc_auc = metrics.auc(false_positive_rate, true_positive_rate)
        print("\n ROC auc: %s" % roc_auc)
        return false_positive_rate, true_positive_rate, roc_auc, dice_result

