# -*- coding: utf-8 -*-
"""
Created on Tue Apr 16 20:41:48 2024

@author: Jacob Heiser
"""
import sys
import pandas as pd
from PyQt5.QtWidgets import QApplication, QLineEdit, QPushButton, QTableWidget, QMainWindow, QFileDialog, QTableWidgetItem, QLabel, QListWidget
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import uic
from PyQt5 import QtCore
from course import course
from staff import staff
from overview import overview

#Notes
#Level 1 Dataframes collect the necessary raw information from Excel Sheets
#Level 2 Dataframes use level 1 in order to combine certain data together
#Level 3 Dataframe containing final information that is given back to the user

pd.set_option('display.max_rows', 40)
pd.set_option('display.max_columns', None)

def design(aarName, dnName, fsName):
    
    
    #create objects
    course_manip = course()
    staff_manip = staff()
    overview_manip = overview()
    
    #Create level 1 dataframes - Data given to us
    course_frame = pd.read_excel(dnName, usecols='A,B,C,D') #Code, Section, Name, Students
    staff_frame = pd.read_excel(aarName, usecols='C,D,E,H,M,S') #Name, ID, Title, Cass, Identifier, UPN
    schedule_frame = pd.read_excel(fsName, usecols='A, B, C, D, F, H') #ID, Name, UPN, Title, Code, Course Name
    
    
    # Main Task 1: Create level 2 Data frames - Organizing level 1 databases
    #1.1 - Create and Organize Courses
    print('Creating Course Info Frame')
    course_frame = course_manip.courseFrameAdjustment(course_frame)
    course_info_frame = course_manip.counter(course_frame, staff_frame)
    print('Course Info Frame - Created')
    print()
    
    #1.2 - Create and Organize Staff
    print('Creating Staff Info Frame')
    staff_info_frame = staff_manip.counter(staff_frame, schedule_frame)
    print('Staff Info Frame - Created')
    print()
    
    #1.3 Create dataframe of containing list of staff
    staff_manager_list = staff_manip.staffManager(staff_info_frame)
    print()
    
    
    #Main Task 2 - Assign courses and create Level 3 dataframe - Creating the Output        
    print('Assigning Courses')
    staff_schedules_frame = course_manip.assignment(course_info_frame, staff_info_frame, course_frame, staff_manager_list)
    print('Assigning Courses Completed')
    print()

    #Main Task 3 - Check Utilization report
    print('Creating Utilization Report')
    staff_utilization_report = staff_manip.utilization(staff_schedules_frame, staff_manager_list)
    print('Utilization Report Completed')
        
 
    #Main Taks 4 - Produce Overview report
    print('Creating Overview Report')
    overview_final_report = overview_manip.overview_report(staff_schedules_frame, staff_utilization_report, staff_info_frame)
    print('Overview Report Completed')


    staff_schedules_frame.sort_values(by=['Code'], ascending=False)
        
    
    #Create Excel Sheets
    staff_schedules_frame.to_excel('StaffSchedules.xlsx', sheet_name='sheet1', index=False)
    staff_utilization_report.to_excel('StaffUtilizationReport.xlsx', sheet_name='sheet2', index=False)
    overview_final_report.to_excel('OverviewReport.xlsx', sheet_name='sheet3', index=False)    
    
    return    

