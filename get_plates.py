# -*- coding: utf-8 -*-

import cv2
import glob
import json
import numpy as np
import os
import subprocess
from subprocess import call
from pandas.io.json import json_normalize
import ast
import sqlite3
import shutil

class PlateRecognition():
	def __init__(self, folder='red'):
		self.db = os.getenv('HOME') + '/WORKDIR'+ '/' + folder +'/' +'rename.db'
		self.conn = sqlite3.connect(self.db)
		self.c =  self.conn.cursor()
		self.c.execute('CREATE TABLE IF NOT EXISTS rename_table(dtime TEXT, folder TEXT, image TEXT, plate TEXT, prob TEXT)')
		
	def dynamic_data_entry(self, dtime, folder, image, plate, prob):

		conn = self.conn
		c = self.c

		DTIME = dtime
		FOLDER = folder
		IMAGE = image
		PLATE = plate
		PROB = prob
		c.execute("INSERT INTO rename_table(dtime, folder, image, plate, prob) VALUES (?,?,?,?,?)",\
			(DTIME, FOLDER, IMAGE, PLATE, PROB))
		conn.commit()

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

	def check_folder(self, path_to_folders, extention):
		cv_img = []
		path = path_to_folders
		for img in glob.glob("{}/*.{}".format(path, extention)):
		    #n = cv2.imread(img)
		    cv_img.append(img)
		return cv_img

	def get_folders(self, path_to_clean):
		"""
			Get a list of the clean folders (usefull)
			, folders with jpg's and avi in folder
		"""
		folders_to_clean = []
		total_folders = []
		print('Path to clean is: ', path_to_clean)	
		# List of folders in the <path_to_clean> input
		files = glob.glob(path_to_clean)
		for folder in files:
			# Get the whole names in the directory
			total_folders.append(folder)
			# Count for the elements in this folde
		return total_folders

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
	def write_plate(image, region, plate):
		# Save image with plate region labeled
		path = image.split('/')
		directory = path[1] + '/'+path[2] + '/'+ path[3] + '/'+ path[4] + '/' + path[5] + '/'
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
		img = cv2.putText(img, plate,(textx,int(texty*0.95)), font, 1,(0,255,3),2,cv2.LINE_AA)
		save_in = '/'+ directory + "{}_rekogn.jpg".format(path[6])
		cv2.imwrite(save_in, img)
		#scipy.misc.imsave(directory+'/{}/'.format(idd)+'{}_{}.jpg'.format(idd,date),img)
		#cv2.imshow(directory+'/{}/'.format(idd)+'{}_{}.jpg'.format(idd,date),img)

	@staticmethod
	def get_information_of_images(image):
		# Check if there is images in WORKDIR
		# if there's image ...
		
		# idd and date from taked image
		information_of_the_image_as_json_file = PlateRecognition.get_json_from_api(image)
		information_of_the_image_as_json_file = information_of_the_image_as_json_file.replace('false','False')
		information_of_the_image_as_json_file = ast.literal_eval(information_of_the_image_as_json_file)
		# Transform result json to pandas df from the api , just the key == 'region' , the rest
		# does not bother us.
		result_pandas_df = json_normalize(information_of_the_image_as_json_file, 'results')
		# Possible plates from the above result in the format i.e :
		#								{'confidence': 94.38839, 'matches_template': 0, 'plate': '2070GKD'},
		#							    {'confidence': 81.850777, 'matches_template': 0, 'plate': '207QGKD'},

		if len(result_pandas_df) == 0:
			return ['The API cant abble to detect any plate in the image']
		else:
			possible_plates = PlateRecognition.get_plates(result_pandas_df)

			# Working on the max confidence
			prob = possible_plates[0]['confidence']
			plate = possible_plates[0]['plate']			
			possible_region = PlateRecognition.get_plate_region(result_pandas_df)
			region = possible_region

			return [region, prob, plate, information_of_the_image_as_json_file]


	@staticmethod
	def leer_DB():
		# Read old metadata
		# Init DB
		db = os.getenv('HOME') + '/WORKDIR'+ '/' + 'red'+'/' +'rename.db'
		conn = sqlite3.connect(db,timeout=1)
		c =  conn.cursor()
		#c.execute("SELECT * FROM stufftoPlot WHERE value=3 AND keyword='Python'")
		#c.execute("SELECT keyword,unix,value FROM stufftoPlot WHERE unix >1515634491")
		c.execute("SELECT folder, image, plate, prob FROM rename_table")
		#data = c.fetchone()
		data = c.fetchall()

		homework = []
		for row in data:
			metadata = data
			homework.append(metadata)
		#print('HOMEWORK', homework)

		c.close()
		conn.close()
		return homework


	def __call__(self, work_in_folder):

		path_to_folders = os.getenv('HOME') + '/WORKDIR'+ '/' + work_in_folder + '/*'

		folders = self.get_folders(path_to_folders)
		for folder in folders:
			print('Working in folder:', folder)
			images = self.check_folder(folder,'jpg')
			for image in images:
				print('Working in image: ', image)
				information =  PlateRecognition.get_information_of_images(image)
				if len(information)>1:
					region, prob, plate, full_data = information[0], information[1], information[2], information[3] 
					#print(region, prob, plate, full_data)
					print('IMAGE BEFORE IS....____----->>>>', image)
					PlateRecognition.write_plate(image, region, plate)
					print('saving the max PROB. confidence to txt log ...')
					# writing log...
					path = image.split('/')
					directory = '/'+ path[1] + '/' + path[2] + '/'+ path[3] + '/'+ path[4] + '/' + path[5] + '/'
					np.save(directory + '{}.npy'.format(path[6][0:-4]), full_data)
					
					folder = directory
					image = path[6][0:-4]
					dtime = path[6][0:-6]
					self.dynamic_data_entry(dtime, folder, image, plate, prob)
					#with open(directory +'{}.txt'.format(path[6][0:-4]),'a') as f:
					#	line = '{} {} {}'.format(plate, prob, region)
					#	f.write(line)

				else:
					print(information)
				# Close coneccions



if __name__ == '__main__':
	folder = 'red'
	demo = "/home/stanlee321/WORKDIR/red/2018-01-17_07-35-55/2018-01-17_07-35-55_0wm.jpg"
	platereko = PlateRecognition()
	#platereko(folder)
	db = platereko.leer_DB()
	for row in db[0]:
		old_folder = row[0][0:-1]
		new_folder = row[0][0:-1] + '_{}_{}'.format(row[2], row[3])
		try:
			os.rename(old_folder, new_folder)
		except:
			print('This dude dont exist')

	#platereko.get_json_from_api(demo)
	#information = platereko.get_information_of_images(demo)
	#region, prob, plate, full_data = information[0], information[1], information[2], information[3] 
	#platereko.write_plate(demo, region)
