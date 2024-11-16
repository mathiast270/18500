import subprocess
import xml.etree.ElementTree as ET
import cv2

def sort_list(ele):
    return ele[0]

def find_beat_pos(in_list, beat_start, beat_end):
    found_start = False
    found_start_idx = 0
    
    for idx, ele in enumerate(in_list):
        print(ele[2])
        if(ele[2] >= beat_start and not found_start):
            found_start_idx = idx
            found_start = True
        if(ele[2] >= beat_end):
            return (found_start_idx,idx)
        
    return (found_start_idx, len(in_list) - 1)
def make_lists_count(sheet_path, music_xml_path, image_path,count):
     file = ET.parse(music_xml_path)
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
     file = ET.parse(sheet_path)
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
        template = cv2.imread(image_path)
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
            singer_list.append((ele[0], ele[1],prev_beat +beat_list_singer[count_s + count] ))
            prev_x = x_post
            prev_beat += beat_list_singer[count + count_s]
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
            count_
        '''
        return (singer_list, count_s,template)
class MusicManager():
    def __init__(self, sheet_path, music_xml_path,image_path):
        self.singer_lists = []
        self.image_lists = []
        total_count = 0
        for idx, sheet in enumerate(sheet_path):
            (singers, count_s, templates) = make_lists_count(sheet,music_xml_path,image_path[idx],total_count)
            total_count += count_s
            self.singer_lists.append(singers)
            self.image_lists.append(templates)

        self.in_sync = True
        self.start = -1
        self.last_recieved_beat = -1
        #parse beats/durations of notes
    def set_sync_status(self,beat, sync_status):
        #In this case we should start measuring 
        if(self.in_sync and not sync_status):
            self.in_sync = False
            self.start = beat
        #Are in sync again dont write to file
        elif(not self.in_sync and sync_status):
            print("Nooooooo plsss")
            for idx, singer in enumerate(self.singer_lists):
                print()
                if(singer[0][2] > self.start or singer[len(singer) - 1][2] < self.start):
                    print(singer)
                    print(self.start)
                    continue
                (start, end) = find_beat_pos(singer, self.start,beat)
                image = self.image_lists[idx]
                start_t = start
                prev_x = 0
                for i in range(start,end + 1):
                    print("Nooooooo")
                    if(singer[i][0] < prev_x):
                        cv2.rectangle(image, (singer[start_t][0], singer[start_t][1]), 
                            (singer[i - 1][0] + 5, singer[i - 1][1] + 5),(0, 0, 255), 2)
                        start_t = i
                        prev_x = 0
                    prev_x =  singer[i][0]
                cv2.imwrite(f"results{idx}.png", image)
                #Continue parsing to next sheet 
                if(singer[end][2] < beat):
                    if(idx < len(self.singer_lists) - 1):
                        self.start = self.singer_lists[idx + 1][2]
            
            self.in_sync = True
            self.start = False
        else:
            self.last_recieved_beat = beat
            
    def done(self):
        print(f"len singer list: {self.singer_lists}")
        print(f"start list: {self.start}")
        for idx, singer in enumerate(self.singer_lists):
                if(singer[0][2] > self.start or singer[len(singer) - 1][2] < self.start):
                    continue
                (start, end) = find_beat_pos(singer, self.start,self.last_recieved_beat)
                image = self.image_lists[idx]
                start_t = start
                prev_x = 0
                for i in range(start,end + 1):
                    if(singer[i][0] < prev_x):
                        cv2.rectangle(image, (singer[start_t][0], singer[start_t][1]), 
                            (singer[i - 1][0] + 5, singer[i - 1][1] + 5),(0, 0, 255), 2)
                        start_t = i
                        prev_x = 0
                    prev_x =  singer[i][0]
                print("Made it")
                cv2.imwrite(f"results{idx}.png", image)
                #Continue parsing to next sheet 
                if(singer[end][2] < self.last_recieved_beat):
                    if(idx < len(self.singer_lists)):
                        self.start = self.singer_lists[idx + 1][2]
            
        self.in_sync = True
        self.start = False
        