def applyUpdates(scheduleDF, aarEditorDF):
    copy = aarEditorDF.drop_duplicates('Unnamed: 18')
    
    print('Updating Schedule')
    #formating Schedule Report
    for i in scheduleDF.index:
        #Code Formatting
        word_list = str(scheduleDF.at[i, 'Class']).split()
        
        if str(scheduleDF.at[i, 'Section']) == '00':
            scheduleDF.at[i, 'Code'] = scheduleDF.at[i, 'Code'] + '-L'
        elif word_list[-1] == 'Lecture':
            scheduleDF.at[i, 'Code'] = scheduleDF.at[i, 'Code'] + '-L'
            
        elif word_list[-1] == 'Online':
            scheduleDF.at[i, 'Code'] = scheduleDF.at[i, 'Code'] + '-O'
        else:
            scheduleDF.at[i, 'Code'] = scheduleDF.at[i, 'Code'] + '-O'
            
    scheduleDF.to_excel('StaffSchedules.xlsx', sheet_name='sheet1', index=False)
    print('Updating Schedule - Completed')


    print('Updating Utilization')
    #Utilization Report
    staff_manip = staff()
    
    utilizationUpdate = staff_manip.utilizationUpdater(scheduleDF, copy)
    
    utilizationUpdate.to_excel('StaffUtilizationReport.xlsx', sheet_name='sheet2', index=False)
    print('Updating Utilization - Completed')
    
    
    print('Updating Overview')
    #Overview Report
    overview_manip = overview()
    
    overViewUpdated = overview_manip.overviewUpdater(scheduleDF, utilizationUpdate, copy)

    
    overViewUpdated.to_excel('OverviewReport.xlsx', sheet_name='sheet3', index=False)    
    print('Updating Overview - Completed')

            
    return
    
