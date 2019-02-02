import cv2
from math import ceil
count=0
mergeRegions = []
lastFrom = -1
lastTo = -1

def toNormalizedRgb(r, g, b):
	sm = r + g + b
	#if(sm==0): print sm
	return [r / sm, g / sm, b / sm]

def classifySkin(r,g,b):
	if(r==0 or g==0 or b==0): return False
	rgbClassifier = (r > 95) and (g > 40) and (g < 100) and (b > 20) and ((max(r, g, b) - min(r, g, b)) > 15) and (abs(r - g) > 15) and (r > g) and (r > b)
	nurgb = toNormalizedRgb(r, g, b)
	nr = nurgb[0]
	ng = nurgb[1]
	nb = nurgb[2]
	#if(nr==0 and ng==0): normRgbClassifier = False
	#elif(ng==0): normRgbClassifier = (r * b / pow(r + g + b, 2)) > 0.107 and (r * g / pow(r + g + b, 2)) > 0.112
	normRgbClassifier = (nr / ng) > 1.185 and (r * b / pow(r + g + b, 2)) > 0.107 and (r * g / pow(r + g + b, 2)) > 0.112
	hsv = toHsvTest(r, g, b)
	h = hsv[0]
	s = hsv[1]
	hsvClassifier = h > 0 and h < 35 and s > 0.23 and s < 0.68
	return rgbClassifier | normRgbClassifier | hsvClassifier

def toHsvTest(r, g, b):
	#print r,g,b
	h = 0
	mx = max(r, g, b)
	mn = min(r, g, b)
	dif = mx - mn
	#print type(dif),dif
	if (dif==0):
		return [-1, 1 - 3 * (min(r, g, b) / (r + g + b)), 1 / 3 * (r + g + b)]#otherwise NaN
	if(mx == r):
		h = (g - b) / dif
	elif(mx == g):
		h = 2 + (g - r) / dif
	else:
		h = 4 + (r - g) / dif
	h *= 60
	if(h < 0):
	  h += 360
	return [h, 1 - 3 * (min(r, g, b) / (r + g + b)), 1 / 3 * (r + g + b)]


