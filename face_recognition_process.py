# import cv2
import face_recognition as fr
import os
import csv
import shutil
import json
import time
import tqdm
from config import get_dir_name

def face_recognition_process(selfie_folder_path, photos_path, output_path):
    print("################", output_path)
    print("[[[[[[[[[[[[[[[[[[[]]]]]]]]]]]]]]]]]]]", photos_path)
    
    img_names = os.listdir(photos_path)
    selfie_encodings = {}
    test_images_encodings = {}
    for img_name in tqdm.tqdm(img_names):
        if not img_name.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp")):
            continue
        img = fr.load_image_file(os.path.join(photos_path, img_name))
        face_locations = fr.face_locations(img)
        face_encodings = []
        for face_location in face_locations:
            face_encoding = fr.face_encodings(img, [face_location])[0]
            face_encodings.append(face_encoding)
        test_images_encodings[img_name] = face_encodings
    test_image_names = os.listdir(selfie_folder_path)
    for image_name in tqdm.tqdm(test_image_names):
        if not image_name.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp")):
            continue
        name = image_name[: (-len(list(image_name.split("."))[-1]) - 1) :]
        name = get_dir_name(test_images_encodings.keys(), name)
        test_image = fr.load_image_file(os.path.join(selfie_folder_path, image_name))
        try:
            test_face_encoding = fr.face_encodings(test_image)[0]
        except:
            print("Exception Here #########################")
            continue
        os.chdir(output_path)
        # try:
        #     os.mkdirs(name, exist_ok=True)
        # except:
        #     print("Exception there..................")
        #     continue
            
        selfie_encodings[name] = test_face_encoding
        for img_name in img_names:
            print(img_name, "-------------------")
            for target_face_encoding in test_images_encodings[img_name]:
                print("------------1111")
                if fr.compare_faces(
                    [target_face_encoding], test_face_encoding, tolerance=0.4
                )[0]:
                    print("725975357370977375893765737583757387589738787777897837873878")
                    print(photos_path, output_path)
                    print(os.path.join(photos_path, img_name), "-----------------------")
                    print(os.path.join(output_path, name, img_name), "------------------------",os.path.join(output_path, name))
                    os.makedirs(os.path.join(output_path, name), exist_ok=True)
                    print("Directory created ---------------")
                    shutil.copy(
                        os.path.join(photos_path, img_name),
                        os.path.join(output_path, name, img_name),
                    )
                    break
