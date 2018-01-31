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

		self.folder = folder
		
	@staticmethod
	def create_db(db_name):
		conn = sqlite3.connect(db_name)
		c =  conn.cursor()
		c.execute('CREATE TABLE IF NOT EXISTS rename_table(dtime TEXT, folder TEXT, image TEXT, plate TEXT, prob TEXT)')

	@staticmethod
	def dynamic_data_entry(db_name, dtime, folder, image, plate, prob):

		DTIME = dtime
		FOLDER = folder
		IMAGE = image
		PLATE = plate
		PROB = prob

		conn = sqlite3.connect(db_name)
		c =  conn.cursor()
		c.execute("INSERT INTO rename_table(dtime, folder, image, plate, prob) VALUES (?,?,?,?,?)",\
			(DTIME, FOLDER, IMAGE, PLATE, PROB))
		conn.commit()

		c.close()
		conn.close()

	@staticmethod
	def leer_DB(db_name):

		conn = sqlite3.connect(db_name)
		c =  conn.cursor()
		c.execute("SELECT folder, image, plate, prob FROM rename_table")
		data = c.fetchall()
		homework = []
		for row in data:
			metadata = data
			homework.append(metadata)
		c.close()
		conn.close()
		return homework

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
		    cv_img.append(img)
		return cv_img

	def get_folders(self, path_to_clean):
		"""
			Get a list of the clean folders (usefull)
			, folders with jpg's and avi in folder
		"""
		folders_to_clean = []
		total_folders = []
		files = glob.glob(path_to_clean)
		for folder in files:
			total_folders.append(folder)
		return total_folders

	@staticmethod
	def get_plates(result):
		plates = result['candidates'][0]
		return plates

	@staticmethod
	def get_plate_region(result):
		region = result['coordinates'][0]
		return region

	@staticmethod
	def write_plate(image_path_name,image_name, folder_to_save, region, plate):
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

		img = cv2.imread(image_path_name)
		img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
		img = cv2.rectangle(img,(px0,py0),(px1,py1),(0,255,0),3)
		img = cv2.putText(img, plate,(textx,int(texty*0.95)), font, 1,(0,255,3),2,cv2.LINE_AA)
		save_in = folder_to_save + "{}_rekogn.jpg".format(image_name)
		cv2.imwrite(save_in, img)

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
		if len(result_pandas_df) == 0:
			return ['The API cant abble to detect any plate in the image']
		else:
			possible_plates = PlateRecognition.get_plates(result_pandas_df)

			# Working on the max confidence
			prob 			= possible_plates[0]['confidence']
			plate 			= possible_plates[0]['plate']			
			possible_region = PlateRecognition.get_plate_region(result_pandas_df)
			region 			= possible_region
			return [region, prob, plate, information_of_the_image_as_json_file]


	def __call__(self, work_in_folder):

		path_to_work_folder = os.getenv('HOME') + '/' + work_in_folder
		path_to_folders     =  path_to_work_folder + '/*'
		path_to_db 			= os.getenv('HOME') + '/WORKDIR' + '/' +'rename_{}.db'.format(work_in_folder)
		# Create DB for this case:
		PlateRecognition.create_db(path_to_db)

		folders = self.get_folders(path_to_folders)
		for folder in folders:
			print('Working in folder:', folder)
			images = self.check_folder(folder,'jpg')
			for image in images:
				print('Working in image: ', image)
				information =  PlateRecognition.get_information_of_images(image)
				if len(information)>1:
					path = image.split('/')

					old_folder_path = '/'.join(path[0:5]) + '/'
					old_folder_name = path[3]
					dtime           = path[4]
					image_name      = path[-1]
					image_path_name =  '/'.join(path)

					# get information from Json
					region, prob, plate, full_data = information[0], information[1], information[2], information[3] 
					
					# write the image with this info
					PlateRecognition.write_plate(image_path_name, image_name, old_folder_path, region, plate)
					
					# record the full log from JSON in a npy
					np.save(old_folder_path + '{}.npy'.format(image_name), full_data)
					
					# Commit information to DB
					PlateRecognition.dynamic_data_entry(path_to_db, dtime, old_folder_path, image_name, plate, prob)
				else:
					print(information)
				# Close coneccions
		print('STARING RENANaming...')
		db_info = PlateRecognition.leer_DB(path_to_db)
		for row in db_info[0]:
			old_folder = row[0][0:-1]
			new_folder = row[0][0:-1] + '_{}_{}'.format(row[2], row[3])
			try:
				os.rename(old_folder, new_folder)
			except:
				print('This dude dont exist', row[0])

if __name__ == '__main__':
	folder = 'red'
	platereko = PlateRecognition()
	platereko(folder)


	#platereko.get_json_from_api(demo)
	#information = platereko.get_information_of_images(demo)
	#region, prob, plate, full_data = information[0], information[1], information[2], information[3] 
	#platereko.write_plate(demo, region)
