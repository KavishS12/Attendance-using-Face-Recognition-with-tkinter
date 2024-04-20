import cv2 as cv
import numpy as np
import pandas as pd
import face_recognition
import os
import sqlite3
from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk

path = "individuals"
images = []
students = []
subjects = ['dbs','maths','os']
lst = os.listdir(path)
for img in lst:
    currImg = cv.imread(f'{path}/{img}')
    images.append(currImg)
    students.append(os.path.splitext(img)[0])

print("Name of individuals : " + ",".join(students))

def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList

conn = sqlite3.connect('attendance.db')
c = conn.cursor()

def markAttendance(subject,reg_no, date):
    try:
        sql_query = f"UPDATE {subject} SET {date} = 1 WHERE reg_no = ?"
        c.execute(sql_query, (reg_no,))
        conn.commit()
        print("Attendance marked successfully.")
    except sqlite3.Error as e:
        print("Error marking attendance:", e)

encodeListKnown = findEncodings(images)
print("Encoding done")

stopped = False

def hide_widgets():
    student_info_frame.pack_forget()
    subj_attendance_frame.pack_forget()
    subj_netattendance_frame.pack_forget()
    student_attendance_frame.pack_forget()
def show_widgets():
    student_info_frame.pack(pady=(0, pad_y))
    subj_attendance_frame.pack(pady=(0, pad_y))
    subj_netattendance_frame.pack(pady=(0, pad_y))
    student_attendance_frame.pack(pady=(0, pad_y))

