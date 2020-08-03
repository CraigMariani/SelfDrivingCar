import numpy as np
from PIL import ImageGrab
import cv2
import time
from directkeys import PressKey, ReleaseKey, E, Q, S, D, LEFT, RIGHT
import pyautogui
from numpy import ones, vstack
from numpy.linalg import lstsq
from statistics import mean

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


# region of interest, we are taking parts of the image that we want to focus on
def roi(img, verticies):
	mask = np.zeros_like(img) # create blank mask
	cv2.fillPoly(mask,verticies, 255) # fill the mask
	masked = cv2.bitwise_and(img, mask) # only the region of interest is left
	return masked


# similar to draw_lines but we are focusing on making them into lanes
def draw_lanes(img, lines, color=[0, 255, 255], thickness=3):
	

	try:
		# print('inside try')
		# find max value y for lane maker
		ys = []
		for i in lines:
			for ii in i:
				ys += [ii[1], ii[3]]

		min_y = min(ys) # for the horizon line
		max_y = 700 # bottom of the screen
		new_lines = []
		line_dict = {}

		for idx,i in enumerate(lines):
			# print('enumerating lines')
			for xyxy in i:
				# print('xyxy in i')

				# line is calculated from two points
				x_coords = (xyxy[0], xyxy[2])
				y_coords = (xyxy[1], xyxy[3])
				A = vstack([x_coords, ones(len(x_coords))]).T
				m, b = lstsq(A, y_coords)[0]

				# caclulate new xs y = mx+b
				x1 = (min_y-b) / m 
				x2 = (max_y-b) / m

				# add the new lines to line_dict and list new_lines
				line_dict[idx] = [m,b,[int(x1), min_y, int(x2), max_y]]
				new_lines.append([int(x1), min_y, int(x2), max_y])

			final_lanes = {}

			for idx in line_dict:
				# print('idx in line_dict')
				final_lanes_copy = final_lanes.copy() # create a copy of the line
				m = line_dict[idx][0] # slope of line
				b = line_dict[idx][1] # y intercept of line
				line = line_dict[idx][2] 

				if len(final_lanes) == 0:
					final_lanes[m] = [ [m,b,line] ]

				else:
					found_copy = False

					for other_ms in final_lanes_copy:
						# print('other_ms in final_lanes_copy')
						if not found_copy:
							# aslong as the slope and bias are in 10 percent they are considered the same line
							if abs(other_ms*1.2) > abs(m) > abs(other_ms*0.8):
								if abs(final_lanes_copy[other_ms][0][1]*1.2) > abs(b) > abs(final_lanes_copy[other_ms][0][1]*0.8):
									final_lanes[other_ms].append([m,b,line])
									found_copy = True
									break

							else:
								final_lanes[m] = [ [m,b,line]]
		line_counter={}

		for lanes in final_lanes:
			# print('lane {} in final_lanes'.format(lanes))
			line_counter[lanes] = len(final_lanes[lanes])

		top_lanes = sorted(line_counter.items(), key=lambda item: item[1])[::-1][:2]

		lane1_id = top_lanes[0][0]
		lane2_id = top_lanes[1][0]

		def average_lane(lane_data):
			# print('average_lane')
			x1s = []
			y1s = []
			x2s = []
			y2s = []

			for data in lane_data:
				# print('data in lane_data')
				x1s.append(data[2][0])
				y1s.append(data[2][1])
				x2s.append(data[2][2])
				y2s.append(data[2][3])
			return int(mean(x1s)), int(mean(y1s)), int(mean(x2s)), int(mean(y2s))

		l1_x1, l1_y1, l1_x2, l1_y2 = average_lane(final_lanes[lane1_id])
		l2_x1, l2_y1, l2_x2, l2_y2 = average_lane(final_lanes[lane2_id])

		return [l1_x1, l1_y1, l1_x2, l1_y2], [l2_x1, l2_y1, l2_x2, l2_y2]

	except Exception as e:
		# errror with final_lanes not being defined
		# print('line122')
		# print(str(e))
		pass


# returns the edges only of the image
def process_img(image):
	# converts image to gray
	original_image = image
	processed_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

	# used for finding edges in an image (canny edges)
	processed_img = cv2.Canny(processed_img, threshold1=200, threshold2=300)

	# output image is to choppy need to blur the image
	# we need to blur the lines after the edge detection or the blurs will be re-done
	processed_img = cv2.GaussianBlur(processed_img, (5,5), 0)

	# what we are using to split the scrapped image from the game
	# vertices = np.array([[10, 500], [10,300], [300, 200], [500, 200], [800,300], [800, 500]])
	vertices = np.array([[0,700], [0,332], [526, 254], [667, 254], [1250, 332], [1250, 700]], np.int32	)
	cut_out = np..array([[390,700], [390, 550], [830, 550], [830, 700]], np.int32)
	# get the roi(region of interest) of the processesd image
	processed_img = roi(processed_img,[vertices],[cut_out])

	# use houghlines algorithm to find major lines in image data
	# 						edges		, rho,theta     ,threshold, minlinelength(in pixels), maxLineGap
	# lines = cv2.HoughLinesP(processed_img, 1, np.pi/180, 180, np.array([]), 500000, 100 )
	lines = cv2.HoughLinesP(processed_img, 1, np.pi/180, 180, np.array([]), 100, 5)
	# returns array of arrays that contains the lines

	# draw_lines(processed_img, lines) # draw on the processed image with lines we just found

	try:
		# print('drawing lanes')
		l1, l2 = draw_lanes(processed_img, lines) # draw on the processed image wieth lines we just found
		cv2.line(original_image, (l1[0], l1[1]), (l1[2], l1[3]), [0,255,0], 30)
		cv2.line(original_image, (l2[0], l2[1]), (l2[2], l2[3]), [0,255,0], 30)

	except Exception as e:
		# print(str(e))
		pass
	try:
		for coords in lines:
			coords = coords[0]
			try:
				cv2.line(processed_img,  (coords[0], coords[1]), (coords[2], coords[3]), [255,0,0], 3)

			except Exception as e:
				# print(str(e))
				pass

	except Exception as e:
		pass

	return processed_img, original_image



def main():
	last_time = time.time()
	while(True):
		# grabe a screen image and format into numpy array
		screen = np.array(ImageGrab.grab(bbox=(0, 40, 1250, 700)))
		new_screen, original_image = process_img(screen)

		cv2.imshow('window', new_screen )
		cv2.imshow('window2',cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB))
		# display the time it took in the loop
		# print('Loop took {} seconds'.format(time.time() - last_time))
		last_time = time.time()

		# display what we have scrapped to the screen 
		# cv2.imshow('window', cv2.cvtColor(screen, cv2.COLOR_BGR2RGB))
		
		# exit command to end scrapping
		if cv2.waitKey(25) & 0xFF == ord('q'):
			cv2.destroyAllWindows()
			break



main()