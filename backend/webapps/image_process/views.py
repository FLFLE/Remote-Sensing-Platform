import base64
import os
import paddle
from webapps.user.models import User
from webapps.history.models import History
from rest_framework import status
from rest_framework.views import APIView
from webapps.image_process import predictors
from PIL import Image
from webapps.utils import generate_response
import cv2 as cv
import numpy as np


# 遥感图像处理的相关视图
class ImageView(APIView):
    def post(self, request):
        email_address = request.data["email_address"]
        if self.change_remain_times(email_address):
            action = request.data["action"]
            if action == "change_detection":
                return self.change_detection(request, email_address)
            elif action == "target_detection":
                category = request.data["category"]
                return self.target_detection(request, email_address, category)
            elif action == "terrain_classification":
                return self.terrain_classification(request, email_address)
            elif action == "target_extraction":
                return self.target_extraction(request, email_address)
            else:
                return generate_response(
                    {"msg": "action error"}, status.HTTP_400_BAD_REQUEST
                )
        else:
            return generate_response(
                {"msg": "用户本日使用次数不足，请明日再使用，或邮件联系我们。"}, status.HTTP_403_FORBIDDEN
            )

    # 变化检测
    @paddle.no_grad()
    def change_detection(self, request, email_address):
        action = "CHANGE_DETECTION"
        files = request.FILES.getlist("file")
        # 保存图片资源的路径, 对不同用户上传的图片分开保存
        access_input_dir_A = os.path.join(
            "images/change_detection/", email_address+'/', "A/"
        )
        access_input_dir_B = os.path.join(
            "images/change_detection/", email_address+'/', "B/"
        )
        access_result_dir = os.path.join(
            "images/change_detection/", email_address+'/', "result/"
        )
        input_dir_A = os.path.join("backend/", access_input_dir_A)
        input_dir_B = os.path.join("backend/", access_input_dir_B)
        result_dir = os.path.join("backend/", access_result_dir)

        # 为每个用户单独创建文件夹
        self.mkdir([input_dir_A, input_dir_B, result_dir])

        file_numbers = len(files)
        # 上传的原图的访问路径
        upload_list = []
        # 用于存放返回给前端的结果
        result_list = []
        # 存储需要进行预测处理的图片，每相邻两张图片视作一对
        input_images = []
        # 变化像素的统计结果
        statistic_list = []
        # predictor = predictors.change_detection_predictor()
        predictor = predictors.change_detection_predictor
        for i in range(file_numbers):
            image = files[i]
            # 对于奇数项的图片，视作A标签图片
            if i % 2 == 0:
                input_path = os.path.join(input_dir_A, image.name)
                access_path = os.path.join(access_input_dir_A, image.name)
                Image.open(image).save(input_path)
                input_images.append(input_path)
                upload_list.append(access_path)

            # 对于偶数项的图片，视为B标签图片
            elif i % 2 != 0:
                input_path = os.path.join(input_dir_B, image.name)
                access_path = os.path.join(access_input_dir_B, image.name)
                Image.open(image).save(input_path)
                input_images.append(input_path)
                upload_list.append(access_path)
                result = predictor.predict(
                    img_file=tuple(input_images[(i - 1) : (i + 1) : 1])
                )

                img_ndarray = result[0]["label_map"] * 255
                total_pixel = img_ndarray.shape[0] * img_ndarray.shape[1]
                changed_pixel = np.sum(result[0]["label_map"])
                mod_result = self.CD_process(result[0]["label_map"], input_path)
                statistic_list.append(
                    {
                        "total_pixel": int(total_pixel),
                        "changed_pixel": int(changed_pixel),
                        "blocks": int(mod_result[1]),
                    }
                )
                # return the modified image

                mod_file = mod_result[0]
                mod_access_path = os.path.join(access_result_dir, "mod_" + image.name)
                # decide where to save the modified file
                mod_save_path = os.path.join("backend/", mod_access_path)
                # save the image file
                cv.imwrite(mod_save_path, mod_file)
                result_img = Image.fromarray(img_ndarray)
                result_path = os.path.join(result_dir, image.name)
                access_result_path = os.path.join(access_result_dir, image.name)
                result_img.convert("L").save(result_path)
                result_list.append(access_result_path)
                # return 2 path instead 1 path: the label img and the modified "B" img
                result_list.append(mod_access_path)
        # release([predictor, img_ndarray, result_img])
        self.save_record(upload_list, result_list, email_address, action)
        # 返回状态信息和图片列表
        msg = {
            "msg": "图片处理成功！",
            "result": result_list,
            "input": upload_list,
            "statistic_list": statistic_list,
        }
        return generate_response(msg, status.HTTP_200_OK)


    # 目标提取功能
    @paddle.no_grad()
    def target_extraction(self, request, email_address):
        action = "TARGET_EXTRACTION"
        image_names = request.FILES.getlist("file")
        # 用于保存可供访问的原图路径
        upload_list = []
        # 保存可供访问的结果路径
        result_list = []
        # 保存统计结果
        statistic_list = []
        # 保存图片资源的路径, 对不同用户上传的图片分开保存
        access_input_dir = os.path.join(
            "images/target_extraction/", email_address+'/', "input/"
        )
        access_result_dir = os.path.join(
            "images/target_extraction/", email_address+'/', "result/"
        )
        input_dir = os.path.join("backend/", access_input_dir)
        result_dir = os.path.join("backend/", access_result_dir)
        # 为每个用户单独创建文件夹
        self.mkdir([input_dir, result_dir])
        # pre = predictors.target_extraction_predictor()
        re = predictors.target_extraction_predictor
        for image in image_names:
            image_name = image.name
            # 将原图保存到相应文件夹
            predictors.save_image(image, input_dir)
            # 根据上传的图片进行推理，并且将推理结果保存
            result_path = predictors.infer(
                action,
                input_dir,
                result_dir,
                access_result_dir,
                image_name,
                predictor=pre,
            )
            # 将上传的原图访问路径保存
            upload_list.append(os.path.join(access_input_dir, image_name))
            # 将结果路径保存到list返回前端,一张是灰度图，一张是原图标注图
            result_list.append(result_path[0])
            result_list.append(result_path[1])
            # 统计结果返回前端
            statistic_list.append(result_path[2])

        # 添加上传记录
        self.save_record(upload_list, result_list, email_address, action)
        # release([pre])
        # 返回状态信息和图片列表
        msg = {
            "msg": "图片处理成功！",
            "result": result_list,
            "input": upload_list,
            "statistic_list": statistic_list,
        }
        return generate_response(msg, status.HTTP_200_OK)

    # 目标检测功能
    @paddle.no_grad()
    def target_detection(self, request, email_address, category):
        action = "TARGET_DETECTION"
        image_names = request.FILES.getlist("file")
        # 用于保存可供访问的原图路径
        upload_list = []
        # 保存可供访问的结果路径
        result_list = []

        # 保存图片资源的路径, 对不同用户上传的图片分开保存
        access_input_dir = os.path.join(
            "images/target_detection/", category, email_address+'/', "input/"
        )
        access_result_dir = os.path.join(
            "images/target_detection/", category, email_address+'/', "result/"
        )

        input_dir = os.path.join("backend/", access_input_dir)
        result_dir = os.path.join("backend/", access_result_dir)
        # 为每个用户单独创建文件夹
        self.mkdir([input_dir, result_dir])
        pre = predictors.target_detection_predictor(category)
        for image in image_names:
            image_name = image.name
            # 将原图保存到相应文件夹
            predictors.save_image(image, input_dir)
            # 根据上传的图片进行推理，并且将推理结果保存
            result_path = predictors.infer(
                action,
                input_dir,
                result_dir,
                access_result_dir,
                image_name,
                predictor=pre,
            )
            # 可访问的原图路径
            upload_list.append(os.path.join(access_input_dir, image_name))
            # 将结果路径保存到list返回前端
            result_list.append(result_path)

        # 添加上传记录
        self.save_record(upload_list, result_list, email_address, action)
        # release([pre])
        # 返回状态信息和图片列表
        msg = {"msg": "图片处理成功！", "result": result_list, "input": upload_list}
        return generate_response(msg, status.HTTP_200_OK)

    # 地物分类功能
    @paddle.no_grad()
    def terrain_classification(self, request, email_address):
        action = "TERRAIN_CLASSIFICATION"
        image_names = request.FILES.getlist("file")
        # 用于保存可供访问的原图路径
        upload_list = []
        # 保存可供访问的结果路径
        result_list = []
        # 保存分类结果统计
        type_list = []
        # 保存图片资源的路径, 对不同用户上传的图片分开保存
        access_input_dir = os.path.join(
            "images/terrain_classification/", email_address+'/', "input/"
        )
        access_result_dir = os.path.join(
            "images/terrain_classification/", email_address+'/', "result/"
        )
        infer_result = []
        input_dir = os.path.join("backend/", access_input_dir)
        result_dir = os.path.join("backend/", access_result_dir)
        # 为每个用户单独创建文件夹
        self.mkdir([input_dir, result_dir])
        # pre = predictors.terrain_classification_predictor()
        pre = predictors.terrain_classification_predictor
        for image in image_names:
            image_name = image.name
            # 将原图保存到相应文件夹
            predictors.save_image(image, input_dir)
            # 根据上传的图片进行推理，并且将推理结果保存
            infer_result = predictors.infer(
                action,
                input_dir,
                result_dir,
                access_result_dir,
                image_name,
                predictor=pre,
            )
            result_path = infer_result[0]
            mod_result_path = infer_result[1]
            # 原图的路径
            upload_list.append(os.path.join(access_input_dir, image_name))
            # 将结果路径保存到list返回前端，一张是彩色分类图，一张是合并对比图
            result_list.append(result_path)
            result_list.append(mod_result_path)
            # 所有图片的统计结果
            type_list.append(infer_result[2])

        # 储存本次操作的记录
        self.save_record(upload_list, result_list, email_address, action)
        # release([pre])
        # 返回状态信息和图片列表
        msg = {
            "msg": "图片处理成功！",
            "result": result_list,
            "input": upload_list,
            "type_statistic": type_list,
        }
        return generate_response(msg, status.HTTP_200_OK)

    def change_remain_times(self, current_email_address):
        user = User.objects.get(email_address=current_email_address)
        current_remain_time = user.times
        current_remain_time = current_remain_time - 1
        if current_remain_time >= 0:
            user.times = current_remain_time
            user.save()
            return True
        else:
            return False

    def CD_process(self, result, input_path):
        img = cv.imread(input_path)
        label = result.astype(np.uint8)
        label *= 255
        if len(label.shape) != 2:
            label = np.reshape((1024, 1024))
        co, _ = cv.findContours(label, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        res = cv.drawContours(img, co, -1, (0, 0, 205), 3)
        return [res, len(co)]

    def mkdir(self, dir_paths):
        for dir in dir_paths:
            if not os.path.exists(dir):
                os.makedirs(dir)


    def save_record(self, upload_list, result_list, email_address, action):
        upload_images = "?".join(upload_list)
        result_images = "?".join(result_list)
        History.objects.create(
            email_address=email_address,
            upload_images=upload_images,
            result_images=result_images,
            type = action
        )
        user = User.objects.get(email_address=email_address)
        if action == "CHANGE_DETECTION":
            user.cd_use_time = user.cd_use_time + 1
        elif action == "TARGET_DETECTION":
            user.td_use_time = user.td_use_time + 1
        elif action == "TARGET_EXTRACTION":
            user.te_use_time = user.te_use_time + 1
        elif action == "TERRAIN_CLASSIFICATION":
            user.tc_use_time = user.tc_use_time + 1
        user.save()


class ImageDownload(APIView):
    def post(self, request):
        return self.download(request)

    def download(self, request):
            base64_list = []
            image_paths = request.data["image_path"]
            prefix = "backend/"
            for img in image_paths:
                path = os.path.join(prefix, img)
                try:
                    img = open(path, "rb")
                except FileNotFoundError as f:
                    return generate_response({"msg":"file not exist"}, status.HTTP_404_NOT_FOUND)
                img_base64 = base64.b64encode(img.read())
                base64_list.append(str(img_base64,encoding='utf-8'))
                img.close()
            return generate_response({"base64_list": base64_list}, status.HTTP_200_OK)
