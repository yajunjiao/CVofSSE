# 进行人脸录入 / face register
# 录入多张人脸 / support multi-faces

import dlib         # 人脸处理的库 Dlib
import numpy as np  # 数据处理的库 Numpy
import cv2          # 图像处理的库 OpenCV
import os           # 读写文件
import shutil       # 读写文件
import time

# Dlib 正向人脸检测器
detector = dlib.get_frontal_face_detector()


class Face_Register:
    def __init__(self):
        self.path_photos_from_camera = "data/data_faces_from_camera/"
        self.font = cv2.FONT_ITALIC

        self.existing_faces_cnt = 0     # 已录入的人脸计数器
        self.ss_cnt = 0                 # 录入 personX 人脸时图片计数器
        self.faces_cnt = 0              # 录入人脸计数器

        # 之后用来控制是否保存图像的 flag
        self.save_flag = 1
        # 之后用来检查是否先按 'n' 再按 's'，即先新建文件夹再保存
        self.press_n_flag = 0

        self.frame_time = 0
        self.frame_start_time = 0
        self.fps = 0

    # 新建保存人脸图像文件
    def pre_work_mkdir(self):
        if os.path.isdir(self.path_photos_from_camera):
            pass
        else:
            os.mkdir(self.path_photos_from_camera)

    # 删除之前存的人脸数据文件夹
    def pre_work_del_old_face_folders(self):
        # 删除之前存的人脸数据文件夹
        folders_rd = os.listdir(self.path_photos_from_camera)
        for i in range(len(folders_rd)):
            shutil.rmtree(self.path_photos_from_camera+folders_rd[i])
        if os.path.isfile("data/features_all.csv"):
            os.remove("data/features_all.csv")

    # 如果有之前录入的人脸, 在之前 person_x 的序号按照 person_x+1 开始录入
    def check_existing_faces_cnt(self):
        if os.listdir("data/data_faces_from_camera/"):
            # 获取已录入的最后一个人脸序号
            person_list = os.listdir("data/data_faces_from_camera/")
            person_num_list = []
            for person in person_list:
                person_num_list.append(int(person.split('_')[-1]))
            self.existing_faces_cnt = max(person_num_list)

        # 如果第一次存储或者没有之前录入的人脸, 按照 person_1 开始录入
        # Start from person_1
        else:
            self.existing_faces_cnt = 0

    # 获取处理之后 stream 的帧数
    def update_fps(self):
        now = time.time()
        self.frame_time = now - self.frame_start_time
        self.fps = 1.0 / self.frame_time
        self.frame_start_time = now

    # 生成的 cv2 window 上面添加说明文字
    def draw_note(self, img_rd):
        # 添加说明
        cv2.putText(img_rd, "Face Register", (20, 40), self.font, 1, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.putText(img_rd, "FPS:   " + str(self.fps.__round__(2)), (20, 100), self.font, 0.8, (0, 255, 0), 1,
                    cv2.LINE_AA)
        cv2.putText(img_rd, "Faces: " + str(self.faces_cnt), (20, 140), self.font, 0.8, (0, 255, 0), 1, cv2.LINE_AA)
        cv2.putText(img_rd, "N: Create face folder", (20, 350), self.font, 0.8, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.putText(img_rd, "S: Save current face", (20, 400), self.font, 0.8, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.putText(img_rd, "Q: Quit", (20, 450), self.font, 0.8, (255, 255, 255), 1, cv2.LINE_AA)

    # 获取人脸
    def process(self, stream):
        # 1. 新建储存人脸图像文件目录
        # self.pre_work_mkdir()

        # 2. 删除 "/data/data_faces_from_camera" 中已有人脸图像文件
        self.pre_work_del_old_face_folders()

        # 3. 检查 "/data/data_faces_from_camera" 中已有人脸文件
        self.check_existing_faces_cnt()

        while stream.isOpened():
            flag, img_rd = stream.read()        # Get camera video stream
            kk = cv2.waitKey(1)
            faces = detector(img_rd, 0)         # Use dlib face detector

            # 4. 按下 'n' 新建存储人脸的文件夹
            if kk == ord('n'):
                self.existing_faces_cnt += 1
                current_face_dir = self.path_photos_from_camera + "person_" + str(self.existing_faces_cnt)
                os.makedirs(current_face_dir)
                print('\n')
                print("新建的人脸文件夹 / Create folders: ", current_face_dir)

                self.ss_cnt = 0              # 将人脸计数器清零
                self.press_n_flag = 1        # 已经按下 'n'

            # 5. 检测到人脸
            if len(faces) != 0:
                # 矩形框
                for k, d in enumerate(faces):
                    # 计算矩形框大小
                    height = (d.bottom() - d.top())
                    width = (d.right() - d.left())
                    hh = int(height/2)
                    ww = int(width/2)

                    # 6. 判断人脸矩形框是否超出 480x640
                    if (d.right()+ww) > 640 or (d.bottom()+hh > 480) or (d.left()-ww < 0) or (d.top()-hh < 0):
                        cv2.putText(img_rd, "OUT OF RANGE", (20, 300), self.font, 0.8, (0, 0, 255), 1, cv2.LINE_AA)
                        color_rectangle = (0, 0, 255)
                        save_flag = 0
                        if kk == ord('s'):
                            print("请调整位置 / Please adjust your position")
                    else:
                        color_rectangle = (255, 255, 255)
                        save_flag = 1

                    cv2.rectangle(img_rd,
                                  tuple([d.left() - ww, d.top() - hh]),
                                  tuple([d.right() + ww, d.bottom() + hh]),
                                  color_rectangle, 2)

                    # 7. 根据人脸大小生成空的图像
                    img_blank = np.zeros((int(height*2), width*2, 3), np.uint8)

                    if save_flag:
                        # 8. 按下 's' 保存摄像头中的人脸到本地
                        if kk == ord('s'):
                            # 检查有没有先按'n'新建文件夹
                            if self.press_n_flag:
                                self.ss_cnt += 1
                                for ii in range(height*2):
                                    for jj in range(width*2):
                                        img_blank[ii][jj] = img_rd[d.top()-hh + ii][d.left()-ww + jj]
                                cv2.imwrite(current_face_dir + "/img_face_" + str(self.ss_cnt) + ".jpg", img_blank)
                                print("写入本地 / Save into：", str(current_face_dir) + "/img_face_" + str(self.ss_cnt) + ".jpg")
                            else:
                                print("请先按 'N' 来建文件夹, 按 'S' / Please press 'N' and press 'S'")
                self.faces_cnt = len(faces)

            # 9. 生成的窗口添加说明文字
            self.draw_note(img_rd)

            # 10. 按下 'q' 键退出
            if kk == ord('q'):
                break

            self.update_fps()
            cv2.namedWindow("camera", 1)
            cv2.imshow("camera", img_rd)

    def run(self):
        cap = cv2.VideoCapture(0)
        self.process(cap)

        cap.release()
        cv2.destroyAllWindows()


def main():
    Face_Register_con = Face_Register()
    Face_Register_con.run()


if __name__ == '__main__':
    main()