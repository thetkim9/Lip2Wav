import sys

if sys.version_info[0] < 3 and sys.version_info[1] < 2:
	raise Exception("Must be using >= Python 3.2")

from os import listdir, path

if not path.isfile('face_detection/detection/sfd/s3fd.pth'):
	raise FileNotFoundError('Save the s3fd model to face_detection/sfd/s3fd.pth \
							before running this script!')

import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor, as_completed
import numpy as np
import argparse, os, cv2, traceback, subprocess
from tqdm import tqdm
from glob import glob
from synthesizer import audio
from synthesizer.hparams import hparams as hp

import face_detection

# template = 'ffmpeg -loglevel panic -y -i {} -ar {} -f wav {}'
template2 = 'ffmpeg -hide_banner -loglevel panic -threads 1 -y -i {} -async 1 -ac 1 -vn -acodec pcm_s16le -ar 16000 {}'

def process_video_file(vfile, args, gpu_id):
	video_stream = cv2.VideoCapture(vfile)
	
	frames = []
	while 1:
		still_reading, frame = video_stream.read()
		if not still_reading:
			video_stream.release()
			break
		frames.append(frame)

	vidname = os.path.basename(vfile).split('.')[0]

	fulldir = path.join(args.preprocessed_root, vidname)
	os.makedirs(fulldir, exist_ok=True)
	#print (fulldir)

	wavpath = path.join(fulldir, 'audio.wav')
	print(wavpath)
	specpath = path.join(fulldir, 'mels.npz')

	command = template2.format(vfile, wavpath)
	subprocess.call(command, shell=True)

	batches = [frames[i:i + args.batch_size] for i in range(0, len(frames), args.batch_size)]

	i = -1
	for fb in batches:
		preds = fa[gpu_id].get_detections_for_batch(np.asarray(fb))

		for j, f in enumerate(preds):
			i += 1
			if f is None:
				continue

			cv2.imwrite(path.join(fulldir, '{}.jpg'.format(i)), f[0])


def process_audio_file(vfile, args, gpu_id):
	vidname = os.path.basename(vfile).split('.')[0]

	fulldir = path.join(args.preprocessed_root, vidname)
	os.makedirs(fulldir, exist_ok=True)

	wavpath = path.join(fulldir, 'audio.wav')
	print(wavpath)
	specpath = path.join(fulldir, 'mels.npz')

	wav = audio.load_wav(wavpath, hp.sample_rate)
	spec = audio.melspectrogram(wav, hp)
	lspec = audio.linearspectrogram(wav, hp)
	np.savez_compressed(specpath, spec=spec, lspec=lspec)

	
def mp_handler(job):
	vfile, args, gpu_id = job
	try:
		process_video_file(vfile, args, gpu_id)
		process_audio_file(vfile, args, gpu_id)
	except KeyboardInterrupt:
		exit(0)
	except:
		traceback.print_exc()

class subModel:
	def __init__(self):
		global fa
		fa = [face_detection.FaceAlignment(face_detection.LandmarksType._2D, flip_input=False,
													  device='cuda:{}'.format(id)) for id in range(1)]
		
def main(args):
	print('Started processing for {} with {} GPUs'.format(args.data_root, args.ngpu))

	filelist = glob(path.join(args.data_root, '*.mp4'))

	jobs = [(vfile, args, i%args.ngpu) for i, vfile in enumerate(filelist)]
	p = ThreadPoolExecutor(args.ngpu)
	futures = [p.submit(mp_handler, j) for j in jobs]
	_ = [r.result() for r in tqdm(as_completed(futures), total=len(futures))]

if __name__ == '__main__':
	pass
	#main(args)
