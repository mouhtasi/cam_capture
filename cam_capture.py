from VideoCapture import Device
import ImageDraw, sys
import PIL
import os, time, datetime, thread, threading

res = (640, 480)
cam = Device(showVideoWindow=0)    #initialize camera instance
cam.setResolution(res[0],res[1])   #set resolution

shots = 0
ctr = 0

def ftp_thread(f, filename):
	'''Thread which uploads filename using spftp instance f.'''
	f.write('put '+ filename+'\n')
	
def save(ctr_array):
	'''Capture image and return its filename.'''
	print('Capturing image.')
	filetime = time.strftime("%d-%m-%Y+%H.%M.%S", time.localtime())
	filename = str(filetime) + '-' + str(ctr_array) + ".jpg"
	cam.saveSnapshot(filename, quality=80, timestamp=1)
	return filename

def diff_image(img1, img2, pix_threshold=20, img_threshold=20):
	'''Compare 2 images to detect possible motion. This funtion is 
	originally from http://huangjiahua.livejournal.com/39912.html'''
	if not img1 or not img2: return False
	resize_res = (320,240)
	img1 = img1.getdata()
	img1 = img1.resize(resize_res)
	img2 = img2.getdata()
	img2 = img2.resize(resize_res)
	pixel_count = len(img1)
	pixdiff = 0
	for i in range(pixel_count):
		if abs(sum(img1[i]) - sum(img2[i])) > pix_threshold:
			pixdiff += 1
			diffperc = pixdiff / (pixel_count/100.0)
			if diffperc > img_threshold:
				# motion detected
				return True
			
def action(array):
	'''Actions to be run when motion is detected.'''
	array_delay = .5    # delay between shots
	ctr_array = 1
	thread_ctr = 1
	while ctr_array <= array:		
		if thread_ctr > 3:
			thread_ctr = 1
			
		filename = save(ctr_array)

		print('Shot: ' + str(ctr_array))
		print('thread_ctr: '+str(thread_ctr)+'\n')
		if thread_ctr == 1:
			thread.start_new_thread(ftp_thread, (f1,filename))
		elif thread_ctr == 2:
			thread.start_new_thread(ftp_thread, (f2,filename))
		elif thread_ctr == 3:
			thread.start_new_thread(ftp_thread, (f3, filename))
		#print('Image saved.\nUploading via SFTP.')
		ctr_array += 1
		thread_ctr += 1
		time.sleep(array_delay)

if __name__ == "__main__":
	f1 , g1 = os.popen4('psftp cam')  # 'cam' is the name of my saved
	f1.write('cd captures\n')           #PuTTY session, and 'captures' is
	f2 , g2 = os.popen4('psftp cam')    #the name of the folder where the
	f2.write('cd captures\n')           #photos are saved on the remote comp
	f3 , g3 = os.popen4('psftp cam')
	f3.write('cd captures\n')
	
	array = 5    #number of shots to take when motion is detected
		
	while 1:		
		shot_a = cam.getImage()
		time.sleep(.5)
		shot_b = cam.getImage()
		
		motion = diff_image(shot_a, shot_b)
		
		if motion:
			action(array)
	f1.close()
	g1.close()
	f2.close()
	g2.close()
	f3.close()
	g3.close()
	