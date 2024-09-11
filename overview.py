# -*- coding: utf-8 -*-
"""
Created on Wed May 22 20:25:17 2024

@author: dialw
"""

import pandas as pd
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)


class overview:
    def overview_report(s, scheduleReport, ultizationReport, staff_info_frame):
        scheduleReport = formatCode(scheduleReport)
        
        copy = scheduleReport.drop_duplicates('Code')
        
        scheduleReport = scheduleReport.drop_duplicates(subset=['Code', 'UPN'])
        
        overview_list = []
        
        for i in copy.index:
            fully = 0
            overult = 0
            underUlt = 0
            notTeaching = 0
            
            currentcheck = copy.at[i, 'Code']
            #This will find all staff that are teaching
            for j in scheduleReport.index:
                valid = True
                
                #Checks only courses that that are valid 
                if scheduleReport.at[j, 'Has Staff'] == 'NO':
                    valid = False
                if scheduleReport.at[j, 'Has Students'] == 'NO':
                    valid = False
                  
                    
                if valid == True:    
                    scheduleCheck = scheduleReport.at[j, 'Code']
                    
                    if scheduleCheck == currentcheck:
                        scheduleUPN = scheduleReport.at[j, 'UPN']
                        
                        for k in ultizationReport.index:
                            if scheduleUPN == ultizationReport.at[k, 'UPN']:
                                utlization = ultizationReport.at[k, 'Utlization']
                                
                                if utlization == 'Over-Utilized':
                                    overult = overult + 1
                                    
                                elif utlization == 'Fully Utilized':
                                    fully = fully + 1
    
                                elif utlization == 'Under-Utilized':
                                    underUlt = underUlt + 1
                                    
                                
            #This will find all staff that are not teaching the courses
            for j in staff_info_frame.index:
                if currentcheck == staff_info_frame.at[j, 'Code']:
                    staffUPN = staff_info_frame.at[j, 'UPN'] 
                    
                    for k in ultizationReport.index:
                        if staffUPN == ultizationReport.at[k, 'UPN']:
                            utlization = ultizationReport.at[k, 'Utlization']
                            
                            if utlization == 'Not Teaching':
                                notTeaching = notTeaching + 1
                
            
            #Add to list
            overview_list.append([currentcheck, fully, overult, underUlt, notTeaching])
            
        #Add to Overview Database
        overview_report = pd.DataFrame(overview_list, columns=['Code','Fully Utilized','Over-Utilized','Under-Utilized','Not Teaching'])

        return overview_report
    
    
    def overviewUpdater(s, scheduleDF, utilizationUpdate, aar):
        scheduleDF = formatCode(scheduleDF)
        
        copy = scheduleDF.drop_duplicates('Code')
        scheduleDF = scheduleDF.drop_duplicates(subset=['Code', 'UPN'])
        
        overview_list = []

        for i in copy.index:
            fully = 0
            overult = 0
            underUlt = 0
            notTeaching = 0

            currentcheck = copy.at[i, 'Code']
            #This will find all staff that are teaching
            for j in scheduleDF.index:
                valid = True
                
                #Checks only courses that that are valid 
                if scheduleDF.at[j, 'Has Staff'] == 'NO':
                    valid = False
                if scheduleDF.at[j, 'Has Students'] == 'NO':
                    valid = False
                  
                    
                if valid == True:    
                    scheduleCheck = scheduleDF.at[j, 'Code']
                    
                    if scheduleCheck == currentcheck:
                        scheduleUPN = scheduleDF.at[j, 'UPN']
                        
                        for k in utilizationUpdate.index:
                            if scheduleUPN == utilizationUpdate.at[k, 'UPN']:
                                utlization = utilizationUpdate.at[k, 'Utlization']
                                
                                if utlization == 'Over-Utilized':
                                    overult = overult + 1
                                    
                                elif utlization == 'Fully Utilized':
                                    fully = fully + 1
    
                                elif utlization == 'Under-Utilized':
                                    underUlt = underUlt + 1
                     
                                
            #This will find all staff that are not teaching the courses
            for j in aar.index:
                if currentcheck == aar.at[j, 'Unnamed: 7']:
                    staffUPN = aar.at[j, 'Unnamed: 18'] 
                    
                    for k in utilizationUpdate.index:
                        if staffUPN == utilizationUpdate.at[k, 'UPN']:
                            utlization = utilizationUpdate.at[k, 'Utlization']
                            
                            if utlization == 'Not Teaching':
                                notTeaching = notTeaching + 1
                

            #Add to list
            overview_list.append([currentcheck, fully, overult, underUlt, notTeaching])
            
        #Add to Overview Database
        overview_report = pd.DataFrame(overview_list, columns=['Code','Fully Utilized','Over-Utilized','Under-Utilized','Not Teaching'])

        return overview_report
    
#Format Code
def formatCode(report):
    frame = []
    code = ''
    section = ''
    className = ''
    students = 0
    staff = ''
    upn = ''
    title = ''
    hasStaff = ''
    hasStudents = ''
    
    for i in report.index:
        code = str(report.at[i, 'Code'])
        code = "".join(code.split())
        code = code[:-2] 
        
        section = report.at[i, 'Section']
        className = report.at[i, 'Class']
        students = report.at[i, 'Students']
        staff = report.at[i, 'Staff']
        upn = report.at[i, 'UPN']
        title = report.at[i, 'Title']
        hasStaff = report.at[i, 'Has Staff']
        hasStudents = report.at[i, 'Has Students']

        frame.append([code, section, className, students, staff, upn, title, hasStaff, hasStudents])
    
    
    frameAdjustment = pd.DataFrame(frame, columns=['Code','Section','Class','Students','Staff','UPN','Title','Has Staff','Has Students'])
    
    return frameAdjustment