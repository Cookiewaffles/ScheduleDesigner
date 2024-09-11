# -*- coding: utf-8 -*-
"""
Created on Wed Apr 17 19:44:31 2024

@author: Jacob Heiser
"""

import pandas as pd
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

class staff:
    #collect basic info of the various courses - One of the MOST IMPORTANT functions
    def counter(s, staff_df, schedule_df):
        #Staff_df: Name, ID, Title, Cass, Identifier, UPN
        #schdule_df: ID, Name, UPN, Title, Code, Course Name
        staff_info = pd.DataFrame([])
        staff_List = []
        
        name = ''
        emp_ID = ''
        class_code = ''
        emp_title = ''
        emp_identify = ''
        emp_level = ''
        emp_UPN = ''
        
        #Loop through each course Staff can teach
        for i in staff_df.index:
            if i != 0:
                data = staff_df.at[i, 'Unnamed: 7'] #grabs Academic Appointment Title
            
                data = data.split()[0] #Grabs the Code, leaving behind description
            
                #Assign Variables
                name = staff_df.at[i, 'Unnamed: 2']
                emp_ID = staff_df.at[i, 'Unnamed: 3']
                emp_UPN = staff_df.at[i, 'Unnamed: 18']
                class_code = data
            
                #Shorten Title
                emp_title = staff_df.at[i, 'Unnamed: 4']
                if emp_title == 'Course Director-SE':
                    emp_title = 'CD'
                elif emp_title == 'Department Chair':
                    emp_title = 'DC'
                elif emp_title == 'Associate Course Director-SE':
                    emp_title = 'ACD'
                elif emp_title == 'Adjunct':
                    emp_title = 'ADJ'
            
            
                emp_identify = staff_df.at[i, 'Unnamed: 12']
            
                #Defines level of staff base on Identifer and Last year Schedule
                if emp_identify == '3 - Adjunct':
                    #loops to see if they taught this previous year
                    for j in schedule_df.index:
                        if data == schedule_df.at[j, 'Code'] and emp_UPN == schedule_df.at[j, 'UPN']:
                            emp_level = 'level 2'
                            break
                        else:
                            emp_level = 'level 3'
                        
                elif emp_identify == '1 - Primary':
                    emp_level = 'level 1'
                
                
                #add to dataframe
                staff_List.append([name, emp_ID, class_code, emp_title, emp_level, emp_UPN])
        
        staff_info = pd.DataFrame(staff_List, columns=['Name', 'ID', 'Code', 'Title', 'Level', 'UPN'])
        return staff_info
    
    #A list of each Staff member
    def staffManager(s, staff_df):
        staff_list = []
        staff_df.drop_duplicates('Name')
        
        for i in staff_df.index:
            name = staff_df.at[i, 'Name']
            upn = staff_df.at[i, 'UPN']
            title = staff_df.at[i, 'Title']
            level = staff_df.at[i, 'Level']
            sections = 0
            students = 0

            staff_list.append([name, upn, title, level, sections, students])
        
        staff_manager = pd.DataFrame(staff_list, columns=['Staff', 'UPN', 'Title', 'Level', 'T-Sections', 'T-Students'])
        return staff_manager
    
    def utilization(s, staff_schedules_frame, staff_manager_list):
        name = ''
        upn = ''
        sections = 0
        students = 0
        utlization = ''
        title = '' 
        
        records_list = []
        
        copy = staff_schedules_frame
        copy = copy.drop_duplicates('UPN')
        
        
        for i in copy.index:
            sections = 0
            students = 0
            
            name = copy.at[i, 'Staff']
            upn = copy.at[i, 'UPN']
            title = copy.at[i, 'Title']
            
            for j in staff_schedules_frame.index:
                if copy.at[i, 'UPN'] == staff_schedules_frame.at[j, 'UPN']:
                    sections = sections + 1 
                    students = students + staff_schedules_frame.at[j, 'Students']

                #General Utilization
                if sections == 0:
                    utlization = 'Under-Utilized'
                if sections >= 4:
                    utlization = 'Over-Utilized'
                   
                #DC & ADJ Utilization
                if sections >= 2 and title == 'DC':
                    utlization = 'Over-Utilized'
                if sections >= 2 and title == 'ADJ':
                    utlization = 'Over-Utilized'
                    
                if sections == 1 and title == 'DC':
                    utlization = 'Fully Utilized'
                if sections == 1 and title == 'ADJ':
                    utlization = 'Fully Utilized'
                    
                #CD & ACD Utilization
                #1 Section
                if sections == 1 and students < 28 and (title == 'CD' or title == 'ACD'):
                    utlization = 'Under-Utilized'
                if sections == 1 and students > 50 and (title == 'CD' or title == 'ACD'):
                    utlization = 'Over-Utilized'
                if sections == 1 and students >= 28 and students <= 50 and (title == 'CD' or title == 'ACD'):
                    utlization = 'Fully Utilized'


                #2 Sections
                if sections == 2 and students < 50  and (title == 'CD' or title == 'ACD'):
                    utlization = 'Under-Utilized'
                if sections == 2 and students > 100 and (title == 'CD' or title == 'ACD'):
                    utlization = 'Over-Utilized'
                if sections == 2 and students >= 50 and students <= 100 and (title == 'CD' or title == 'ACD'):
                    utlization = 'Fully Utilized'
                    
                #3 Sections
                if sections == 3 and students > 72 and (title == 'CD' or title == 'ACD'):
                    utlization = 'Over-Utilized'
                if sections == 3 and students <= 72 and (title == 'CD' or title == 'ACD'):
                    utlization = 'Fully Utilized'
            
            records_list.append([name, upn, sections, students, utlization])
        
        #Looks for staff that arent teaching anything
        not_teaching = []
        staff_manager_list = staff_manager_list.drop_duplicates('UPN')
        
        for i in staff_manager_list.index:
            isMatch = True
            
            for j in staff_schedules_frame.index:
                if staff_manager_list.at[i, 'UPN'] == staff_schedules_frame.at[j, 'UPN']:
                    isMatch = True
                    break
                else:
                    isMatch = False
            
            #if not teaching add to list     
            if isMatch == False:
                name = staff_manager_list.at[i, 'Staff']
                upn = staff_manager_list.at[i, 'UPN']
                sections = 0
                students = 0
                utlization = 'Not Teaching'
                
                not_teaching.append([name, upn, sections, students, utlization])

        #add those not teaching to end of output list        
        for i in not_teaching:
            records_list.append(i)        
                

        staff_report = pd.DataFrame(records_list, columns=['Staff','UPN','T-Sections','T-Students','Utlization'])   
        
        return staff_report
    
    
    def utilizationUpdater(s, scheduleDF, aar):
        records = []
        
        name = ''
        upn = ''
        sections = 0
        students = 0
        utlization = ''
        title = '' 
                
        copy = scheduleDF
        copy = copy.drop_duplicates('UPN')
        
        
        for i in copy.index:
            sections = 0
            students = 0
            
            name = copy.at[i, 'Staff']
            upn = copy.at[i, 'UPN']
            title = copy.at[i, 'Title']
            
            for j in scheduleDF.index:
                if copy.at[i, 'UPN'] == scheduleDF.at[j, 'UPN']:
                    sections = sections + 1 
                    students = students + scheduleDF.at[j, 'Students']

                #General Utilization
                if sections == 0:
                    utlization = 'Under-Utilized'
                if sections >= 4:
                    utlization = 'Over-Utilized'
                   
                #DC & ADJ Utilization
                if sections >= 2 and title == 'DC':
                    utlization = 'Over-Utilized'
                if sections >= 2 and title == 'ADJ':
                    utlization = 'Over-Utilized'
                    
                if sections == 1 and title == 'DC':
                    utlization = 'Fully Utilized'
                if sections == 1 and title == 'ADJ':
                    utlization = 'Fully Utilized'
                    
                #CD & ACD Utilization
                #1 Section
                if sections == 1 and students < 28 and (title == 'CD' or title == 'ACD'):
                    utlization = 'Under-Utilized'
                if sections == 1 and students > 50 and (title == 'CD' or title == 'ACD'):
                    utlization = 'Over-Utilized'
                if sections == 1 and students >= 28 and students <= 50 and (title == 'CD' or title == 'ACD'):
                    utlization = 'Fully Utilized'


                #2 Sections
                if sections == 2 and students < 50  and (title == 'CD' or title == 'ACD'):
                    utlization = 'Under-Utilized'
                if sections == 2 and students > 100 and (title == 'CD' or title == 'ACD'):
                    utlization = 'Over-Utilized'
                if sections == 2 and students >= 50 and students <= 100 and (title == 'CD' or title == 'ACD'):
                    utlization = 'Fully Utilized'
                    
                #3 Sections
                if sections == 3 and students > 72 and (title == 'CD' or title == 'ACD'):
                    utlization = 'Over-Utilized'
                if sections == 3 and students <= 72 and (title == 'CD' or title == 'ACD'):
                    utlization = 'Fully Utilized'
            
            records.append([name, upn, sections, students, utlization])
        
        #Looks for staff that arent teaching anything
        not_teaching = []
        aar = aar.drop_duplicates('Unnamed: 18')
        
        for i in aar.index:
            isMatch = True
            
            for j in scheduleDF.index:
                if aar.at[i, 'Unnamed: 18'] == scheduleDF.at[j, 'UPN']:
                    isMatch = True
                    break
                else:
                    isMatch = False
            
            #if not teaching add to list     
            if isMatch == False:
                name = aar.at[i, 'Unnamed: 2']
                upn = aar.at[i, 'Unnamed: 18']
                sections = 0
                students = 0
                utlization = 'Not Teaching'
                
                not_teaching.append([name, upn, sections, students, utlization])

        #add those not teaching to end of output list        
        for i in not_teaching:
            records.append(i)        
        
        
        
        staff_report = pd.DataFrame(records, columns=['Staff','UPN','T-Sections','T-Students','Utlization']) 
        return staff_report