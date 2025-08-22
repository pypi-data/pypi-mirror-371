import os
from astropy.io import fits
import pyds9 
import numpy as np
import string, random


class nf9():

	def __init__(self,ds9_id=None):
		# targets = pyds9.ds9_targets()
		# print("Found",targets)


		# if ds9_id is None and targets==None or targets is None:
		# 	self.ds9_id = self.id_generator()
		# else:
		# 	self.ds9_id = targets[0]

		# print("Connecting to",ds9_id)
		# self.nf_ds9 = pyds9.DS9(ds9_id)


		if ds9_id is not None:
			print("Connecting to",ds9_id)
			self.nf_ds9 = pyds9.DS9(ds9_id)
			self.ds9_id = ds9_id

		if ds9_id is None:
			targets = pyds9.ds9_targets()
			print("Found",targets)
			if targets is None:
				print("No connection")
				return
			if len(targets)>1:
				print("Choose one")
				return
				# ds9_id = self.id_generator()
				# print(ds9_id)
			ds9_id = targets[0]
			self.nf_ds9 = pyds9.DS9(ds9_id)
			self.ds9_id = ds9_id

		# if ds9_id is None and targets==None or targets is None:
		# 	self.ds9_id = self.id_generator()
		# else:
		# 	self.ds9_id = targets[0]

		# print("Connecting to",ds9_id)
		# self.nf_ds9 = pyds9.DS9(ds9_id)


		self.disp_z1 = None
		self.disp_z2 = None
		self.imhist_z1 = None
		self.mhist_z2 = None


	def id_generator(self,size=6, chars=string.ascii_uppercase + string.digits):
		return ''.join(random.choice(chars) for _ in range(size))




	def check_dir(self):
		"""Ensure that DS( looks in the right place"""
		dir = os.getcwd()
		self.nf_ds9.set("cd %s" % (dir))

	def reinit(self):
		self.nf_ds9 = pyds9.DS9(self.ds9_id)

	def ext_parser(self,name):
		if "[" in name:
			filename = name.split("[")[0]
			ext = name.split("[")[-1].split("]")[0]
			try:
				ext = int(ext)
			except:
				pass
		else:
			filename = name
			ext = 0

		return filename,ext

	def lock(self):
		self.check_dir()
		self.nf_ds9.set("lock frame image" )

	def disp(self,f,frame=1,z1=None,z2=None,zoom=None):
		"""Display a file, a list of files or a numpy array into DS9, defaulting to frame 1. Data range can be specified with z1,z2 
		as well as a zoom factor"""
		# global disp_z1
		# global disp_z2

		self.check_dir()

		if type(f)==np.ndarray or type(f)==np.ma.core.MaskedArray:
			if frame!=None:
				self.nf_ds9.set("frame %d" % (frame))
			self.nf_ds9.set_np2arr(f)
			return

		if type(f)==type(" ") and "*" in f:
			import glob
			files = glob.glob(f.split("[")[0])
			ext = ""
			if len(f.split("["))>1:
				ext = "["+f.split("[")[1]

			files = [x+ext for x in files]
		else:
			ext = ""
			if len(f.split("["))>1:
				ext = "["+f.split("[")[1]
			files = [f]

		#print "files:",files,ext

		for i,f in enumerate(files):
			if i>0:
				frame = i+1
			if not os.path.isfile(f.split("[")[0]):
				print(f,"Not found")
				return

			if z1==None and self.disp_z1!=None:
				z1 = disp_z1
			if z1!=None:
				disp_z1 = z1

			if z2==None and self.disp_z2!=None:
				z2 = disp_z2
			if z2!=None:
				disp_z2 = z2
		
			if frame!=None:
				self.nf_ds9.set("frame %d" % (frame))
			self.nf_ds9.set("file %s" % (f))
			if z1==None and z2==None:
				self.nf_ds9.set("scale zscale")

			#print "check:",z1,z2
			if z1!=None and z2!=None:
				self.nf_ds9.set("scale limits %e %e" % (z1,z2))
			if zoom!=None:
				self.nf_ds9.set("zoom to %d" % (zoom))
	
	def print(self,frame,oname):
		"""Produce an image of the current display"""
		self.nf_ds9.set("frame %d" % (frame))
		self.nf_ds9.set('saveimage %s' % (oname))

	def circle(self,i,j,r,frame=None,c="green",ra=False):
		"""Draw a circle defined by (i,j) and radius r (pixels)"""
		self.check_dir()

		if frame!=None:
			self.nf_ds9.set("frame %d" % (frame))
		if ra==False:
			self.nf_ds9.set('regions', 'physical; circle(%f, %f, %f) # color = %s' % (i,j,r,c))
		else:
			self.nf_ds9.set('regions', 'fk5; circle(%f, %f, %f) # color = %s' % (i,j,r,c))

	def ellipse(self,i,j,a,b,theta,c="green"):
		"""Draw an ellipse defined by (i,j) and axes (a,b) (pixels)"""
		self.check_dir()
		self.nf_ds9.set('regions', 'physical; ellipse(%f, %f, %f, %f, %f) # color = %s' % (i,j,a,b,theta,c))


	def box(self,i,j,a,b,t,c="green"):
		"""Draw a box defined by (i,j) and size (a,b) (pixels)"""
		self.check_dir()

		self.nf_ds9.set('regions', 'image; box(%f, %f, %f, %f, %f) # color = %s' % (i,j,a,b,t,c))

	def pan(self,i,j,frame=None,world=False):
		"""Pan DS9 to a specific image coordinate"""
		self.check_dir()
		if frame!=None:
			self.nf_ds9.set("frame %d" % (frame))
		if not world:
			self.nf_ds9.set("pan to %d %d" % (i,j))
		else:
			self.nf_ds9.set("pan to %f %f wcs fk5" % (i,j))

	def zoom(self,s,frame=None):
		"""Zoom on image by factor s"""
		self.check_dir()
		if frame!=None:
			self.nf_ds9.set("frame %d" % (frame))
		self.nf_ds9.set("zoom to %d" % (s))

	def scale(self,z1,z2,frame=None):
		"""Set display scale to z1<z2"""
		self.check_dir()
		if frame!=None:
			self.nf_ds9.set("frame %d" % (frame))
		self.nf_ds9.set("scale limits %e %e" % (z1,z2))


	def tvm(self,x,y,frame=None,label=None,fontsize=7,color="green",circle=None, world=False, xoff=0, yoff=0, origin = 0):
		"""Rough implementation of the old rvm command. This lets you mark regions on an image using circles. Input can be 
		a catalog (default is photutils (i.e. starts at 0,0 and uses xcentroid,ycentroid) format with X_IMAGE, Y_IMAGE coordinated). x and y can specify different column names 
		in the catalog. cat can be the name of a text file or an astropy Table. If cat is None, coordinates can be passed as
		x and y and these can be lists"""
		import tempfile, string
		from astropy.table import Table

		self.check_dir()

		if frame!=None:
			self.nf_ds9.set("frame %d" % (frame))
		font="helvetica %d normal roman" % (fontsize)

		
		if not world:
			if circle==None:
				circle = 5
			coordsys = "image"
		else:
			if circle==None:
				circle = 5*0.128/3600
			coordsys = "J2000"
		

		x = np.array(x) 
		y = np.array(y)

		if origin==0 and world is False:
			x = x + 1
			y = y + 1

			

		x_image = x
		y_image = y
		a_image = x_image*0.+circle
		b_image = x_image*0.+circle
		theta_image = x_image*0.


		vg1 = np.isnan(a_image)
		vg2 = np.isnan(b_image)
		b_image[vg2] = 0.
		tmp = tempfile.mkstemp()[1]

		lines = ""
		for i in range(len(x_image)):
			if label!=None:
				t = "%s; ellipse(%f,%f,%f,%f,%f) # color = %s text={%s} font=\"%s\"\n" % (coordsys,x_image[i],y_image[i],a_image[i],b_image[i],theta_image[i],color,label[i],font)
			else:
				t = "%s; ellipse(%f,%f,%f,%f,%f) # color = %s font=\"%s\"\n" % (coordsys,x_image[i],y_image[i],a_image[i],b_image[i],theta_image[i],color,font)
			lines = lines + t
		self.nf_ds9.set("regions",lines)

	def imexam(self,frame=None):
		"""Causes DS9 to wait for a mouse click with a blinking cursor. Upon mouse click, returns (i,j) and the value of the pixel"""
		if frame!=None:
			self.nf_ds9.set("frame %d" % (frame))

		s = self.nf_ds9.get("iexam coordinate image")
		ws = s.split()
		x = float(ws[0])
		y = float(ws[1])
		s = self.nf_ds9.get("data image {} {} 1 1 yes".format(x,y))

		return x,y,float(s)



	
