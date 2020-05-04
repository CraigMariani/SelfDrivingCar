import numpy as np
from PIL import ImageGrab
import cv2
import time



'''
put the game at the top right hand corner of the screen

Game Controls:
Q : Brake
W : Horn
E : Accelerate
S : Drive Gear
D : Rear Gear
Arrow Keys : Turn
'''

# printscreen_pil = ImageGrab.grab(bbox=(0, 40, 1250, 700))
# printscreen_numpy = np.array(printscreen_pil.getdata(),dtype='uint8')\
# .reshape((printscreen_pil.size[1],printscreen_pil.size[0],3))
last_time = time.time()
while(True):
	# grabe a screen image and format into numpy array
	screen = np.array(ImageGrab.grab(bbox=(0, 40, 1250, 700)))
	
	# display the time it took in the loop
	print('Loop took {} seconds'.format(time.time() - last_time))

	# display what we have scrapped to the screen 
	cv2.imshow('window', screen)
	# cv2.imshow('window', cv2.cvtColor(screen, cv2.COLOR_BGR2RGB))
	
	# exit command to end scrapping
	if cv2.waitKey(25) & 0xFF == ord('q'):
		cv2.destroyAllWindows()
		break