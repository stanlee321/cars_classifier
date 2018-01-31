
from cars_detector.cars_cropper import CarsCropper
from cars_detector.cars_cropper import GetFolders
from get_plates import 	PlateRecognition
import argparse




if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Process SubFolders in a Root folder')

	parser.add_argument('-folder', '--cleanFolder', default = None, type=str, help="format is Year-month-day")

	args = parser.parse_args()


	# If -folder flag is set, path_to_clean = <-folder flab>
	if args.cleanFolder != None:
		home_dir = os.getenv('HOME')
		today_date = datetime.datetime.now().strftime('%Y-%m-%d')
		path_to_folder = home_dir + '/' + args.cleanFolder

	# Else it will search for the todays report and set path_to_clean to actual day
	else:
		home_dir = os.getenv('HOME')
		today_date = datetime.datetime.now().strftime('%Y-%m-%d')
		path_to_folder =  home_dir + '/' + today_date + '_reporte'

	get_folders 	= GetFolders()
	cars_cropper    = CarsCropper()

	# Cut the cars in image
	folders_to_work = get_folders(path_to_folder)
	for folder in folders_to_work:
		cars_cropper(path_to_images_dir = folder)

	print('##################################################################')
	print('FINISHED THE CROPPING PART, STARTING THE RECOGNITION OF PLATES....')
	print('##################################################################')
	# Make Plate recognition
	plate_recognition = PlateRecognition()
	plate_recognition(path_to_folder)