#User Interface
class mainUI(QMainWindow):
    def __init__(self):
        super(mainUI, self).__init__()
        
        #Load ui file - IMPORTANT!
        uic.loadUi("mainWindow.ui", self)
        
        self.setWindowIcon(QtGui.QIcon('logo.png'))
        self.setWindowTitle("Full Sail: Scheduler")
        self.setFixedSize(970, 480)
        
        #DESIGN TAB
        #define buttons
        self.btnCreate = self.findChild(QPushButton, "btnCreate")
        self.btnFileAAR = self.findChild(QPushButton, "btnFileAAR")
        self.btnFileDN = self.findChild(QPushButton, "btnFileDN")
        self.btnFileFS = self.findChild(QPushButton, "btnFileFS")
        
        
        self.btnFileAAREditor = self.findChild(QPushButton, "btnFileAAR_2")
        self.btnFileSchedule = self.findChild(QPushButton, "btnFileSchedule")
        self.btnFileUtilzation = self.findChild(QPushButton, "btnFileUtilization")
        self.btnEditor = self.findChild(QPushButton, "btnEditor")

        
        #Define line edits
        self.LineEditFileAAR = self.findChild(QLineEdit, "leAAR")
        self.LineEditFileDN = self.findChild(QLineEdit, "leDN")
        self.LineEditFileFS = self.findChild(QLineEdit, "leFS")
        
        self.LineEditFileAAREditor = self.findChild(QLineEdit, "leAAR2")
        self.LineEditFileSchedule = self.findChild(QLineEdit, "leScheduleReport")
        self.LineEditFileUtl = self.findChild(QLineEdit, "leUltReport")

        
        #Button events
        self.btnCreate.clicked.connect(self.designMaker)
        self.btnFileAAR.clicked.connect(self.openAARFile)
        self.btnFileDN.clicked.connect(self.openDNFile)
        self.btnFileFS.clicked.connect(self.openFSFile)
        
        
        self.btnFileAAREditor.clicked.connect(self.openAAREditorFile)
        self.btnFileSchedule.clicked.connect(self.openScheduleFile)
        self.btnFileUtilzation.clicked.connect(self.openUtlFile)
        self.btnEditor.clicked.connect(self.editorWindowOpen)

        
        #SCHEDULE TAB
        self.btnFindSchedule = self.findChild(QPushButton, "btnFindSchedule")
        self.btnUploadSchedule = self.findChild(QPushButton, "btnUploadSchedule")
        
        self.leName = self.findChild(QLineEdit, "leScheduleName")
        self.leCode = self.findChild(QLineEdit, "leScheduleCode")
        self.leTitle = self.findChild(QLineEdit, "leScheduleTitle")
        self.leUPN = self.findChild(QLineEdit, "leScheduleUPN")


        self.leScheduleFile = self.findChild(QLineEdit, "leScheduleFile")
        
        self.scheduleTable = self.findChild(QTableWidget, "tableView")
        
        #Events
        self.btnUploadSchedule.clicked.connect(self.uploadSchedule)
        self.btnFindSchedule.clicked.connect(self.findSchedule)



        #UTILZATION TAB
        self.btnFindUlt = self.findChild(QPushButton, "btnUltFind")
        self.btnUploadUlt = self.findChild(QPushButton, "btnUtlUpload")
        
        self.leUtlName = self.findChild(QLineEdit, "leUtlName")
        self.leUtlUPN = self.findChild(QLineEdit, "leUtlUPN")
        self.leUtlUtlization = self.findChild(QLineEdit, "leUtlUtlization")
        
        self.leUltizationFile = self.findChild(QLineEdit, "leUltFile")
        
        self.ultizationTable = self.findChild(QTableWidget, "tableUlt")
        
        #Events
        self.btnUploadUlt.clicked.connect(self.uploadUltization)
        self.btnFindUlt.clicked.connect(self.findUltization)
        
        
        #OVERVIEW TAB
        self.btnFindOverview = self.findChild(QPushButton, "btnOverFind")
        self.btnUploadOverview = self.findChild(QPushButton, "btnOverviewUpload")
        
        self.leOverCode = self.findChild(QLineEdit, "leOverCode")
        self.leOverUlt = self.findChild(QLineEdit, "leOverUlt")
        
        self.leOverviewFile = self.findChild(QLineEdit, "leOverview")
        
        self.overviewTable = self.findChild(QTableWidget, "tableOverview")
        
        #Events
        self.btnFindOverview.clicked.connect(self.findOverview)
        self.btnUploadOverview.clicked.connect(self.uploadOverview)

        #Show app
        self.show()
        
        
        
    #Button Event Create: Main program
    def designMaker(self):
        if self.LineEditFileAAR == "":
            print("ERROR")
            return
        
        elif self.LineEditFileDN == "":
            print("ERROR")
            return
        
        elif self.LineEditFileFS == "":
            print("ERROR")
            return
        else:
            
            aarName = self.LineEditFileAAR.text()
            dnName = self.LineEditFileDN.text()
            fsName = self.LineEditFileFS.text()
            
            design(aarName, dnName, fsName)
            
            
    #Buttons Functions
    #Design Functions
    def openAARFile(self):
        fname = QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*);;Excel Files (*.xlsx)")
        
        self.LineEditFileAAR.setText(fname[0])
        
    def openDNFile(self):
        fname = QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*);;Excel Files (*.xlsx)")
        
        self.LineEditFileDN.setText(fname[0])
        
    def openFSFile(self):
        fname = QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*);;Excel Files (*.xlsx)")
        
        self.LineEditFileFS.setText(fname[0])
     
    #Schedule Functions
    def uploadSchedule(self):
        fname = QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*);;Excel Files (*.xlsx)")

        self.leScheduleFile.setText(fname[0])
        
        file = self.leScheduleFile.text()
        
        df = pd.read_excel(file)
        
        if df.size == 0:
            return
        
        self.scheduleTable.setRowCount(df.shape[0])
        self.scheduleTable.setColumnCount(df.shape[1])
        self.scheduleTable.setHorizontalHeaderLabels(df.columns)
        
        for row in df.iterrows():
            values = row[1]  
            
            for col_index, value in enumerate(values):
                self.scheduleTable.setItem(row[0], col_index, QTableWidgetItem(str(value)))
                
                
    def findSchedule(self):
        nameTxt = self.leName.text()
        codeTxt = self.leCode.text()
        titleTxt = self.leTitle.text()
        upnTxt = self.leUPN.text()
        
        #reveals all rows at begining
        for row in range(self.scheduleTable.rowCount()):
            self.scheduleTable.showRow(row)

        
        for row in range(self.scheduleTable.rowCount()):
            name = self.scheduleTable.item(row, 4).text()
            code = self.scheduleTable.item(row, 0).text()
            title = self.scheduleTable.item(row, 6).text()
            UPN = self.scheduleTable.item(row, 5).text()

            #Checks to see if all fields are blank
            if nameTxt == "" and codeTxt == "" and titleTxt == "" and upnTxt == "":
                return
            
            
            #hides all rows that dont match filters
            #All fields are filled
            if nameTxt != "" and codeTxt != "" and titleTxt != "" and upnTxt != "":
                if name != nameTxt or code != codeTxt or title != titleTxt or UPN != upnTxt:
                    self.scheduleTable.hideRow(row)
                           
                    
            #3 fields are filled
            elif nameTxt == "" and codeTxt != "" and titleTxt != "" and upnTxt != "":
                if code != codeTxt or title != titleTxt or UPN != upnTxt:
                    self.scheduleTable.hideRow(row)                    
            elif nameTxt != "" and codeTxt == "" and titleTxt != "" and upnTxt != "":
                if name != nameTxt or title != titleTxt or UPN != upnTxt:
                    self.scheduleTable.hideRow(row)    
            elif nameTxt != "" and codeTxt != "" and titleTxt == "" and upnTxt != "":
                if code != codeTxt or name != nameTxt or UPN != upnTxt:
                    self.scheduleTable.hideRow(row)        
            elif nameTxt != "" and codeTxt != "" and titleTxt != "" and upnTxt == "":
                if code != codeTxt or title != titleTxt or name != nameTxt:
                    self.scheduleTable.hideRow(row)
                     
                
            #2 Fields are filled
            elif nameTxt != "" and codeTxt != "" and titleTxt == "" and upnTxt == "":
                if code != codeTxt or name != nameTxt:
                    self.scheduleTable.hideRow(row) 
            elif nameTxt != "" and codeTxt == "" and titleTxt != "" and upnTxt == "":
                if title != titleTxt or name != nameTxt:
                    self.scheduleTable.hideRow(row) 
            elif nameTxt != "" and codeTxt == "" and titleTxt == "" and upnTxt != "":
                if UPN != upnTxt or name != nameTxt:
                    self.scheduleTable.hideRow(row) 
                    
                    
            elif nameTxt == "" and codeTxt != "" and titleTxt != "" and upnTxt == "":
                if code != codeTxt or title != titleTxt:
                    self.scheduleTable.hideRow(row)       
            elif nameTxt == "" and codeTxt != "" and titleTxt == "" and upnTxt != "":
                if code != codeTxt or UPN != upnTxt:
                    self.scheduleTable.hideRow(row) 
                   
                    
            elif nameTxt == "" and codeTxt == "" and titleTxt != "" and upnTxt != "":
                if UPN != upnTxt or title != titleTxt:
                    self.scheduleTable.hideRow(row)       
                  
    
            #1 Field is filled
            elif nameTxt != "" and codeTxt == "" and titleTxt == "" and upnTxt == "":
                if name != nameTxt:
                    self.scheduleTable.hideRow(row) 
            elif nameTxt == "" and codeTxt != "" and titleTxt == "" and upnTxt == "":
                if code != codeTxt:
                    self.scheduleTable.hideRow(row)
            elif nameTxt == "" and codeTxt == "" and titleTxt != "" and upnTxt == "":
                if title != titleTxt:
                    self.scheduleTable.hideRow(row)
            elif nameTxt == "" and codeTxt == "" and titleTxt == "" and upnTxt != "":
                if UPN != upnTxt:
                    self.scheduleTable.hideRow(row) 
                
        
          
                
    #Utilzation Functions
    def uploadUltization(self):
        fname = QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*);;Excel Files (*.xlsx)")

        self.leUltizationFile.setText(fname[0])
        
        file = self.leUltizationFile.text()
        
        df = pd.read_excel(file)
        
        if df.size == 0:
            return
        
        self.ultizationTable.setRowCount(df.shape[0])
        self.ultizationTable.setColumnCount(df.shape[1])
        self.ultizationTable.setHorizontalHeaderLabels(df.columns)
        
        for row in df.iterrows():
            values = row[1]  
            
            for col_index, value in enumerate(values):
                self.ultizationTable.setItem(row[0], col_index, QTableWidgetItem(str(value))) 


    def findUltization(self):
        nameTxt = self.leUtlName.text()
        upnTxt = self.leUtlUPN.text()
        ultlizationTxt = self.leUtlUtlization.text()

        #reveals all rows at begining
        for row in range(self.ultizationTable.rowCount()):
            self.ultizationTable.showRow(row)

        
        for row in range(self.ultizationTable.rowCount()):
            name = self.ultizationTable.item(row, 0).text()
            upn = self.ultizationTable.item(row, 1).text()
            ultlization = self.ultizationTable.item(row, 4).text()
            
            #Checks to see if all fields are blank
            if nameTxt == "" and upnTxt == "" and ultlizationTxt == "":
                return
            
            
            #hides all rows that dont match filters
            #All fields are filled
            if nameTxt != "" and upnTxt != "" and ultlizationTxt != "":
                if name != nameTxt or upn != upnTxt or ultlization != ultlizationTxt:
                    self.ultizationTable.hideRow(row)
                
                    
            #2 Fields are filled
            if nameTxt != "" and upnTxt != "" and ultlizationTxt == "":
                if name != nameTxt or upn != upnTxt:
                    self.ultizationTable.hideRow(row)
            if nameTxt != "" and upnTxt == "" and ultlizationTxt != "":
                if name != nameTxt or ultlization != ultlizationTxt:
                    self.ultizationTable.hideRow(row)
            if nameTxt == "" and upnTxt != "" and ultlizationTxt != "":
                if upn != upnTxt or ultlization != ultlizationTxt:
                    self.ultizationTable.hideRow(row)
            
            
            #1 Field is filled
            if nameTxt != "" and upnTxt == "" and ultlizationTxt == "":
                if name != nameTxt:
                    self.ultizationTable.hideRow(row)
            if nameTxt == "" and upnTxt != "" and ultlizationTxt == "":
                if upn != upnTxt:
                    self.ultizationTable.hideRow(row)
            if nameTxt == "" and upnTxt == "" and ultlizationTxt != "":
                if ultlization != ultlizationTxt:
                    self.ultizationTable.hideRow(row)
     
                    
    #Overview Functions
    def findOverview(self):
        codeTxt = self.leOverCode.text()
        ultTxt = self.leOverUlt.text()
        
        
        #reveals all rows at begining
        for row in range(self.overviewTable.rowCount()):
            self.overviewTable.showRow(row)

        
        for row in range(self.overviewTable.rowCount()):
            code = self.overviewTable.item(row, 0).text()
            full = self.overviewTable.item(row, 1).text()
            over = self.overviewTable.item(row, 2).text()
            under = self.overviewTable.item(row, 3).text()
            notTeaching = self.overviewTable.item(row, 4).text()
            
            
            #If 2 Fields are filled
            if codeTxt != "" and ultTxt != "":
                if ultTxt == 'Over-Utilized':
                    if int(over) <= 0 or code != codeTxt:
                        self.overviewTable.hideRow(row)
                        
                elif ultTxt == 'Under-Utilized':
                    if int(under) <= 0 or code != codeTxt:
                        self.overviewTable.hideRow(row)
                        
                elif ultTxt == 'Fully Utilized':
                    if int(full) <= 0 or code != codeTxt:
                        self.overviewTable.hideRow(row)
                        
                elif ultTxt == 'Not Teaching':
                    if int(notTeaching) <= 0 or code != codeTxt:
                        self.overviewTable.hideRow(row)
                
                else:
                    self.overviewTable.hideRow(row)

            
            
            #If 1 Field is filled
            if codeTxt != "" and ultTxt == "":
                if code != codeTxt:
                    self.overviewTable.hideRow(row)
            
            if codeTxt == "" and ultTxt != "":
                if ultTxt == 'Over-Utilized':
                    if int(over) <= 0:
                        self.overviewTable.hideRow(row)
                        
                elif ultTxt == 'Under-Utilized':
                    if int(under) <= 0:
                        self.overviewTable.hideRow(row)
                        
                elif ultTxt == 'Fully Utilized':
                    if int(full) <= 0:
                        self.overviewTable.hideRow(row)
                        
                elif ultTxt == 'Not Teaching':
                    if int(notTeaching) <= 0:
                        self.overviewTable.hideRow(row)
                
                else:
                    self.overviewTable.hideRow(row)
    
    
    def uploadOverview(self):
        fname = QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*);;Excel Files (*.xlsx)")

        self.leOverviewFile.setText(fname[0])
        
        file = self.leOverviewFile.text()
        
        df = pd.read_excel(file)
        
        if df.size == 0:
            return
        
        self.overviewTable.setRowCount(df.shape[0])
        self.overviewTable.setColumnCount(df.shape[1])
        self.overviewTable.setHorizontalHeaderLabels(df.columns)
        
        for row in df.iterrows():
            values = row[1]  
            
            for col_index, value in enumerate(values):
                self.overviewTable.setItem(row[0], col_index, QTableWidgetItem(str(value))) 
    
       
    #OPENS scheduleUI Window             
    def editorWindowOpen(self):
        aarEditorName = self.LineEditFileAAREditor.text()
        scheduleName = self.LineEditFileSchedule.text()
        utlFile = self.LineEditFileUtl.text()
        
        if aarEditorName == '':
            print('Error: No ARR File')
            return
        if scheduleName == '':
            print('Error: No Schedule File')
            return
        if utlFile == '':
            print('Error: No Utilization File')
            return
        
        self.ui = scheduleUI(aarEditorName, scheduleName, utlFile)
        
        
        
        self.ui.show()
        
            
    def openAAREditorFile(self):
        fname = QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*);;Excel Files (*.xlsx)")
        
        self.LineEditFileAAREditor.setText(fname[0])
        
    def openScheduleFile(self):
        fname = QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*);;Excel Files (*.xlsx)")
        
        self.LineEditFileSchedule.setText(fname[0])
        
    def openUtlFile(self):
        fname = QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*);;Excel Files (*.xlsx)")
        
        self.LineEditFileUtl.setText(fname[0])
        
    
    
    
    
