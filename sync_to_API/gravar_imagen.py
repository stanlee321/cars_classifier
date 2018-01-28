import cv2
import time
from subprocess import call

cap = cv2.VideoCapture(0)


while True:

	ret, frame = cap.read()

	cv2.imshow('frame', frame)

	ch = 0xFF & cv2.waitKey(1)
	if ch == ord('s'):
		cv2.imwrite('./placasAreconocer/placa.jpg', frame)
		cv2.imwrite('./casosReportados/placa.jpg', frame)
		break


	if ch == 27:
		break
time.sleep(1)
cv2.destroyAllWindows()