def scan(src):
	skinRegions = []
	skinMap = []
	detectedRegions = []
	detRegions = []#[]] * 100000
	totalSkin = 0
	def	addMerge(frm, to):
		#if(frm==287 or to==287): print "yo"
		global mergeRegions
		global lastFrom
		global lastTo
		lastFrom = frm
		lastTo = to
		lnt = len(mergeRegions)
		fromIndex = -1
		toIndex = -1
		region=-1#initialized
		rlen=-1#initialized
		#print lnt,"f",mergeRegions
		while(lnt):
			lnt-=1
			region = mergeRegions[lnt]
			rlen = len(region)
			while(rlen):
				rlen-=1
				if(region[rlen] == frm):
					fromIndex = lnt
				if(region[rlen] == to):
					toIndex = lnt
		#if(to==628 or frm==628): print "yo"
		if(fromIndex != -1 and toIndex != -1 and fromIndex == toIndex):
			return
		if(fromIndex == -1 and toIndex == -1):
			#print mergeRegions.append([frm,to]),"f"
			return mergeRegions.append([frm, to])
		if(fromIndex != -1 and toIndex == -1):
			return mergeRegions[fromIndex].append(to)
		if(fromIndex == -1 and toIndex != -1):
			return mergeRegions[toIndex].append(frm)
		if(fromIndex != -1 and toIndex != -1 and fromIndex != toIndex):
			mergeRegions[fromIndex].extend(mergeRegions[toIndex])
			del mergeRegions[toIndex]
			#mergeRegions = [].append(mergeRegions.slice(0, toIndex), mergeRegions.slice(toIndex + 1))
	imageData = cv2.imread(src,cv2.CV_LOAD_IMAGE_COLOR)
	height, width, depth = imageData.shape
	#print imageData.shape
	#canvas.width = img.width
	#canvas.height = img.height
	totalPixels = width * height
	#ctx.drawImage(img, 0, 0)
	#imageData = ctx.getImageData(0, 0, canvas.width, canvas.height).data
	imageData= imageData.flatten()
	#print imageData[0],imageData[1],imageData[2],imageData[3],imageData[4],imageData[5]
	length = imageData.size
	#print totalPixels
	i=0
	u=0
	#raw_input("press key")
	#print length
	while(i<length):
		#if(i>1500): exit()
		#raw_input(length)
		#print i,"f"
		#if(i==562497): print "gg",imageData[i],imageData[i+1],imageData[i+2]
		r = float(imageData[i+2])
		#print type(r)
		g = float(imageData[i + 1])
		b = float(imageData[i])
		#print r,g,b
		#raw_input("D")
		x = u % width
		y = u / width
		#print u,width,x,y
		#if( y==375): exit()
		if(classifySkin(r, g, b)):
			#print "y"
			global count
			count+=1
			#print count
			skinMap.append({'checked': False, 'region': 0,'skin': True, 'y': y,  'x': x,'id': u})
			region = -1
			#print skinMap[0],"y"
			checkIndexes = [u - 1, u - width - 1, u - width, u - width+1]
			checker = False
			o = 0
			index=0
			#print type(skinMap[0])
			while(o<4):
				#raw_input("while o")
				index = checkIndexes[o]
				#print skinMap[index]['region'],region,lastFrom,lastTo
				try:
					if(skinMap[index] and skinMap[index]['skin']):
						#print "work"
						#print detectedRegions
						#exit()
						#print x,y,skinMap[index]['x'],skinMap[index]['y'],skinMap[index]['region'],region,lastFrom,lastTo
						if(skinMap[index]['region'] != region and region != -1 and lastFrom != region and lastTo != skinMap[index]['region']):
							#print region
							#print "hh"
							addMerge(region, skinMap[index]['region'])
							#print lastFrom,lastTo
							#exit()
							#print "again"
						region = skinMap[index]['region']
						checker = True
				except IndexError:
				#	print "d"
					pass
				o+=1
			#print "c",count
			#if(count==100):
			#	print len(mergeRegions)
			#	exit()				
			if(not checker):
				#print "here"
				#print len(detectedRegions)
				skinMap[u]['region'] = len(detectedRegions)
				detectedRegions.append([skinMap[u]])
				#print detectedRegions
				#exit()
				#continue
			else:
				#print detectedRegions
				#exit()
				#if((not detectedRegions[region])==True): print "yoyo"
				#if(region > -1):
				
				if(not detectedRegions[region]):
					detectedRegions[region] = []
				skinMap[u]['region'] = region
				detectedRegions[region].append(skinMap[u])
				#print detectedRegions
				#exit()
				#print "ever"
		else:
			skinMap.append({ 'checked': False, 'region': 0,'skin': False, 'y': y,  'x': x,'id': u,  })	
			#print skinMap[0][0],"d"
		#if(i==1500): print skinMap
		i+=3
		u+=1
	#print mergeRegions
	length = len(mergeRegions)
	#print length
	#print skinMap
	#print detectedRegions[627]
	#ss=0
	#for ff in mergeRegions:
	#	ss+=len(ff)
	#	print ff
	#print ss
	#print length,"l"
	#exit()
	detRegions = [[] for i in range(length)]
	#detRegions = [[:]]*length;
	#print detRegions
	#print len(detRegions),"g"
	test=0
	while(length):
		#raw_input("while length")
		length-=1
		region = mergeRegions[length]
		rlen = len(region)
		#print rlen
		while(rlen):
			test+=1
			rlen-=1
			index = region[rlen]
			#print detRegions[length]
			
			#print detectedRegions[index]
			#exit()
			#print index
			#print len(detectedRegions[index])
			detRegions[length].extend(detectedRegions[index])
			#print detRegions
			#exit()
			detectedRegions[index] = []
		#print detRegions
		#exit()
	#print detectedRegions
	#print len(detRegions)
	#print len(detectedRegions)
	length = len(detectedRegions)
	#print length
	while(length):
		length-=1
		#raw_input("while length2")
		if(len(detectedRegions[length]) > 0):
			detRegions.append(detectedRegions[length])
	length = len(detRegions)
	#print length
	i=0
	#print skinRegions
	while(i < length):
		#raw_input("while i length2")
		if(len(detRegions[i]) > 30):#no of pixels in region is greater than 30
			skinRegions.append(detRegions[i])
		i+=1
	length = len(skinRegions)
	#print length #this is detected final no of regions
	if(length < 3):
		print "Valid"
		exit()
	sorted = False
	temp=1#initialized
	while(not sorted):
		#raw_input("while sorted")
		sorted = True
		i=0
		while(i<length-1):
			if(len(skinRegions[i])< len(skinRegions[i + 1])):
				sorted = False
				temp = skinRegions[i]
				skinRegions[i] = skinRegions[i + 1]
				skinRegions[i + 1] = temp
			i+=1
	#ss=0
	#for ff in skinRegions:
	#	ss=len(ff)
	#	print ss
	#print ss
	#exit()
	while(length):
		#raw_input("while length3")
		length-=1
		print len(skinRegions[length])
		totalSkin += len(skinRegions[length])
	print totalSkin,totalPixels
	if((totalSkin*1.0 / totalPixels) * 100 < 15):
		print "Valid"
	elif((len(skinRegions[0]) *1.0/ totalSkin) * 100 < 35 and (len(skinRegions[1])*1.0 / totalSkin) * 100 < 30 and (len(skinRegions[2])*1.0 / totalSkin) * 100 < 30):
		print "Valid"
	elif((len(skinRegions[0]) *1.0/ totalSkin) * 100 < 45):
		print "Valid"
	elif(len(skinRegions) > 60):#doubtful
		print "Valid"
	else: print "Hawww:Nude"
	
#for i in range(1,4):
#	imagepath='tests/images/'+str(i)+'.jpg'
#	print imagepath
imagepath='tests/images/4.jpg'
res=scan(imagepath)
#imageData = cv2.imread(imagepath)
#b,g,r = cv2.split(imageData)
#print imageData[2][3][0],imageData[2][3][1],imageData[2][3][2]
#imageData= imageData.flatten()
#print imageData
#height,width,depth=imageData.shape
#imageData.size
#length=height*width*(depth+1)
#print width, height, length
#print 'Image: ' + imagepath + '   Result: ' + res
#print image
#print height, width, depth


#cv2.imshow("Faces found", imageData)
#cv2.waitKey(0)

#375 500 3
#gbr

#difference in number of pixels read in javascript and python
