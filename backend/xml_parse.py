import subprocess
import xml.etree.ElementTree as ET
import cv2


AUDIVERIES_COMMAND = '../audiveris/build/distributions/Audiveris-5.3.1/bin/Audiveris -export -batch'

def sort_list(ele):
    return ele[0]

def find_beat_pos(in_list, beat_start, beat_end):
    found_start = False
    found_start_idx = 0
    found_end_idx = 0
    print(in_list)
    for idx, ele in enumerate(in_list):
        print(ele[2])
        if(ele[2] >= beat_start and not found_start):
            found_start_idx = idx
            found_start = True
        if(ele[2] >= beat_end):
            return (found_start_idx,idx)
        
def parse_xml(path,path2):
     #parse beats/durations of notes
     file = ET.parse(path2)
     root = file.getroot()
     parts = root.findall('part')
     beat_list_singer = list()
     beat_list_pianist_l = list()
     beat_list_pianist_r = list()
     part_count = 0
     for part in parts:
         measures = part.findall('measure')
         for measure in measures:
            prev_note_x = 0
            notes = measure.findall('note')
            measure_list = list()
            #print("hi")
            for note in notes:
                #print(note.attrib)
                x_pos = int(note.attrib['default-x'])
                #Some notes are stacked on each other so we can ignore
                if(x_pos  <= prev_note_x +5 and x_pos >= prev_note_x - 5):
                    continue
                prev_note_x = x_pos
                #We went back to the second measure for the piano
                if(x_pos < prev_note_x - 10 and part_count != 0):
                    for note in measure_list:
                        beat_list_pianist_l.append(note)
                    measure_list = list()
                res=  note.find('duration')
                if(res is not None):
                    measure_list.append(int(note.find('duration').text))
            
            if(part_count == 0):
                for note in measure_list:
                    beat_list_singer.append(note)
            else:
                for note in measure_list:
                    beat_list_pianist_r.append(note)
                    
         part_count += 1
         print("hi")


                
     #Parse positions of notes,
     file = ET.parse(path)
     root = file.getroot()
     page = root.find('page')
     systems = page.findall('system')
     singer_list = list()
     piano_list_l = list()
     piano_list_r = list()

     count_s = 0
     count_piano_l = 0
     count_piano_r = 0
     prev_beat = 0
     for system in systems:
        sig = system.find('sig')
        inters = sig.find('inters')
        #print(inters.tag)
        brace = inters.find('brace').find('bounds').attrib
        tupl =  ((int(brace['x']) + 5),(int(brace['y']) + int(brace['h'])))
        #print(tupl)
        
        heads = inters.findall('head')
        template = cv2.imread('../../BINARY.png')
        cv2.rectangle(template,(int((brace['x'])),int(brace['y'])),tupl
                    ,(0, 0, 255), 2)
        listsing_ = list()
        list_piano_1 = list()
        list_piano_2 = list()
        brace_y = int(brace['y'])
        brace_height = int(brace['h'])
        for head in heads:
            bounds = head.find('bounds').attrib
            if(int(bounds['y']) < brace_y - brace_height/3):
                listsing_.append((int(bounds['x']),int(bounds['y'])))
            elif(int(bounds['y']) < brace_y + brace_height/2):
                list_piano_1.append((int(bounds['x']),int(bounds['y'])))
            else:
                list_piano_2.append((int(bounds['x']),int(bounds['y'])))
            #print(int(bounds['x']))
            #cv2.rectangle(template, (int(bounds['x']), int(bounds['y'])), 
                        #(int(bounds['x']) + 5, int(bounds['y']) + 5),(0, 0, 255), 2)
        listsing_.sort(key = sort_list)
        list_piano_1.sort(key = sort_list)
        list_piano_2.sort(key = sort_list)
        prev_x = 0 
        
        for ele in listsing_:
            x_post = ele[0]
            if(x_post  <= prev_x +5 and x_post >= prev_x - 5 ):
                continue
            singer_list.append((ele[0], ele[1],prev_beat + beat_list_singer[count_s] ))
            prev_x = x_post
            prev_beat += beat_list_singer[count_s]
            count_s += 1
        
        '''
        for ele in list_piano_1:
            x_post = ele[0]
            if(x_post  <= prev_x +5 and x_post >= prev_x - 5 ):
                continue
            piano_list_l.append((ele[0], ele[1],beat_list_pianist_l[count_piano_l] ))
            prev_x = x_post
            count_piano_l += 1

        for ele in list_piano_2:
            x_post = ele[0]
            if(x_post  <= prev_x +5 and x_post >= prev_x - 5 ):
                continue
            piano_list_r.append((ele[0], ele[1],beat_list_singer[count_piano_r] ))
            prev_x = x_post
            count_piano_r += 1
        '''
     (idx1, idx2) = find_beat_pos(singer_list, 8, 150)
     print((idx1,idx2))
     prev_x = 0
     start = idx1
     #do this to check for new line
     for i in range(idx1,idx2 + 1):
        if(singer_list[i][0] < prev_x):
            cv2.rectangle(template, (singer_list[start][0], singer_list[start][1]), 
                (singer_list[i - 1][0] + 5, singer_list[i - 1][1] + 5),(0, 0, 255), 2)
            start = i
            prev_x = 0
        prev_x =  singer_list[i][0]
    
            
        
     cv2.rectangle(template, (singer_list[start][0], singer_list[start][1]), 
     (singer_list[idx2][0] + 5, singer_list[idx2][1] + 5),(0, 0, 255), 2)
     cv2.imwrite("results.png", template)
    
def upload(file_path):
    result = subprocess.run([AUDIVERIES_COMMAND, "-export", "-batch", file_path])
    return_code = result.returncode
    return f"Yes {return_code}"
    
#upload("../../Ach, ich fühl's (Pamina) La flauta mágica (Mozart).pdf")     
parse_xml('../../sheet#1.xml', '../../music1.xml')