#User Interface - 2nd window Schedule Editor
class scheduleUI(QMainWindow):    
    def __init__(self, aarEditorName, scheduleName, utlFile):
        super(scheduleUI, self).__init__()
        #Load ui file - IMPORTANT!
        uic.loadUi("scheduleEditorWindow.ui", self)
        
        self.setWindowIcon(QtGui.QIcon('logo.png'))
        self.setWindowTitle("Full Sail: Editor")
        
        self.move(80, 20)
        self.setFixedSize(970, 480)
        
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        
        
        #List Table
        self.lCourses = self.findChild(QListWidget, 'lCourses')
        
        #Tables
        self.tbSchedule = self.findChild(QTableWidget, 'tbSchedule')
        self.tbStaff = self.findChild(QTableWidget, 'tbStaff')
        
        #Buttons
        self.btnAdd = self.findChild(QPushButton, "btnAdd")
        self.btnRemove = self.findChild(QPushButton, "btnRemove")
        self.btnApply = self.findChild(QPushButton, "btnApply")
        self.btnBack = self.findChild(QPushButton, "btnBack")
        
        #Labels
        self.lbCode = self.findChild(QLabel, "lblCode")
        self.lbSection = self.findChild(QLabel, "lblSection")
        self.lbStaff = self.findChild(QLabel, "lblStaff")
        self.lbUPN = self.findChild(QLabel, "lblUPN")
        
        #Databases
        self.aarEditorDF = pd.read_excel(aarEditorName)
        self.scheduleDF = pd.read_excel(scheduleName)
        self.utlFileDF = pd.read_excel(utlFile)
        
        
        #Edit codes in AAR File
        for i in self.aarEditorDF.index:
            data = self.aarEditorDF.at[i, 'Unnamed: 7'] #grabs Academic Appointment Title
            data = data.split()[0] #Grabs the Code, leaving behind description
            self.aarEditorDF.at[i, 'Unnamed: 7'] = data
            
        
        #Fill list with entries and then Schedule Table        
        for i in self.scheduleDF.index:
            code = str(self.scheduleDF.at[i, 'Code'])
            code = "".join(code.split())
            code = code[:-2] 
            
            self.scheduleDF.at[i, 'Code'] = code
            
        self.scheduleDFCopy = self.scheduleDF.drop_duplicates('Code')

        self.lCourses.insertItem(i, '')

        for i in self.scheduleDFCopy.index:
            self.lCourses.insertItem(i + 1, self.scheduleDFCopy.at[i, 'Code'])
         
        
        #Fill the Schedule table        
        if self.scheduleDF.size == 0:
            return
        
        self.tbSchedule.setRowCount(self.scheduleDF.shape[0])
        self.tbSchedule.setColumnCount(self.scheduleDF.shape[1])
        self.tbSchedule.setHorizontalHeaderLabels(self.scheduleDF.columns)
        
        for row in self.scheduleDF.iterrows():
            values = row[1]  
            
            for col_index, value in enumerate(values):
                self.tbSchedule.setItem(row[0], col_index, QTableWidgetItem(str(value)))
            
        self.tbSchedule.hideColumn(7)
        self.tbSchedule.hideColumn(8)
        
        
        #Fill the Staff table        
        if self.utlFileDF.size == 0:
            return
        
        self.tbStaff.setRowCount(self.utlFileDF.shape[0])
        self.tbStaff.setColumnCount(self.utlFileDF.shape[1])
        self.tbStaff.setHorizontalHeaderLabels(self.utlFileDF.columns)
        
        for row in self.utlFileDF.iterrows():
            values = row[1]  
            
            for col_index, value in enumerate(values):
                self.tbStaff.setItem(row[0], col_index, QTableWidgetItem(str(value)))
                
        self.tbStaff.hideColumn(1)
        self.tbStaff.hideColumn(2)
        self.tbStaff.hideColumn(3)
       
        
        #List Events
        self.lCourses.itemActivated.connect(self.itemActivated_event)
        
        #Table Events
        self.tbSchedule.cellClicked.connect(self.SchdeuleSelected)
        self.tbStaff.cellClicked.connect(self.StaffSelected)
        
        #Button Events
        self.btnAdd.clicked.connect(self.addStaff)
        self.btnRemove.clicked.connect(self.removeStaff)
        self.btnApply.clicked.connect(self.applyChanges)
        self.btnBack.clicked.connect(self.backMethod)


        
        self.show()


    def itemActivated_event(self, item):
        currentItem = item.text()
        
        #hide all rows if there is a current item
        if currentItem != '':
            for row in range(self.tbStaff.rowCount()):
                self.tbStaff.hideRow(row)
        else:
            for row in range(self.tbStaff.rowCount()):
                self.tbStaff.showRow(row)
        
        
        #Finds Matching courses in Schedule
        #reveals all rows at begining
        for row in range(self.tbSchedule.rowCount()):
            self.tbSchedule.showRow(row)

        
        for row in range(self.tbSchedule.rowCount()):
            code = self.tbSchedule.item(row, 0).text()

            if currentItem == '':
                return
                
            if currentItem != code:
                self.tbSchedule.hideRow(row)
                
                
            
        #Show all matching staff
        for i in self.aarEditorDF.index:
            if currentItem == self.aarEditorDF.at[i, 'Unnamed: 7']:
                aarUPN = self.aarEditorDF.at[i, 'Unnamed: 18']
                
                for row in range(self.tbStaff.rowCount()):
                    upn = self.tbStaff.item(row, 1).text()
                    if upn == aarUPN:
                        self.tbStaff.showRow(row)



    def SchdeuleSelected(self, row):
        self.lbCode.setText('Code:' + self.tbSchedule.item(row, 0).text())
        self.lbSection.setText('Section:' + self.tbSchedule.item(row, 1).text())
        
    def StaffSelected(self, row):
        self.lbStaff.setText('Staff:' + self.tbStaff.item(row, 0).text())
        self.lbUPN.setText('UPN:' + self.tbStaff.item(row, 1).text())
        
    #Adds Staff from selected course row and Staff Row   
    def addStaff(self):
        code = self.lbCode.text()
        section = self.lbSection.text()
        staff = self.lbStaff.text()
        upn = self.lbUPN.text()
        
        if staff == 'Staff:':
            print('Error: No Staff')
            return
        
        #Change in Database
        for i in self.scheduleDF.index:
            if code == 'Code:' + str(self.scheduleDF.at[i, 'Code']):
                if section == 'Section:' + self.scheduleDF.at[i, 'Section']:
                    self.scheduleDF.at[i, 'Staff'] = staff[6:]
                    self.scheduleDF.at[i, 'UPN'] = upn[4:]
                    
                    for j in self.aarEditorDF.index:
                        if self.scheduleDF.at[i, 'UPN'] == self.aarEditorDF.at[j, 'Unnamed: 18']:
                            emp_title = self.aarEditorDF.at[j, 'Unnamed: 4']
                            if emp_title == 'Course Director-SE':
                                emp_title = 'CD'
                            elif emp_title == 'Department Chair':
                                emp_title = 'DC'
                            elif emp_title == 'Associate Course Director-SE':
                                emp_title = 'ACD'
                            elif emp_title == 'Adjunct':
                                emp_title = 'ADJ'
                                
                            self.scheduleDF.at[i, 'Title'] = emp_title  
                            
        #Change in Table
        for row in range(self.tbStaff.rowCount()):
            if code == 'Code:' + self.tbSchedule.item(row, 0).text() and section == 'Section:' + self.tbSchedule.item(row, 1).text():
                self.tbSchedule.item(row, 4).setText(staff[6:])
                self.tbSchedule.item(row, 5).setText(upn[4:])
                self.tbSchedule.item(row, 6).setText(emp_title)
        return
              
    #Removes Staff from selected course row
    def removeStaff(self):
        code = self.lbCode.text()
        section = self.lbSection.text()
        
        
        #Change in Database
        for i in self.scheduleDF.index:
            if code == 'Code:' + str(self.scheduleDF.at[i, 'Code']):
                if section == 'Section:' + self.scheduleDF.at[i, 'Section']:
                    self.scheduleDF.at[i, 'Staff'] = 'NA'
                    self.scheduleDF.at[i, 'UPN'] = 'NA'
                    self.scheduleDF.at[i, 'Title'] = 'NA'
        
        #Change in Table
        for row in range(self.tbStaff.rowCount()):
            if code == 'Code:' + self.tbSchedule.item(row, 0).text() and section == 'Section:' + self.tbSchedule.item(row, 1).text():
                self.tbSchedule.item(row, 4).setText('NA')
                self.tbSchedule.item(row, 5).setText('NA')
                self.tbSchedule.item(row, 6).setText('NA')
                
        return
                
    
    def applyChanges(self):
        applyUpdates(self.scheduleDF, self.aarEditorDF)
        
        self.close()

        return
                
    
    def backMethod(self):
        self.close()
        return
                

#Create application                   
app = QApplication(sys.argv)

UIMainWindow = mainUI()


app.exec_()