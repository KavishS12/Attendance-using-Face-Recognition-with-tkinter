import sqlite3

conn = sqlite3.connect('attendance.db')

c = conn.cursor()

c.execute("""create table students_info (
            reg_no INTEGER PRIMARY KEY,
            name VARCHAR(20),
            section CHAR(1),
            semester INTEGER,
            branch VARCHAR(30)
)""")

c.execute("""create table dbs(
          reg_no INTEGER PRIMARY KEY,
          FOREIGN KEY (reg_no) REFERENCES students_info(reg_no)
)""")

c.execute("""create table maths(
          reg_no INTEGER PRIMARY KEY,
          FOREIGN KEY (reg_no) REFERENCES students_info(reg_no)
)""")

c.execute("""create table os(
          reg_no INTEGER PRIMARY KEY,
          FOREIGN KEY (reg_no) REFERENCES students_info(reg_no)
)""")

c.execute("""CREATE TABLE attendance_record (
            reg_no INTEGER PRIMARY KEY,
            dbs_present INTEGER default 0,
            dbs_total INTEGER default 0,
            maths_present INTEGER default 0,
            maths_total INTEGER default 0,
            os_present INTEGER default 0,
            os_total INTEGER default 0,
            FOREIGN KEY (reg_no) REFERENCES students_info(reg_no)
)""")

c.execute("insert into students_info values(1234,'Kavish','B',4,'AIML')")
c.execute("insert into students_info values(5678,'Kabir','B',4,'AIML')")
c.execute("insert into students_info values(4832,'DwayneJohnson','A',5,'CSE')")
c.execute("insert into students_info values(8556,'PaulWalker','A',5,'AIML')")
c.execute("insert into students_info values(1546,'RyanGosling','C',4,'CSE')")
c.execute("insert into students_info values(2348,'RyanReynolds','B',6,'CSE')")
c.execute("insert into students_info values(7852,'VinDiesel','A',4,'AIML')")

c.execute("insert into attendance_record(reg_no) values(1234)")
c.execute("insert into attendance_record(reg_no) values(5678)")
c.execute("insert into attendance_record(reg_no) values(4832)")
c.execute("insert into attendance_record(reg_no) values(8556)")
c.execute("insert into attendance_record(reg_no) values(1546)")
c.execute("insert into attendance_record(reg_no) values(2348)")
c.execute("insert into attendance_record(reg_no) values(7852)")

c.execute("insert into dbs(reg_no) values(1234)")
c.execute("insert into dbs(reg_no) values(5678)")
c.execute("insert into dbs(reg_no) values(4832)")
c.execute("insert into dbs(reg_no) values(8556)")
c.execute("insert into dbs(reg_no) values(1546)")
c.execute("insert into dbs(reg_no) values(2348)")
c.execute("insert into dbs(reg_no) values(7852)")

c.execute("insert into maths(reg_no) values(1234)")
c.execute("insert into maths(reg_no) values(5678)")
c.execute("insert into maths(reg_no) values(4832)")
c.execute("insert into maths(reg_no) values(8556)")
c.execute("insert into maths(reg_no) values(1546)")
c.execute("insert into maths(reg_no) values(2348)")
c.execute("insert into maths(reg_no) values(7852)")

c.execute("insert into os(reg_no) values(1234)")
c.execute("insert into os(reg_no) values(5678)")
c.execute("insert into os(reg_no) values(4832)")
c.execute("insert into os(reg_no) values(8556)")
c.execute("insert into os(reg_no) values(1546)")
c.execute("insert into os(reg_no) values(2348)")
c.execute("insert into os(reg_no) values(7852)")

#for loop to insert values directly for each subject table
"""
reg_nos = [1234, 5678, 4832, 8556, 1546, 2348, 7852]
subjects = ['dbs', 'maths', 'os']
for subject in subjects:
    for reg_no in reg_nos:
        c.execute(f"INSERT INTO {subject} (reg_no) VALUES (?)", (reg_no,))
"""

c.execute('''CREATE TRIGGER update_dbs_record 
             BEFORE UPDATE ON dbs
             BEGIN
                 UPDATE attendance_record
                 SET  dbs_present = dbs_present + 1
                 WHERE reg_no = NEW.reg_no;
             END;''')

c.execute('''CREATE TRIGGER update_os_record 
             BEFORE UPDATE ON os
             BEGIN
                 UPDATE attendance_record
                 SET  os_present = os_present + 1
                 WHERE reg_no = NEW.reg_no;
             END;''')

c.execute('''CREATE TRIGGER update_maths_record 
             BEFORE UPDATE ON maths
             BEGIN
                 UPDATE attendance_record
                 SET  maths_present = maths_present + 1
                 WHERE reg_no = NEW.reg_no;
             END;''')

conn.commit()

conn.close()

