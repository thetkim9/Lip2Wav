from flask import Flask, render_template, request, send_file, make_response
#from flask_limiter import Limiter
from PIL import Image, ImageOps
import time
import shutil
import os
import sys
import threading
from moviepy.editor import *
import cv2

progressRates = {}
threads = []

global model
model = None


class thread_with_trace(threading.Thread):
    def __init__(self, *args, **keywords):
        threading.Thread.__init__(self, *args, **keywords)
        self.killed = False

    def start(self):
        self.__run_backup = self.run
        self.run = self.__run
        threading.Thread.start(self)

    def __run(self):
        sys.settrace(self.globaltrace)
        self.__run_backup()
        self.run = self.__run_backup

    def globaltrace(self, frame, event, arg):
        if event == 'call':
            return self.localtrace
        else:
            return None

    def localtrace(self, frame, event, arg):
        if self.killed:
            if event == 'line':
                raise SystemExit()
        return self.localtrace

    def kill(self):
        self.killed = True

def run_model(user_id):
    pass

app = Flask(__name__, static_url_path="", template_folder="./")
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 8

#limiter = Limiter(app, default_limits=['1 per second'])

@app.route("/")
def index():
    return render_template('index.html')

@app.route('/lip2wav', methods=['GET', 'POST'])
def lip2wav():
  if request.method != "POST":
    return

  global threads
  if len(threads)>5:
      return {'error': 'too many requests'}, 429

  if not request.files.get('lip_video'):
    return {'error': 'video not found'}, 400

  try:
    global progressRates
    user_id = int(request.form.get('user_id'))
    print("hi1", user_id)
    lip_video = VideoFileClip(request.files['lip_video'].stream)

    if(lip_video.format!='mp4'):
      return {'error': 'video must be mp4'}, 401

    print("hi2", user_id)
    path = os.path.join("inputs", str(user_id))
    os.mkdir(path)
    print("hi3", user_id)
    dir1 = "inputs/"+str(user_id)+"/"+str(user_id)+".mp4"
    lip_video.save(dir1)
    progressRates[user_id] = 10
    print("hi4", user_id)

    t1 = thread_with_trace(target=run_model, args=[user_id])
    t1.user_id = user_id
    threads.append(t1)
    while threads[0].user_id!=user_id:
        print(str(user_id)+": ", threads[0].user_id)
        if threads[0].is_alive():
            threads[0].join()
    threads[0].start()
    threads[0].join(timeout=20)
    if threads[0].is_alive():
        threads[0].kill()
    print(threads.pop(0))
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

    progressRates[user_id] = 70

    print("hi5", user_id)
    result = send_file("demo/outputs/"+str(user_id)+"/outImg.gif", mimetype='image/gif')
    print("hi6", user_id)
    response = make_response(result)
    print("hi7", user_id)
    response.headers['Content-Type'] = str(user_id)
    print("hi8", user_id)
    return response

  except Exception:
    return {'error': 'error while loading input and/or output image files'}, 403

@app.route('/setup/<int:user_id>')
def setup(user_id):
    global progressRates
    progressRates[user_id] = 0
    return "0"

@app.route('/progress/<int:user_id>')
def progress(user_id):
    global progressRates
    return str(progressRates.get(user_id, 100))

@app.route('/remove/<int:user_id>')
def remove(user_id):
    try:
        for i in range(len(threads)):
            if threads[i].user_id == user_id and threads[i].is_alive():
                threads[i].kill()
                break
        path = os.path.join("demo/inputs", str(user_id))
        shutil.rmtree(path)
        path = os.path.join("demo/outputs", str(user_id))
        shutil.rmtree(path)
    except:
        pass
    progressRates.pop(user_id, None)
    return "0"

@app.route('/pending/<int:user_id>')
def pending(user_id):
    global threads
    for i in range(len(threads)):
        if threads[i].user_id == user_id:
            return str(i)
    if progressRates.get(user_id, 100) == 100:
        return "0"
    else:
        return str(len(threads))

@app.errorhandler(413)
def request_entity_too_large(error):
  return {'error': 'File Too Large'}, 413

@app.route('/healthz')
def health():
  return "healthy", 200

if __name__ == '__main__':
    '''
    import argparse
    import demo.demo as demo
    parser = argparse.ArgumentParser(description='Demo configurations.')
    parser.add_argument('--input', default='demo/inputs', type=str,
                        help='Path to the directory containing input images')
    parser.add_argument('--result', default='demo/outputs', type=str,
                        help='Path to the directory for saving results')
    parser.add_argument('--checkpoint', default='./pretrained/pretrained_celeba/checkpoint030.pth', type=str,
                        help='Path to the checkpoint file')
    parser.add_argument('--output_size', default=128, type=int, help='Output image size')
    parser.add_argument('--gpu', default=True, action='store_true', help='Enable GPU')
    parser.add_argument('--detect_human_face', default=True, action='store_true',
                        help='Enable automatic human face detection. This does not detect cat faces.')
    parser.add_argument('--render_video', default=True, action='store_true', help='Render 3D animations to video')
    args = parser.parse_args()
    model = demo.Demo(args)
    '''
    app.run(debug=False, port=80, host='0.0.0.0', threaded=True)