def capture_attendance():
    if hasattr(display_attendance, 'text_widget') and display_attendance.text_widget:
        display_attendance.text_widget.pack_forget()
    if hasattr(stinfo_display, 'text_widget') and stinfo_display.text_widget:
        stinfo_display.text_widget.pack_forget()
    if hasattr(display_netattendance, 'text_widget') and display_netattendance.text_widget:
        display_netattendance.text_widget.pack_forget()
    if hasattr(display_studentattendance, 'text_widget') and display_studentattendance.text_widget:
        display_studentattendance.text_widget.pack_forget()
    hide_widgets()
    marked = set()
    date = date_entry.get()
    subject = subject_entry.get()
    if date == '':
        messagebox.showerror("Error", "Enter the date please.")
    elif subject.lower() not in subjects:
        messagebox.showerror("Error", "Enter a valid subject.")
    else:
        date = 'date_' + date[0:2] + '_' + date[2:4]
        subj_tot = subject + '_total'
        c.execute(f"ALTER table {subject} ADD COLUMN {date} INTEGER default 0 CHECK ({date} IN (0, 1));")
        c.execute(f"UPDATE attendance_record SET {subj_tot} = {subj_tot} + 1;")
        cap = cv.VideoCapture(0)

        def video_loop():
            global stopped  # Declare stopped as a global variable
            success, img = cap.read()
            if success and not stopped:
                img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
                imgSmall = cv.resize(img, (0, 0), None, 0.25, 0.25)
                imgSmall = cv.cvtColor(imgSmall, cv.COLOR_BGR2RGB)
                facesCurrFrame = face_recognition.face_locations(imgSmall)
                encodeCurrFrame = face_recognition.face_encodings(imgSmall)

                for encodeFace, faceloc in zip(encodeCurrFrame, facesCurrFrame):
                    matches = face_recognition.compare_faces(encodeListKnown, encodeFace, tolerance=0.5)
                    face_dist = face_recognition.face_distance(encodeListKnown, encodeFace)
                    matchIndex = np.argmin(face_dist)

                    if matches[matchIndex]:
                        reg_no = students[matchIndex].upper()
                        print(reg_no)
                        y1, x2, y2, x1 = faceloc
                        y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                        cv.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), thickness=2)
                        cv.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv.FILLED)
                        cv.putText(img, reg_no, (x1 + 6, y2 - 6), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
                        if reg_no not in marked:
                            markAttendance(subject,reg_no, date)
                            marked.add(reg_no)

                img = Image.fromarray(img)
                img = ImageTk.PhotoImage(image=img)
                canvas.create_image(0, 0, anchor=NW, image=img)
                canvas.img = img
                root.update()

            if not stopped:
                canvas.pack(pady=(0, pad_y))  # Show the canvas
                canvas.after(10, video_loop)
            else:
                canvas.pack_forget()  # Hide the canvas
                cap.release()
                cv.destroyAllWindows()

        global stopped
        stopped = False
        video_loop()

def stop_capture():
    show_widgets()
    global stopped
    stopped = True
    canvas.delete("all")

def display_attendance(subject):
    if hasattr(stinfo_display, 'text_widget') and stinfo_display.text_widget:
        stinfo_display.text_widget.pack_forget()
    if hasattr(display_netattendance, 'text_widget') and display_netattendance.text_widget:
        display_netattendance.text_widget.pack_forget()
    if hasattr(display_studentattendance, 'text_widget') and display_studentattendance.text_widget:
        display_studentattendance.text_widget.pack_forget()
    if subject.lower() not in subjects:
        messagebox.showerror("Error", "Enter a valid subject.")
    c.execute(f"SELECT * FROM {subject};")
    data = c.fetchall()
    column_names = [description[0] for description in c.description]
    df = pd.DataFrame(data, columns=column_names)
    num_rows, num_cols = df.shape
    if hasattr(display_attendance, 'text_widget') and display_attendance.text_widget:
        display_attendance.text_widget.pack_forget()
    text_widget = Text(root, height=num_rows + 2, width=num_cols * 15)
    text_widget.insert(END, df.to_string())
    text_widget.pack(pady=(0, pad_y))
    display_attendance.text_widget = text_widget

def display_netattendance(subject):
    if hasattr(stinfo_display, 'text_widget') and stinfo_display.text_widget:
        stinfo_display.text_widget.pack_forget()
    if hasattr(display_attendance, 'text_widget') and display_attendance.text_widget:
        display_attendance.text_widget.pack_forget()
    if hasattr(display_studentattendance, 'text_widget') and display_studentattendance.text_widget:
        display_studentattendance.text_widget.pack_forget()
    if subject.lower() not in subjects:
        messagebox.showerror("Error", "Enter a valid subject.")
    if subject.lower() == 'dbs':
        c.execute("SELECT students_info.reg_no, students_info.name, attendance_record.dbs_present AS present,attendance_record.dbs_total as total,(CAST(attendance_record.dbs_present AS FLOAT) / attendance_record.dbs_total) * 100 AS percentage FROM students_info JOIN attendance_record ON students_info.reg_no = attendance_record.reg_no;")
    if subject.lower() == 'os':
        c.execute("SELECT students_info.reg_no, students_info.name, attendance_record.os_present AS present,attendance_record.os_total as total,(CAST(attendance_record.os_present AS FLOAT) / attendance_record.os_total) * 100 AS percentage FROM students_info JOIN attendance_record ON students_info.reg_no = attendance_record.reg_no;")
    if subject.lower() == 'maths':
        c.execute("SELECT students_info.reg_no, students_info.name, attendance_record.maths_present AS present,attendance_record.maths_total as total,(CAST(attendance_record.maths_present AS FLOAT) / attendance_record.maths_total) * 100 AS percentage FROM students_info JOIN attendance_record ON students_info.reg_no = attendance_record.reg_no;")
    data = c.fetchall()
    column_names = [description[0] for description in c.description]
    df = pd.DataFrame(data, columns=column_names)
    num_rows, num_cols = df.shape
    if hasattr(display_netattendance, 'text_widget') and display_netattendance.text_widget:
        display_netattendance.text_widget.pack_forget()
    text_widget = Text(root, height=num_rows + 2, width=num_cols * 15)
    text_widget.insert(END, df.to_string())
    text_widget.pack(pady=(0, pad_y))
    display_netattendance.text_widget = text_widget

def display_sortednetattendance(subject):
    if hasattr(stinfo_display, 'text_widget') and stinfo_display.text_widget:
        stinfo_display.text_widget.pack_forget()
    if hasattr(display_attendance, 'text_widget') and display_attendance.text_widget:
        display_attendance.text_widget.pack_forget()
    if hasattr(display_studentattendance, 'text_widget') and display_studentattendance.text_widget:
        display_studentattendance.text_widget.pack_forget()
    if subject.lower() not in subjects:
        messagebox.showerror("Error", "Enter a valid subject.")
    if subject.lower() == 'dbs':
        c.execute("SELECT students_info.reg_no, students_info.name, attendance_record.dbs_present AS present,attendance_record.dbs_total as total,(CAST(attendance_record.dbs_present AS FLOAT) / attendance_record.dbs_total) * 100 AS percentage FROM students_info JOIN attendance_record ON students_info.reg_no = attendance_record.reg_no where percentage<75;")
    if subject.lower() == 'os':
        c.execute("SELECT students_info.reg_no, students_info.name, attendance_record.os_present AS present,attendance_record.os_total as total,(CAST(attendance_record.os_present AS FLOAT) / attendance_record.os_total) * 100 AS percentage FROM students_info JOIN attendance_record ON students_info.reg_no = attendance_record.reg_no where percentage<75;")
    if subject.lower() == 'maths':
        c.execute("SELECT students_info.reg_no, students_info.name, attendance_record.maths_present AS present,attendance_record.maths_total as total,(CAST(attendance_record.maths_present AS FLOAT) / attendance_record.maths_total) * 100 AS percentage FROM students_info JOIN attendance_record ON students_info.reg_no = attendance_record.reg_no where percentage<75;")
    data = c.fetchall()
    column_names = [description[0] for description in c.description]
    df = pd.DataFrame(data, columns=column_names)
    num_rows, num_cols = df.shape
    if hasattr(display_netattendance, 'text_widget') and display_netattendance.text_widget:
        display_netattendance.text_widget.pack_forget()
    text_widget = Text(root, height=num_rows + 2, width=num_cols * 15)
    text_widget.insert(END, df.to_string())
    text_widget.pack(pady=(0, pad_y))
    display_netattendance.text_widget = text_widget

def display_studentattendance(reg_no):
    if hasattr(stinfo_display, 'text_widget') and stinfo_display.text_widget:
        stinfo_display.text_widget.pack_forget()
    if hasattr(display_attendance, 'text_widget') and display_attendance.text_widget:
        display_attendance.text_widget.pack_forget()
    if hasattr(display_netattendance, 'text_widget') and display_netattendance.text_widget:
        display_netattendance.text_widget.pack_forget()
    if reg_no not in students:
        messagebox.showerror("Error", "Enter a valid registration number.")
    c.execute("""SELECT 
                    (CAST(dbs_present AS FLOAT) / dbs_total) * 100 AS DBS,
                    (CAST(maths_present AS FLOAT) / maths_total) * 100 AS Maths,
                    (CAST(os_present AS FLOAT) / os_total) * 100 AS OS
                FROM attendance_record WHERE reg_no = ?""", (reg_no,))
    data = c.fetchall()
    column_names = [description[0] for description in c.description]
    df = pd.DataFrame(data, columns=column_names)
    df = df.T
    num_rows, num_cols = df.shape
    if hasattr(display_studentattendance, 'text_widget') and display_studentattendance.text_widget:
        display_studentattendance.text_widget.pack_forget()
    text_widget = Text(root, height=num_rows + 2, width=num_cols * 15)
    text_widget.insert(END, df.to_string())
    text_widget.pack(pady=(0, pad_y))
    display_studentattendance.text_widget = text_widget

def stinfo_display():
    if hasattr(display_attendance, 'text_widget') and display_attendance.text_widget:
        display_attendance.text_widget.pack_forget()
    if hasattr(display_netattendance, 'text_widget') and display_netattendance.text_widget:
        display_netattendance.text_widget.pack_forget()
    if hasattr(display_studentattendance, 'text_widget') and display_studentattendance.text_widget:
        display_studentattendance.text_widget.pack_forget()
    c.execute("SELECT * FROM students_info;")
    data = c.fetchall()
    column_names = [description[0] for description in c.description]
    df = pd.DataFrame(data, columns=column_names)
    
    num_rows, num_cols = df.shape
    if hasattr(stinfo_display, 'text_widget') and stinfo_display.text_widget:
        stinfo_display.text_widget.pack_forget()
    text_widget = Text(root, height=num_rows + 2, width=num_cols * 15)
    text_widget.insert(END, df.to_string())
    text_widget.pack(pady=(0, pad_y))
    stinfo_display.text_widget = text_widget

root = Tk()
root.title("Attendance System")
root.configure(bg='black')
width = root.winfo_screenwidth() 
height = root.winfo_screenheight()  
root.geometry("%dx%d+0+0" % (width, height))

pad_y = 30
pad_x = 40

widgets = []

date_frame = Frame(root, bg='black')
date_frame.pack(pady=(10, pad_y))
date_label = Label(date_frame, text="Date:", font=('Arial', 16), bg='black', fg='white')
date_label.pack(side='left', padx=(0, 10))
date_entry = Entry(date_frame, font=('Arial', 16))
date_entry.pack(side='left', padx=(0, 10))
widgets.extend([date_frame, date_label, date_entry])

subject_frame = Frame(root, bg='black')
subject_frame.pack(pady=(0, pad_y))
subject_label = Label(subject_frame, text="Subject:", font=('Arial', 16), bg='black', fg='white')
subject_label.pack(side='left', padx=(0, 10))
subject_entry = Entry(subject_frame, font=('Arial', 16))
subject_entry.pack(side='left', padx=(0, 10))
widgets.extend([subject_frame, subject_label, subject_entry])

button_frame = Frame(root, bg='black')
button_frame.pack(pady=(0, pad_y))
capture_button = Button(button_frame, text="Capture Attendance", command=capture_attendance, width=20,font=('Arial', 12))
capture_button.pack(side=LEFT, padx=(0, 10))
stop_button = Button(button_frame, text="Stop Capturing", command=stop_capture, width=20,font=('Arial', 12))
stop_button.pack(side=LEFT, padx=(10, 0))
widgets.extend([button_frame, capture_button, stop_button])

canvas = Canvas(root, width=640, height=480)

student_info_frame = Frame(root, bg='black')
student_info_frame.pack(pady=(0, pad_y))
student_info_label = Label(student_info_frame, text="Students data :", font=('Arial', 16), bg='black', fg='white')
student_info_label.pack(side='left', padx=(0, 10))
stinfo_display_button = Button(student_info_frame, text="Display:", 
                        command=stinfo_display, font=('Arial', 12))
stinfo_display_button.pack(side='left')
widgets.extend([student_info_frame, student_info_label, stinfo_display_button])

subj_attendance_frame = Frame(root, bg='black')
subj_attendance_frame.pack(pady=(0, pad_y))
subj_attendance_label = Label(subj_attendance_frame, 
                            text="Enter subject for attendance record:", font=('Arial', 16), bg='black', fg='white')
subj_attendance_label.pack(side='left', padx=(0, 10))
subj_attendance_entry = Entry(subj_attendance_frame, font=('Arial', 16))
subj_attendance_entry.pack(side='left', padx=(0, 10))
display_button = Button(subj_attendance_frame, text="Display Attendance", 
                        command=lambda: display_attendance(subj_attendance_entry.get()), font=('Arial', 12))
display_button.pack(side='left')
widgets.extend([subj_attendance_frame, subj_attendance_label, subj_attendance_entry, display_button])

subj_netattendance_frame = Frame(root, bg='black')
subj_netattendance_frame.pack(pady=(0, pad_y))
subj_netattendance_label = Label(subj_netattendance_frame, 
                            text="Enter subject to view net attendance(with %):", font=('Arial', 16), bg='black', fg='white')
subj_netattendance_label.pack(side='left', padx=(0, 10))
subj_netattendance_entry = Entry(subj_netattendance_frame, font=('Arial', 16))
subj_netattendance_entry.pack(side='left', padx=(0, 10))
display_button = Button(subj_netattendance_frame, text="Display Net Attendance", 
                        command=lambda: display_netattendance(subj_netattendance_entry.get()), font=('Arial', 12))
display_button.pack(side='left')
sorted_display_button = Button(subj_netattendance_frame, text="< 75%", 
                        command=lambda: display_sortednetattendance(subj_netattendance_entry.get()), font=('Arial', 12))
sorted_display_button.pack(side='left')
widgets.extend([subj_netattendance_frame, subj_netattendance_label, subj_netattendance_entry, display_button,sorted_display_button])

student_attendance_frame = Frame(root, bg='black')
student_attendance_frame.pack(pady=(0, pad_y))
student_attendance_label = Label(student_attendance_frame, 
                            text="Enter student registration number to view attendance:", font=('Arial', 16), bg='black', fg='white')
student_attendance_label.pack(side='left', padx=(0, 10))
student_attendance_entry = Entry(student_attendance_frame, font=('Arial', 16))
student_attendance_entry.pack(side='left', padx=(0, 10))
display_button = Button(student_attendance_frame, text="Display Student Attendance", 
                        command=lambda: display_studentattendance(student_attendance_entry.get()), font=('Arial', 12))
display_button.pack(side='left')
widgets.extend([student_attendance_frame, student_attendance_label, student_attendance_entry, display_button])

root.mainloop()

conn.close()
