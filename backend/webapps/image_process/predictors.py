import cv2 as cv
import paddle
import paddlers as pdrs
from PIL import Image
import os
from paddlers.tasks.utils.visualize import visualize_detection
import numpy as np


# 变化检测用到的推理器
def change_detection_predictor():
    return pdrs.deploy.Predictor(
        "backend/models/change_detection", use_gpu=True, gpu_id=0
    )


def target_extraction_predictor():
    return pdrs.deploy.Predictor(
        "backend/models/target_extraction", use_gpu=True, gpu_id=0
    )


def terrain_classification_predictor():
    return pdrs.deploy.Predictor(
        "backend/models/terrain_classification", use_gpu=True, gpu_id=0
    )


def target_detection_predictor(category):
    if category == "playground":
        # 目标检测用到的推理器(playground)
        return pdrs.deploy.Predictor(
            "backend/models/target_detection_playground/", use_gpu=True, gpu_id=0
        )

    elif category == "aircraft":
        # 目标检测用到的推理器(playground)
        return pdrs.deploy.Predictor(
            "backend/models/target_detection_aircraft/", use_gpu=True, gpu_id=0
        )

    elif category == "oiltank":
        # 目标检测用到的推理器(playground)
        return pdrs.deploy.Predictor(
            "backend/models/target_detection_oiltank/", use_gpu=True, gpu_id=0
        )

    elif category == "overpass":
        # 目标检测用到的推理器(playground)
        return pdrs.deploy.Predictor(
            "backend/models/target_detection_overpass/", use_gpu=True, gpu_id=0
        )


def save_image(image, input_dir):
    image_name = image.name
    Image.open(image).save(os.path.join(input_dir, image_name))


# 将除了变化检测的推理方法封装起来
@paddle.no_grad()
def infer(action, input_dir, result_dir, access_result_dir, image_name, **kw):
    input_path = os.path.join(input_dir, image_name)
    result_path = os.path.join(result_dir, image_name)

    if action == "TARGET_EXTRACTION":
        # 目标提取用到的推理器
        # predictor = target_extraction_predictor()
        predictor = kw["predictor"]
        result = predictor.predict(img_file=[input_path])
        # Modified input image,
        modified_img = post_process(result[0]["label_map"], input_path)
        # path of modified image.
        mod_access_path = os.path.join(access_result_dir, "mod_" + image_name)
        mod_save_path = os.path.join("backend/", mod_access_path)
        # save the image file
        cv.imwrite(mod_save_path, modified_img)
        img_ndarray = result[0]["label_map"] * 255
        result_img = Image.fromarray(img_ndarray)
        result_img.convert("L").save(result_path)
        # 结果图片访问路径
        access_path = os.path.join(access_result_dir, image_name)
        total_pixel = result[0]["label_map"].shape[0] * result[0]["label_map"].shape[1]
        target_pixel = np.sum(result[0]["label_map"])
        statistic_dic = {
            "total_pixel": int(total_pixel),
            "target_pixel": int(target_pixel),
        }
        # release(
        #     [predictor, result, modified_img, img_ndarray, result_img]
        # )
        return [access_path, mod_access_path, statistic_dic]

    elif action == "TARGET_DETECTION":
        prefix = "visualize_"
        result_img_name = prefix + image_name
        predicor = kw["predictor"]
        result = predicor.predict(img_file=input_path)
        color = np.asarray([[0, 0, 255]])
        # 结果可视化
        visualize_detection(input_path, result, 0.5, save_dir=result_dir, color=color)
        access_path = os.path.join(access_result_dir, result_img_name)
        # release([result, color])
        return access_path

    elif action == "TERRAIN_CLASSIFICATION":
        predictor = kw["predictor"]
        original_img = cv.imread(input_path)
        result = predictor.predict(img_file=[input_path])
        img_ndarray = result[0]["label_map"]
        img = classify_process(img_ndarray)
        cv.imwrite(result_path, img)
        access_path = os.path.join(access_result_dir, image_name)
        type_dic = {
            "cls1": int(np.sum(img_ndarray == 0)),
            "cls2": int(np.sum(img_ndarray == 1)),
            "cls3": int(np.sum(img_ndarray == 2)),
            "cls4": int(np.sum(img_ndarray == 3)),
            "bg": int(np.sum(img_ndarray == 4)),
            "total": int(np.sum(img_ndarray >= 0)),
        }
        mod_access_path = os.path.join(access_result_dir, "mod_" + image_name)
        mod_save_path = os.path.join("backend/", mod_access_path)
        mod_img = cv.addWeighted(original_img, 1.0, img, 0.48, 0)
        cv.imwrite(mod_save_path, mod_img)
        # release([predictor, result, img_ndarray, img])
        return [access_path, mod_access_path, type_dic]
    else:
        return None


def post_process(result, input):
    """Visualize the result,modify the input image.
    THE INPUT IMAGE RESOLUTION MUST BE 1024x1024
    :param action: the infer action
    :param result: the original label map. e.g. result[0]["label_map"]
    :param input: path of the input image file.
    :returns: Modified image file,BGR Format.
    :rtype: np.ndarray
    """
    img = cv.imread(input)
    label = result.astype(np.uint8)
    label *= 255
    if len(label.shape) != 2:
        label = np.reshape((1024, 1024))
    # co, _ = cv.findContours(label, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    co, _ = cv.findContours(label, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    res = cv.drawContours(img, co, -1, (0, 0, 205), -1)
    return res


def classify_process(result):
    """
    Modify the terrain classification label.
    :param result:the original label map
    """
    lut = np.zeros((256, 3), dtype=np.uint8)
    lut[0] = [255, 0, 0]
    lut[1] = [30, 255, 142]
    lut[2] = [60, 0, 255]
    lut[3] = [255, 222, 0]
    lut[4] = [255, 255, 255]

    if result.ndim == 3:
        result = cv.cvtColor(result, cv.COLOR_BGR2GRAY)
    res = lut[result]
    return res
