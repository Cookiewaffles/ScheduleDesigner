# -*- coding: utf-8 -*-
"""
Created on Tue Apr 16 20:50:00 2024

@author: Jacob Heiser
"""
import pandas as pd
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)


class course:
    #collect basic info of the various courses
    def counter(s, courseFrame, staffFrame):
        update = []
        
        #UPDATE DATA FORMAT: to remove duplicates
        for i in courseFrame.index:
            newCode = courseFrame.at[i, 'Code']
            
            newSection = courseFrame.at[i, 'Section']
            newDescrip = courseFrame.at[i, 'ClassSchedDescrip']
            newStudents = courseFrame.at[i, 'RegStudents']
            
            update.append([newCode, newSection, newDescrip, newStudents])

    
        courseFrameUpdate = pd.DataFrame(update, columns=['Code', 'Section', 'ClassSchedDescrip', 'RegStudents'])
        courseFrameUpdate = courseFrameUpdate.drop_duplicates('Code')

        #variables
        classes = 0
        students = 0
        staff = 0
        code = ''
        name = ''
        
        
        
        info_list = []
        #loop to collect info on each unique course
        for i in courseFrameUpdate.index:
            first = courseFrameUpdate.at[i, 'Code']
            
            for j in courseFrame.index:
                second = courseFrame.at[j, 'Code']
                
                if first == second:
                    classes = classes + 1
                    students = students + courseFrame.at[j, 'RegStudents']
            
            

            code = first
            name = courseFrame.at[i, 'ClassSchedDescrip']
                
            for j in staffFrame.index:
                data = staffFrame.at[j, 'Unnamed: 7'] #grabs Academic Appointment Title
                data = data.split()[0] #Grabs the Code, leaving behind description
                
                if data == code:
                    staff = staff + 1

            info_list.append([code, name, classes, staff, students])
                
            #reset
            classes = 0
            students = 0
            staff = 0
            
        course_info = pd.DataFrame(info_list,columns=['Code', 'Class', 'T-Classes', 'T-Staff', 'T-Students'])
        
        return course_info
    
    

    #Assign courses to staff
    #TODO: in course_frame and course_info - add column called isAssigned
    def assignment(s, course_info, staff_info, course_frame, staff_manager_list):
        #course_info: Code, Class, T-Classes, T-Staff, T-Students
        #staff_info: Name, ID, Code, Title, Level, UPN
        #course_frame: Code, Section, Name, Students, fulfill
        
        #variables
        info_list = []
        no_staff_available_list = []
        course_no_students_list = []
        unfilledClasses = True
        
        #1: Find categories with most categories to assign first        
        #2: Find Staff that can be assigned
        #3: Loop till all classes are filled
        #4: Repeat for all categories - Done - Not Tested
        
        #Organize which classes to fill first
        course_info = course_info.sort_values(by=['T-Classes'], ascending=False)
        course_frame = course_frame.sort_values(by=['RegStudents'], ascending=False)
        
        #Keep looping till all courses are assigned
        while unfilledClasses == True:
            #Using Course_Info: Loop through Categories with greater courses first
            #
            #Skip Courses that have no Students attending
            
            code = ''
            section = ''
            class_name = '' 
            students = 0
            staff = ''
            title = ''
            UPN = ''
            has_Staff = 'NA'
            has_Students= 'NA'
            isOnline = False
            valid = True
            
            #Loops through each course starting with courses with more classes/sections
            for i in course_info.index:
                #find each matching course in the provided data    

                
                for j in course_frame.index:
                    Frame_code = course_frame.at[j, 'Code']
                    
                    #Design to see if course is online or lecture
                    word_list = str(course_frame.at[j, 'ClassSchedDescrip']).split()
                    
                    if word_list[-1] == 'Lecture':
                        isOnline = False
                    elif word_list[-1] == 'Online':
                        isOnline = True
                    else:
                        isOnline = True
                    
                    #Assign found courses that have not been fulfilled
                    if course_info.at[i, 'Code'] == Frame_code and course_frame.at[j, 'Fulfilled?'] == 'No':
                        #loop and find and assign staff able to teach 
                        assigned = False
                        needReserved = False
                        level = 1
                        staff_title = 'DC'
                        loop = 0      
                        totalStudents = 0
                        isNan = False
                        
                        try:
                            totalStudents = int(course_frame.at[j, 'RegStudents'])
                        except ValueError:
                            isNan = True
                            pass
                            
                        
                        while assigned == False and loop <= 100 and totalStudents > 0:
                            #assign staff
                            for k in staff_info.index:
                                staff_level = staff_info.at[k, 'Level']
                                valid = True
                                
                                #if adj and on campus, cannot teach course
                                if staff_title == 'ADJ':
                                    if isOnline == True:
                                        valid = True
                                    else:
                                        valid = False
                                    

                                if valid == True:
                                    #Checks to see if staff has correct code
                                    if staff_info.at[k, 'Code'] == Frame_code:
                                        #Loops through staff titles starting at DC -> CD -> ADC -> ADJ
                                        if staff_info.at[k, 'Title'] == staff_title:
                                            if level == 1:
                                                if staff_level == 'level 1':
                                                    #Assign Staff
                                                    staff = staff_info.at[k, 'Name']
                                                    UPN = staff_info.at[k, 'UPN']
                                                    title = staff_info.at[k, 'Title']
                                                    
                                                    course_frame.at[j, 'Fulfilled?'] = 'Yes'
                                                    
                                                    #IF title is DC update to level 6 so they cannot be assigned again
                                                    #IF title is ADJ update to level 7 so they cannot be assigned again
                                                    #IF CD or ACD Check Utilze Status
                                                    if staff_info.at[k, 'Title'] == 'DC':
                                                        staff_info.at[k, 'Level'] = 'level 6'
                                                    elif staff_info.at[k, 'Title'] == 'ADJ':
                                                        staff_info.at[k, 'Level'] = 'level 7'
                                                    else:
                                                        status = course.courseUtilization(staff_manager_list, UPN, course_frame.at[j, 'RegStudents'])
                                                        
                                                        if status == 'Over':
                                                            staff_info.at[k, 'Level'] = 'level 4'
                                                        elif status == 'Full':
                                                            staff_info.at[k, 'Level'] = 'level 4'
                                                        elif status == 'Under':
                                                            staff_info.at[k, 'Level'] = 'level 1'
                                                            
                                                    newLevel = staff_info.at[k, 'Level']   
                                                    assigned = True
                                                    break
                                            if level == 2:   
                                                 if staff_level == 'level 2':
                                                     #Assign Staff
                                                     staff = staff_info.at[k, 'Name']
                                                     UPN = staff_info.at[k, 'UPN']
                                                     title = staff_info.at[k, 'Title']
                                                     
                                                     course_frame.at[j, 'Fulfilled?'] = 'Yes'
                                                     
                                                     #IF title is DC update to level 6 so they cannot be assigned again
                                                     #IF title is ADJ update to level 7 so they cannot be assigned again
                                                     #IF CD or ACD Check Utilze Status
                                                     if staff_info.at[k, 'Title'] == 'DC':
                                                         staff_info.at[k, 'Level'] = 'level 6'
                                                     elif staff_info.at[k, 'Title'] == 'ADJ':
                                                         staff_info.at[k, 'Level'] = 'level 7'
                                                     else:
                                                         status = course.courseUtilization(staff_manager_list, UPN, course_frame.at[j, 'RegStudents']) 
                                                         
                                                         if status == 'Over':
                                                             staff_info.at[k, 'Level'] = 'level 4'
                                                         elif status == 'Full':
                                                             staff_info.at[k, 'Level'] = 'level 4'
                                                         elif status == 'Under':
                                                             staff_info.at[k, 'Level'] = 'level 2'
                                                             
                                                     newLevel = staff_info.at[k, 'Level']    
                                                     assigned = True
                                                     break
        
                                            if level == 3:    
                                                 if staff_level == 'level 3':
                                                     #Assign Staff
                                                     staff = staff_info.at[k, 'Name']
                                                     UPN = staff_info.at[k, 'UPN']
                                                     title = staff_info.at[k, 'Title']
                                                     
                                                     course_frame.at[j, 'Fulfilled?'] = 'Yes'
                                                     
                                                     
                                                     #IF title is DC update to level 6 so they cannot be assigned again
                                                     #IF title is ADJ update to level 7 so they cannot be assigned again
                                                     #IF CD or ACD Check Utilze Status
                                                     if staff_info.at[k, 'Title'] == 'DC':
                                                         staff_info.at[k, 'Level'] = 'level 6'
                                                     elif staff_info.at[k, 'Title'] == 'ADJ':
                                                         staff_info.at[k, 'Level'] = 'level 7'
                                                     else:
                                                         status = course.courseUtilization(staff_manager_list, UPN, course_frame.at[j, 'RegStudents'])
                                                         
                                                         if status == 'Over':
                                                             staff_info.at[k, 'Level'] = 'level 4'
                                                         elif status == 'Full':
                                                             staff_info.at[k, 'Level'] = 'level 4'
                                                         elif status == 'Under':
                                                             staff_info.at[k, 'Level'] = 'level 3'
                                                         
                                                     newLevel = staff_info.at[k, 'Level']
                                                     assigned = True
                                                     break
                                            if level == 4:    
                                                 if staff_level == 'level 4':
                                                     #Assign Staff
                                                     staff = staff_info.at[k, 'Name']
                                                     UPN = staff_info.at[k, 'UPN']
                                                     title = staff_info.at[k, 'Title']
                                                     
                                                     course_frame.at[j, 'Fulfilled?'] = 'Yes'
                                                     staff_info.at[k, 'Level'] = 'level 5'
                                                     newLevel = staff_info.at[k, 'Level']
                                                     assigned = True
                                                     break
                                            
                                        #reset all level 5 to 4
                                        #Level 5 does not care about current title - just want to reset everyone to Level 4 and repeat
                                        if level == 5:    
                                             if staff_level == 'level 5':
                                                 #Assign Staff
                                                 staff = staff_info.at[k, 'Name']
                                                 UPN = staff_info.at[k, 'UPN']
                                                 title = staff_info.at[k, 'Title']
                                                 
                                                 staff_info.at[k, 'Level'] = 'level 4'
                                                 assigned = False  
                         
                            #assign staff courses to correct level
                            if assigned == True:
                                for k in staff_info.index:
                                    if staff_info.at[k, 'UPN'] == UPN:
                                        staff_info.at[k, 'Level'] = newLevel
                                    
                            
                            if assigned == False:
                                level = level + 1

                            if needReserved == False:
                                if level > 3:
                                    if staff_title != 'ADJ':
                                        level = 1
                                        staff_title = course.updateTitle(staff_title)
                                        
                                        loop = loop + 1
                            
                            if level > 5:
                                level = 1
                                needReserved = True
                                staff_title = course.updateTitle(staff_title)
                                
                                loop = loop + 1
                        
                                
                        if assigned == True:
                            has_Staff = 'YES'
                            has_Students = 'YES'
                            
                            
                        #assign variables
                        code = course_frame.at[j, 'Code']
                        section = course_frame.at[j, 'Section']
                        class_name = course_frame.at[j, 'ClassSchedDescrip']
                        students = course_frame.at[j, 'RegStudents']
                        
                        #Check if it there is staff to teach course and assign to correct list      
                        if isNan == False:
                            if loop >= 100:
                                print('ERROR: No Staff found to assign to Course: ' + code + ' --- Section:' + str(section))
                                
                                staff = 'NA'
                                UPN = 'NA'
                                title = 'NA'
                                
                                has_Staff = 'NO'
                                
                                if totalStudents > 0:
                                    has_Students = 'YES'
                                
                                no_staff_available_list.append([code, section, class_name, students, staff, UPN, title, has_Staff, has_Students])
                                
                            elif totalStudents <= 0:
                                    print('ERROR: No Students in Course: ' + code + ' --- Section:' + str(section))
    
                                    staff = 'NA'
                                    UPN = 'NA'
                                    title = 'NA'
                                    
                                    has_Students = 'NO'
                                    
                                    for k in staff_info.index:
                                        if staff_info.at[k, 'Code'] == Frame_code:
                                            has_Staff = 'YES'
                                            break
                                        else:
                                            has_Staff = 'NO'
                                            
    
                                    course_no_students_list.append([code, section, class_name, students, staff, UPN, title, has_Staff, has_Students])
                            else:
                                info_list.append([code, section, class_name, students, staff, UPN, title, has_Staff, has_Students])
            
            
            print('Caluclating Fullfiment')
            
            no_staff_available = pd.DataFrame(no_staff_available_list, columns=['Code', 'Section', 'Class', 'Students', 'Staff', 'UPN', 'Title', 'Has Staff', 'Has Students'])
            print('Caluclating Fullfiment')
            #Check to see if all courses have been assigned
            for i in course_frame.index:
                try:
                    studentsAmount = int(course_frame.at[i, 'RegStudents'])
                except ValueError:
                    pass
                
                #Check only courses with students
                if studentsAmount > 0:
                    
                    #Checks to see if course has staff that can teach the course
                    hasStaff = True
                    for j in no_staff_available.index:
                        if no_staff_available.at[j, 'Code'] == course_frame.at[i, 'Code'] and no_staff_available.at[j, 'Section'] == course_frame.at[i, 'Section']:
                            hasStaff = False
                            break
                     
                    if hasStaff == True:
                        status = course_frame.at[i, 'Fulfilled?']
                
                        if status == 'No':
                            print(course_frame.at[i, 'Code'])
                            unfilledClasses = True
                            break
                        
                        else:
                            unfilledClasses = False
                    else:
                        unfilledClasses = False
        
                        
        for i in no_staff_available_list:
            info_list.append(i)
        for i in course_no_students_list:
            info_list.append(i)
            
            
        staff_schedules = pd.DataFrame(info_list,columns=['Code', 'Section', 'Class', 'Students', 'Staff', 'UPN', 'Title', 'Has Staff', 'Has Students'])
        
        #fix up formating
        for i in staff_schedules.index:
            #Section Formatting
            try:             
                if int(staff_schedules.at[i, 'Section']) <= 9:
                    staff_schedules.at[i, 'Section'] = '0' + str(staff_schedules.at[i, 'Section'])
                else:
                    staff_schedules.at[i, 'Section'] = str(staff_schedules.at[i, 'Section'])
            except ValueError:
                pass
            
            #Code Formatting
            word_list = str(staff_schedules.at[i, 'Class']).split()
            
            if str(staff_schedules.at[i, 'Section']) == '00':
                staff_schedules.at[i, 'Code'] = staff_schedules.at[i, 'Code'] + '-L'
            elif word_list[-1] == 'Lecture':
                staff_schedules.at[i, 'Code'] = staff_schedules.at[i, 'Code'] + '-L'
                
            elif word_list[-1] == 'Online':
                staff_schedules.at[i, 'Code'] = staff_schedules.at[i, 'Code'] + '-O'
            else:
                staff_schedules.at[i, 'Code'] = staff_schedules.at[i, 'Code'] + '-O'
                
        return staff_schedules
            
     
    
    
    #Updates title to next title
    def updateTitle(title):
        if title == 'DC':
            title = 'CD'
            
        elif title == 'CD':
            title = 'ACD'
            
        elif title == 'ACD':
            title = 'ADJ'
            
        elif title == 'ADJ':
            title = 'DC'
            
        else:
            title = 'Error'
            
        return title
    
    
    def courseUtilization(staff_list, upn, students):
        status = ''
        for i in staff_list.index:
            #add new course additions
            if staff_list.at[i, 'UPN'] == upn:
                staff_list.at[i, 'T-Sections'] = staff_list.at[i, 'T-Sections'] + 1
                staff_list.at[i, 'T-Students'] = staff_list.at[i, 'T-Students'] + students
                
                sections = staff_list.at[i, 'T-Sections']
                totalStudents = staff_list.at[i, 'T-Students']
                title = staff_list.at[i, 'Title']

                #Check Utilization
                #General Utilization
                if staff_list.at[i, 'T-Sections'] == 0:
                    status = 'Under'
                if staff_list.at[i, 'T-Sections'] >= 4:
                    status = 'Over'
            
                
                
                #CD & ACD Utilization
                #1 Section
                if sections == 1 and totalStudents < 28 and (title == 'CD' or title == 'ACD'):
                    status = 'Under'
                if sections == 1 and totalStudents > 50 and (title == 'CD' or title == 'ACD'):
                    status = 'Over'
                if sections == 1 and totalStudents >= 28 and totalStudents <= 50 and (title == 'CD' or title == 'ACD'):
                    status = 'Full'

                #2 Sections
                if sections == 2 and totalStudents < 50  and (title == 'CD' or title == 'ACD'):
                    status = 'Under'
                if sections == 2 and totalStudents > 100 and (title == 'CD' or title == 'ACD'):
                    status = 'Over'
                if sections == 2 and totalStudents >= 50 and totalStudents <= 100 and (title == 'CD' or title == 'ACD'):
                    status = 'Full'
                    
                #3 Sections
                if sections == 3 and totalStudents > 72 and (title == 'CD' or title == 'ACD'):
                    status = 'Over'
                if sections == 3 and totalStudents <= 72 and (title == 'CD' or title == 'ACD'):
                    status = 'Full'
                    
                break
            
        return status
    

    
    def courseFrameAdjustment(s, courseFrame):
        frame = []
        fulfilled = 'No'
        code = ''
        section = ''
        class_name = '' 
        students = 0
        
        
        for i in courseFrame.index:
            code = str(courseFrame.at[i, 'Code'])
            code = "".join(code.split())
            code = code[:-2] 
            
            section = courseFrame.at[i, 'Section']
            class_name = courseFrame.at[i, 'ClassSchedDescrip']
            students = courseFrame.at[i, 'RegStudents']

            frame.append([code, section, class_name, students, fulfilled])
        
        frameAdjustment = pd.DataFrame(frame, columns=['Code','Section','ClassSchedDescrip','RegStudents','Fulfilled?'])
        return frameAdjustment