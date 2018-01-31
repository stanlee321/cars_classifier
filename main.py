import argparse
import datetime
from cars_cropper import CarsCropper
from cars_cropper import GetFolders
from get_plates import 	PlateRecognition





if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Process SubFolders in a Root folder')

	parser.add_argument('-folder', '--cleanFolder', default = None, type=str, help="format is Year-month-day")

	args = parser.parse_args()


	# If -folder flag is set, path_to_clean = <-folder flab>
	if args.cleanFolder != None:
		path_to_folder = args.cleanFolder

	# Else it will search for the todays report and set path_to_clean to actual day
	else:
		
		today_date = datetime.datetime.now().strftime('%Y-%m-%d')
		path_to_folder =  today_date + '_reporte'

	get_folders 	= GetFolders()
	cars_cropper    = CarsCropper()

	print(path_to_folder)
	# Cut the cars in image
	folders_to_work = get_folders(path_to_folder)
	print('folders to work', folders_to_work)
	for folder in folders_to_work:
		cars_cropper(path_to_images_dir = folder)

	print('##################################################################')
	print('FINISHED THE CROPPING PART, STARTING THE RECOGNITION OF PLATES....')
	print('##################################################################')
	# Make Plate recognition
	plate_recognition = PlateRecognition()
	plate_recognition(path_to_folder)