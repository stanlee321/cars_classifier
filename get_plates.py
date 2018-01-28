# -*- coding: utf-8 -*-
import cv2
import glob
import json
import numpy as np
import os
import subprocess
from subprocess import call




class GetPlate(Object):
	def __init__(self, directory, date):
		self.directory = directory
		self.date = date


	@staticmethod
	def get_json_from_api(image):

		print('IMAGE is:', image)
		
		cmd = ['curl','X', 'POST', '-F','image=@{}'.format(image),'https://api.openalpr.com/v2/recognize?recognize_vehicle=1&country=us&secret_key=sk_DEMODEMODEMODEMODEMODEMO']

		p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
		out, err= p.communicate()
		out = out.decode('utf-8')

		m = out
		n = json.dumps(m)  
		o = json.loads(n)  
		return str(o)


	def check_folder(path_to_file, extention):
		cv_img = []
		there_files = False
		path = path_to_file
		for img in glob.glob("{}*.{}".format(path,extention)):
		    n = cv2.imread(img)
		    cv_img.append(n)
		return cv_img

	def get_folders(self, path_to_clean):
		"""
			Get a list of the clean folders (usefull)
			, folders with jpg's and avi in folder
		"""
		print('Path to clean is: ', path_to_clean)	
		# List of folders in the <path_to_clean> input
		files = glob.glob(path_to_clean)
		for folder in files:
			# Get the whole names in the directory
			self.total_folders.append(folder)
			# Count for the elements in this folder
			try:
				files_in = os.listdir(folder) # folder is your directory path to look
				number_files = len(files_in)
				# If number of files in dir is <4 , append to the list of folders_to_clean
				if number_files < 4:
					print('Number of files in this folder {} : '.format(folder), number_files)
					self.logger.info('Number of files in this folder {} : '.format(folder) +  str(number_files))
					self.folders_to_clean.append(folder)
				else:
					pass
			except Exception as e:
				print('U are a log or something else:', e)
				self.logger.info('U are a log or something else:'+ str(e))
		return  self.folders_to_clean

	@staticmethod
	def get_plates(result):
		plates = result['candidates'][0]
		return plates
		#print(plates)

	@staticmethod
	def get_plate_region(result):
		region = result['coordinates'][0]
		return region


	@staticmethod
	def write_plate(image, region):
		# Save image with plate region labeled
		font = cv2.FONT_HERSHEY_SIMPLEX

		# CREATE the "detected" region in the image
		# and write his plate number over it
		px0 = region[0]['x']
		py0 = region[0]['y']
		px1 = region[2]['x']
		py1 = region[2]['y']

		textx = region[0]['x']
		texty = region[0]['y']

		img = cv2.imread(image)
		img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
		img = cv2.rectangle(img,(px0,py0),(px1,py1),(0,255,0),3)
		img = cv2.putText(img,plate,(textx,int(texty*0.95)), font, 1,(0,255,3),2,cv2.LINE_AA)
		scipy.misc.imsave(self.directory+'/{}/'.format(idd)+'{}_{}.jpg'.format(idd,date),img)
		cv2.imshow(self.directory+'/{}/'.format(idd)+'{}_{}.jpg'.format(idd,date),img)

	def get_information_of_images(file_exist, image, idd, date):
		# Check if there is images in WORKDIR
		# if there's image ...
		if files_exist :
			
			# idd and date from taked image
			information_of_the_image_as_json_file = GetPlate.get_json_from_api(image)
			information_of_the_image_as_json_file = information_of_the_image_as_json_file.replace('false','False')
			information_of_the_image_as_json_file = ast.literal_eval(information_of_the_image_as_json_file)
			print(information_of_the_image_as_json_file)
			# Transform result json to pandas df from the api , just the key == 'region' , the rest
			# does not bother us.
			result_pandas_df = json_normalize(information_of_the_image_as_json_file, 'results')
			# Possible plates from the above result in the format i.e :
			#								{'confidence': 94.38839, 'matches_template': 0, 'plate': '2070GKD'},
			#							    {'confidence': 81.850777, 'matches_template': 0, 'plate': '207QGKD'},

			if len(result_pandas_df) == 0:
				print('The API cant abble to detect any plate in the image')
			else:
				print('!', result_pandas_df)
			
				possible_plates = get_plates(result_pandas_df)

				# Working on the max confidence
				prob = possible_plates[0]['confidence']
				plate = possible_plates[0]['plate']

				# Possible region of interest in the format i.e : [{'x': 147, 'y': 135},
		 		#												  {'x': 349, 'y': 156},
				#												  {'x': 338, 'y': 246},
				#												  {'x': 138, 'y': 224}]

				possible_region = get_plate_region(result_pandas_df)

				# Working on the max confidence
				region = possible_region
				print('The posible plates are:')
				print(possible_plates)
				print('saving the max PROB. confidence to txt log ...')
				# writing log...
				np.save(self.directory+'/{}/'.format(idd)+'full_log_{}_{}.npy'.format(idd,date), information_of_the_image_as_json_file)
				with open(self.directory+'/{}/'.format(idd)+'{}_{}.txt'.format(idd,date),'a') as f:
					line = '{} {} {} {} {}'.format(idd, date, prob, plate, region)
					f.write(line)

				return region, prob, plate

		def __call__(self):

			folders = get_folders()
			for folder in folders:
				images = check_folder(folder,'jpg')
				for image in images:
					region, prob, plate = get_information_of_images(image)
					







def check_folder(path_to_file, extention):
	cv_img = []
	there_files = False
	path = path_to_file
	for img in glob.glob("{}*.{}".format(path,extention)):
	    n = cv2.imread(img)
	    cv_img.append(n)
	if len(cv_img) != 0:
		#print(cv_img)
		print('Folder not empty, folder len is ..', len(cv_img))
		there_files = True
		return there_files
	else:
		print('No files in {}!!'.format(path_to_file))
		return False



def get_plates(result):
	plates = result['candidates'][0]
	return plates
	#print(plates)


def get_plate_region(result):
	region = result['coordinates'][0]
	return region

#from pandas.io.json import json_normalize

def get_json_from_api(image):

	print(image)
	cmd = ['curl','X', 'POST', '-F','image=@{}'.format(image),'https://api.openalpr.com/v2/recognize?recognize_vehicle=1&country=us&secret_key=sk_DEMODEMODEMODEMODEMODEMO']
	
	p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
	out, err= p.communicate()
	out = out.decode('utf-8')

	m = out
	n = json.dumps(m)  
	o = json.loads(n)  
	return str(o)

def read_data(img_glob):
	files = []
	for fname in sorted(glob.glob(img_glob)):
		print('...',fname)

		#img = cv2.imread(fname)[:, :, 0].astype(np.float32) / 255.
		img = cv2.imread(fname)

	##############################################
	# HER LEFT TO CHABNGE BITWHISECHANGE FROM BGR TO RGB in img
		img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
	####################################
		date = fname.split("/")[1][0:19]

		code = fname.split("/")[1][-13:-4]

		files.append([fname,img,code,date])
		#os.remove(fname)

	return files


def send(FILE_TO_UPLOAD):
	cmd = './Dropbox-Uploader/dropbox_uploader.sh upload {} {}'.format(FILE_TO_UPLOAD,FILE_TO_UPLOAD)
	call([cmd], shell=True)

