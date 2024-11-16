import multiprocessing
from flask import Flask, request, redirect, url_for
from werkzeug.utils import secure_filename
import subprocess
import os
import xml.etree.ElementTree as ET
import cv2
import session
app = Flask(__name__)
UPLOAD_FOLDER = '../../upload_folder'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg','pdf'}
AUDIVERIES_COMMAND = './audiveris/build/distributions/Audiveris-5.3.1/bin/Audiveris -export -batch'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
@app.route('/upload', methods=['POST'])
def upload():
    saved_name = request.args['name']
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files('file')
    if file and allowed_file(file.filename):
            filename = secure_filename(saved_name  + ".pdf")
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            result = subprocess.run([AUDIVERIES_COMMAND, "-export", "-batch", file_path])
            return_code = result.returncode

            return f"Yes {return_code}"
    
    return "No"

@app.route('/startsong', methods=['POST'])
def start_song():
    print("Recieved Start Song")
    song_name = str(request.get_data())
    song_name = song_name[2:len(song_name) - 1]
    print(song_name)
    data_path = os.path.join(app.config['UPLOAD_FOLDER'], song_name)
    music_path = ""
    sheets = []
    images = []
    for dir_path in os.listdir(data_path):
         for dir_path2 in os.listdir(os.path.join(data_path,dir_path)):
              
              if(dir_path.endswith("sheet")):
                   if(os.path.isdir(os.path.join(data_path, dir_path,dir_path2))):
                        for dir_path3 in os.listdir(os.path.join(data_path,dir_path,dir_path2)):
                             print(dir_path3)
                             if(dir_path3.endswith(".png")):
                                  images.append(os.path.join(data_path, dir_path, dir_path2, dir_path3))
                             else:
                                  sheets.append(os.path.join(data_path, dir_path, dir_path2, dir_path3))
              else:
                   if(os.path.isfile(os.path.join(data_path, dir_path,dir_path2))):
                        music_path = os.path.join(data_path, dir_path,dir_path2)
    
    print(sheets)
    print( "path:" +music_path)          
    p = multiprocessing.Process(target=session.create_and_handle_session, args=(sheets,music_path,images))
    p.start()
    p.join()
    print("Done")
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''


@app.route('/get_all_songs', methods=['GET'])
def get_all_songs():

    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files('file')
    if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            

            return redirect(url_for('download_file', name=filename))
    
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''
'''
This function parses the position of the note elements from the XML and sorts them
It sorts first by y postion and groups elements with similar y positions into there own list(measure)
then by x position within each measure
'''
def parse_xml(path):
     file = ET.parse(path)
     root = file.getroot()
     page = root.find('page')
     system = page.find('system')
     heads = system.findall('head')
     template = cv2.imread('BINARY.png')

     for head in heads:
        bounds = head.find('bounds').text
        print(bounds)
        
     
    