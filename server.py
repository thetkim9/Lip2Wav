from flask import Flask, render_template, request, send_file, make_response
#from flask_limiter import Limiter
from PIL import Image, ImageOps
import time
import shutil
import os
import sys
import threading
#from moviepy.editor import *
import cv2
import argparse
import preprocess as pre
import preprocess_speakers as prespe
import complete_test_generate as run

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

def preprocess(user_id):
    parser = argparse.ArgumentParser()
    parser.add_argument('--ngpu', help='Number of GPUs across which to run in parallel', default=1, type=int)
    parser.add_argument('--batch_size', help='Single GPU Face detection batch size', default=32, type=int)
    parser.add_argument("--data_root", help="Root folder of the LRW dataset", default="input/"+str(user_id))
    parser.add_argument("--preprocessed_root", help="Root folder of the preprocessed dataset", default="input_preprocessed/")
    args = parser.parse_args()

    pre.main(args)

def run_model(user_id):
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', "--data_root", help="Speaker folder path", default="input_preprocessed/"+str(user_id))
    parser.add_argument('-r', "--results_root", help="Speaker folder path", default="output/"+str(user_id))
    args = parser.parse_args()

    run.run_model(args)

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

  print(request.files)

  if not request.files.get('lip_video'):
    return {'error': 'video not found'}, 400

  try:
    global progressRates
    user_id = int(request.form.get('user_id'))
    print("hi1", user_id)

    #save video
    path = os.path.join("input", str(user_id))
    os.mkdir(path)
    lip_video = request.files.get('lip_video')
    with open("input/"+str(user_id)+"/"+str(user_id)+".mp4", 'wb') as f:
        f.write(lip_video.getvalue())

    '''
    if(lip_video.format!='mp4'):
      return {'error': 'video must be mp4'}, 401
    '''

    #preprocessing
    print(user_id, "hi2")
    t1 = thread_with_trace(target=preprocess, args=[user_id])
    t1.user_id = user_id
    threads.append(t1)
    while threads[0].user_id != user_id:
        if threads[0].is_alive():
            threads[0].join()
    threads[0].start()
    threads[0].join(timeout=15)
    if threads[0].is_alive():
        threads[0].kill()
    print(threads.pop(0))
    print(user_id, "first GPU task complete~~~~~~~~~~~~~~~~~")

    print(user_id, "hi3")
    parser = argparse.ArgumentParser()
    parser.add_argument('--num_workers', help='Number of workers to run in parallel', default=8, type=int)
    parser.add_argument("--preprocessed_root", help="Folder where preprocessed files will reside", default="input_preprocessed/"+str(user_id))
    args = parser.parse_args()

    prespe.dump(args)
    progressRates[user_id] = 40

    print("hi4", user_id)

    t1 = thread_with_trace(target=run_model, args=[user_id])
    t1.user_id = user_id
    threads.append(t1)
    while threads[0].user_id!=user_id:
        if threads[0].is_alive():
            threads[0].join()
    threads[0].start()
    threads[0].join(timeout=20)
    if threads[0].is_alive():
        threads[0].kill()
    print(threads.pop(0))
    print(user_id, "second GPU task complete~~~~~~~~~~~~~~~~~")

    progressRates[user_id] = 90

    print("hi5", user_id)
    result = send_file("output/"+str(user_id)+"/wavs/"+str(user_id)+".wav", mimetype='audio/wav')
    print("hi6", user_id)
    response = make_response(result)
    print("hi7", user_id)
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
    '''
    try:
        for i in range(len(threads)):
            if threads[i].user_id == user_id and threads[i].is_alive():
                threads[i].kill()
                break
        path = os.path.join("input", str(user_id))
        shutil.rmtree(path)
        path = os.path.join("input_preprocessed", str(user_id))
        shutil.rmtree(path)
        path = os.path.join("output", str(user_id))
        shutil.rmtree(path)
    except:
        pass
    progressRates.pop(user_id, None)
    '''
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
    path = os.path.join(".", "input")
    os.mkdir(path)
    path = os.path.join(".", "output")
    os.mkdir(path)

    run.sif.hparams.set_hparam('eval_ckpt', "../tacotron_model.ckpt-313000")
    app.run(debug=False, port=80, host='0.0.0.0', threaded=True)