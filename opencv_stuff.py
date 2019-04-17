import numpy as np
from PIL import ImageGrab
import cv2
import time
# import pyautogui
from directkeys import PressKey, W, A, S, D
import warnings
warnings.filterwarnings("ignore")

def canny(image):
	gray=cv2.cvtColor(image,cv2.COLOR_RGB2GRAY)
	blur=cv2.GaussianBlur(gray,(3,3),0)
	canny=cv2.Canny(blur,50,100)
	return canny

def display_lines(image,lines):
	line_image=np.zeros_like(image)
	if lines is not None:
		for line in lines:
			if line is not None:
				x1,y1,x2,y2=line.reshape(4)
				try:
					cv2.line(line_image,(x1,y1),(x2,y2),(255,0,0),10)
				except OverflowError:
					pass

	return line_image

def roi(image):
	# height=image.shape[0]
	# polygons=np.array([[(100,900),(1600,700),(700,250)]]) #for full res
	# polygons = np.array([[(200, 420), (900, 400), (500, 30)]]) #for windowed
	# polygons = np.array([[(450, 300),(9, 550),(1300, 786)]]) #first person
	polygons = np.array([[(10, 635), (10, 400), (430, 290),  (800, 400), (800, 635),
          ]])
	mask=np.zeros_like(image)
	cv2.fillPoly(mask,polygons,255)
	masked_image=cv2.bitwise_and(image,mask)
	return masked_image

def make_coordiantes(image,lines):
	try:
		slope,intercept=lines
		y1=image.shape[0]
		y2=int(y1*3/5)
		x1= int((y1-intercept)/slope)
		x2= int((y2-intercept)/slope)
		return np.array([x1,y1,x2,y2])
	except:
		pass

def average_slope_intercept(image,lines):
		left_fit=[]
		right_fit=[]

		try:
			for line in lines:
				try:
					x1,y1,x2,y2=line.reshape(4)
					coordinates=np.polyfit((x1,x2),(y1,y2),1)
					slope=coordinates[0]
					intercept=coordinates[1]
					if slope>0:
						right_fit.append((slope,intercept))
					else:
						left_fit.append((slope, intercept))
				except:
					pass
			left_fit_avg=np.average(left_fit,axis=0)
			right_fit_avg = np.average(right_fit, axis=0)
			left_line=make_coordiantes(image,left_fit_avg)
			right_line = make_coordiantes(image,right_fit_avg)
			return np.array([left_line,right_line])
		except:
			pass

# image=cv2.imread('test_images/9.png')
def process_img(image):
	lane_image=np.copy(image)

	canny_image=canny(lane_image)

	cropped_image=roi(canny_image)

	lines=cv2.HoughLinesP(cropped_image,6,np.pi/180,100,np.array([]),minLineLength=30,maxLineGap=15)

	average_lines=average_slope_intercept(lane_image,lines)

	line_image=display_lines(lane_image,average_lines)

	combo=cv2.addWeighted(lane_image,0.7,line_image,1,1)
	return combo


def main():
	# for i in list(range(4))[::-1]:
	# 	print(i + 1)
	# 	time.sleep(1)

	last_time = time.time()
	while True:
		# PressKey(W)
		screen = np.array(ImageGrab.grab(bbox=(40, 16, 853, 652)))

		last_time = time.time()
		new_screen = process_img(screen)
		cv2.imshow('window', new_screen)
		# cv2.imshow('window',cv2.cvtColor(screen, cv2.COLOR_BGR2RGB))
		if cv2.waitKey(25) & 0xFF == ord('q'):
			cv2.destroyAllWindows()
			break

main()