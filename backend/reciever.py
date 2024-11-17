import multiprocessing
from flask import Flask, request, redirect, send_file, url_for
from werkzeug.utils import secure_filename
import subprocess
import os
import xml.etree.ElementTree as ET
import cv2
import session
import shutil
import zipfile
app = Flask(__name__)
UPLOAD_FOLDER = './upload_folder'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg','pdf'}
AUDIVERIES_COMMAND = '../audiveris/build/distributions/Audiveris-5.3.1/bin/Audiveris'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
@app.route('/upload', methods=['POST'])
def upload():
    saved_name = request.headers.get('name')
    if 'file' not in request.files:
        print(request.files)
        return redirect(request.url)
    file = request.files['file']
    if file and allowed_file(file.filename):
            filename = secure_filename(saved_name  + ".pdf")
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            result = subprocess.run([AUDIVERIES_COMMAND, "-export", "-batch", file_path])
            return_code = result.returncode
            extract_to_directory = f"{UPLOAD_FOLDER}/{saved_name}"
            os.mkdir(f"{UPLOAD_FOLDER}/{saved_name}")
            os.mkdir(f"{UPLOAD_FOLDER}/{saved_name}/{saved_name}sheet")
            os.mkdir(f"{UPLOAD_FOLDER}/{saved_name}/{saved_name}music")
            extract_to_directory = f"{UPLOAD_FOLDER}/{saved_name}/{saved_name}sheet"
            extract_to_directory2 = f"{UPLOAD_FOLDER}/{saved_name}/{saved_name}music"
            shutil.move(f"/Users/mathiasthomas/Library/AudiverisLtd/audiveris/data/{saved_name}/{saved_name}.mxl", f"{UPLOAD_FOLDER}/{saved_name}")
            shutil.move(f"/Users/mathiasthomas/Library/AudiverisLtd/audiveris/data/{saved_name}/{saved_name}.omr", f"{UPLOAD_FOLDER}/{saved_name}")
            with zipfile.ZipFile( f"{UPLOAD_FOLDER}/{saved_name}/{saved_name}.mxl", 'r') as zip_ref:
                zip_ref.extractall(extract_to_directory)
            with zipfile.ZipFile( f"{UPLOAD_FOLDER}/{saved_name}/{saved_name}.omr", 'r') as zip_ref:
                zip_ref.extractall(extract_to_directory2)
            os.remove( f"{UPLOAD_FOLDER}/{saved_name}/{saved_name}.mxl")
            os.remove( f"{UPLOAD_FOLDER}/{saved_name}/{saved_name}.omr")
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
    print(images)
    sheets.reverse()
    images.reverse()
    print( "path:" +music_path)          
    p = multiprocessing.Process(target=session.create_and_handle_session, args=(sheets,music_path,images))
    p.start()
    p.join()

    files_to_zip = [
        'results0.png',
        'results1.png',
        'results2.png'
    ]
    zip_filename = 'files.zip'
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in files_to_zip:
            # Ensure the file exists before adding it
            if os.path.exists(file_path):
                zipf.write(file_path, os.path.basename(file_path))
    print("Done")
    return send_file(zip_filename,as_attachment=True, download_name='files.zip')


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
        
     
    