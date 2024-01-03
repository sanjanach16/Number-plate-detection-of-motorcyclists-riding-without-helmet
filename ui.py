import tkinter as tk
from tkinter import filedialog
import cv2
import os
import shutil
from my_functions import *
import os
import shutil
import pytesseract
from PIL import Image, ImageTk
from tkinter import ttk
from matplotlib import pyplot as plt
import pytesseract
import pandas as pd
import csv
import pywhatkit
from datetime import datetime
from datetime import timedelta
from matplotlib import pyplot as plt
import glob





def process_video(video_file):
    source = video_file
    save_video = True # want to save video? (when video as source)
    show_video=True # set true when using video file
    save_img=True  # set true when using only image file to save the image
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter('output.avi', fourcc, 20.0, frame_size)
    cap = cv2.VideoCapture(source)
    while(cap.isOpened()):
        ret, frame = cap.read()
        if ret == True:
            frame = cv2.resize(frame, frame_size)  # resizing image
            orifinal_frame = frame.copy()
            frame, results = object_detection(frame) 
            rider_list = []
            head_list = []
            number_list = []
            for result in results:
                x1,y1,x2,y2,cnf, clas = result
                if clas == 0:
                    rider_list.append(result)
                elif clas == 1:
                    head_list.append(result)
                elif clas == 2:
                    number_list.append(result)
            for rdr in rider_list:
                time_stamp = str(time.time())
                x1r, y1r, x2r, y2r, cnfr, clasr = rdr
                for hd in head_list:
                    x1h, y1h, x2h, y2h, cnfh, clash = hd
                    if inside_box([x1r,y1r,x2r,y2r], [x1h,y1h,x2h,y2h]): # if this head inside this rider bbox
                        try:
                            head_img = orifinal_frame[y1h:y2h, x1h:x2h]
                            helmet_present = img_classify(head_img)
                        except:
                            helmet_present[0] = None
                        if  helmet_present[0] == True: # if helmet present
                            frame = cv2.rectangle(frame, (x1h, y1h), (x2h, y2h), (0,255,0), 1)
                            frame = cv2.putText(frame, f'{round(helmet_present[1],1)}', (x1h, y1h+40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 1, cv2.LINE_AA)
                        elif helmet_present[0] == None: # Poor prediction
                            frame = cv2.rectangle(frame, (x1h, y1h), (x2h, y2h), (0, 255, 255), 1)
                            frame = cv2.putText(frame, f'{round(helmet_present[1],1)}', (x1h, y1h), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 1, cv2.LINE_AA)
                        elif helmet_present[0] == False: # if helmet absent 
                            frame = cv2.rectangle(frame, (x1h, y1h), (x2h, y2h), (0, 0, 255), 1)
                            frame = cv2.putText(frame, f'{round(helmet_present[1],1)}', (x1h, y1h+40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 1, cv2.LINE_AA)
                            try:
                                cv2.imwrite(f'riders_pictures/{time_stamp}.jpg', frame[y1r:y2r, x1r:x2r])
                            except:
                                print('could not save rider')
                            for num in number_list:
                                x1_num, y1_num, x2_num, y2_num, conf_num, clas_num = num
                                if inside_box([x1r,y1r,x2r,y2r], [x1_num, y1_num, x2_num, y2_num]):
                                    try:						
                                        num_img = orifinal_frame[y1_num:y2_num, x1_num:x2_num]
                                        a=time_stamp
                                        b=conf_num
                                        cv2.imwrite(f'number_plates/{a}_{b}.jpg', num_img)
                                    except:
                                        print('could not save number plate')
            
            if save_video: # save video
                out.write(frame)
            if save_img: #save img
                cv2.imwrite('saved_frame.jpg', frame)
            src_file = 'saved_frame.jpg'
            dst_folder = 'riders_pictures'
            dst_file = os.path.join(dst_folder, os.path.basename(src_file))

            shutil.copy(src_file, dst_file)
            if show_video: # show video
                frame = cv2.resize(frame, (900, 450))  # resizing to fit in screen
                cv2.imshow('Frame', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            break

    cap.release()
    cv2.destroyAllWindows()
    print('Execution completed')

    directory = "C:/Users/sanja/Downloads/motorcycle_license_plate/number_plates"
    image_files = glob.glob(directory + '/*.jpg')
    for image_path in image_files:
        img = cv2.imread(image_path)
        cv2.imshow('NUmber Plate', img)
        cv2.waitKey(3000)
        cv2.destroyAllWindows()

        resize_test_license_plate = cv2.resize(img, None, fx = 2, fy = 2,interpolation = cv2.INTER_CUBIC)
        grayscale_resize_test_license_plate = cv2.cvtColor(resize_test_license_plate, cv2.COLOR_BGR2GRAY)
        gaussian_blur_license_plate = cv2.GaussianBlur(grayscale_resize_test_license_plate, (5, 5), 0)
        text = pytesseract.image_to_string(gaussian_blur_license_plate)
        print(text)
        string = text
        text_new = string.replace('\n', '').replace('\r', '')
        dict={'* AP09.°CG 8847': 6301196260,'GWT2180':9014805519}
        for key, value in dict.items():
            if key==text_new:
                result1=value
                break
        result1="+91"+str(result1)
        current_time=datetime.now()
        new_time = current_time + timedelta(seconds=30)
        pywhatkit.sendwhatmsg(result1,"Stay Safe, Protect Your Head! Please Wear a Helmet While Driving",new_time.hour,new_time.minute+1)
        print("Done!!")
    





window = tk.Tk()
window.title("Automatic Helmet and Number plate detection")
window.geometry("800x600")  # Set window size
window.configure(bg="#ffffff")  # Set background color
bg= ImageTk.PhotoImage(file="./background.jpg")
#Create a canvas
canvas= tk.Canvas(window,width=1920, height=1080)
canvas.pack(expand=True)
#Add the image in the canvas
canvas.create_image(0,0,image=bg, anchor="nw")
# description = "Automatic Number Plate and Helmet Detection"
# canvas.create_text(400, 100, text=description, font=("Arial", 14), fill="black")


def upload_video():
    video_file = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4")])
    if video_file:
        process_video(video_file)
        

upload_button = tk.Button(window, text="UPLOAD VIDEO", command=upload_video)
button_window = canvas.create_window(950, 400, anchor="center", window=upload_button)

window.mainloop()
