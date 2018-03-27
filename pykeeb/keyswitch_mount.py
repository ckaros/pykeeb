from openpyscad import *
from .pykeeb import *

class Keyswitch_mount:
	#width is X, length is Y
	thickness = 4
	alps_keyswitch = Import(r'C:\\Users\\Dean\\Documents\\GitHub\\pykeeb\\pykeeb\\models\\matias.stl').color('Gray')
	mx_keyswitch = Import(r'C:\\Users\\Dean\\Documents\\GitHub\\pykeeb\\pykeeb\\models\\cherry.stl').color('Gray')
	dsa_key = {1:Import(r'C:\\Users\\Dean\\Documents\\GitHub\\pykeeb\\pykeeb\\models\\dsa_1u.stl').color('White'), #18x18x8mm 
			   1.5:Import(r'C:\\Users\\Dean\\Documents\\GitHub\\pykeeb\\pykeeb\\models\\dsa_1.5u.stl').color('White'),
			   2:Import(r'C:\\Users\\Dean\\Documents\\GitHub\\pykeeb\\pykeeb\\models\\dsa_2u.stl').color('White')}

	def __init__(self, transformations, ik=False, switch_type='alps', mount_length=DSA_KEY_WIDTH, mount_width=DSA_KEY_WIDTH, mx_notches=True,proj=False,size=1,rotate=0):
		"""Sets up single switch-mount geometry, with transformations, W.R.T. switch type."""
		mx_length = 14.4
		mx_width = 14.4
		alps_length = 12.8
		alps_width = 15.5
		self.mount_length = mount_length 
		self.mount_width = mount_width
		self.switch_type = switch_type
		self.proj=proj
		self.size=size
		self.rotate=rotate
		
		mx_hole = Cube([mx_width, mx_length, self.thickness], center=True)
		nip_r = ((Cylinder(2.75,1,_fn=60).rotate([0,90,90]).translate([-7.2,-1.475,-1])))+\
		     (Cube([1,2.75,3]).rotate([0,-20,0]).translate([-7.2,-1.475,-1]))
		nip_l = nip_r.mirror(-1)
		if mx_notches == True:
			mx_hole = mx_hole - nip_l - nip_r

		alps_hole = Cube([alps_width, alps_length, self.thickness], center=True)
	
		if switch_type == 'mx':
			self.switch_mount = Cube([self.mount_width, self.mount_length, self.thickness], center=True) - mx_hole
		if switch_type == 'alps':
			self.switch_mount = Cube([self.mount_width, self.mount_length, self.thickness], center=True) - alps_hole 
		
		self.ignore_key = ik
		self.transformations = transformations

	def transform(self, x):
		"""Applies a list (tiers) of lists (each following the format [x-translate, y-translate, z-translate, x-rotate, y-rotate, z-rotate]) to the mount, one tier at a time."""
		if self.proj!= False:
			x=x.translate([0,0,-self.proj[0]]).rotate([self.proj[1],0,0]).translate([0,0,self.proj[0]]).translate([0,0,-self.proj[2]]).rotate([0,self.proj[3],0]).translate([0,0,self.proj[2]])
		if any(isinstance(l, list) for l in self.transformations):
			for tier in self.transformations:
				x = x.rotate(tier[3:]).translate(tier[0:3])
		else:
			x = x.rotate(self.transformations[3:]).translate(self.transformations[0:3])
		return x

	#def __add__(self, other):
		#return self.switch_mount.rotate(self.rotation).translate(self.origin) + other.switch_mount.rotate(other.rotation).translate(other.origin)

	def get_switch_at_location(self, hull=False):
		"""Returns the mount with transformations applied."""
		if self.ignore_key == True: return Cube(0).disable()
		if hull == True: #helpful for cutting away hulls/stuff in the way of switch hole. Need to think about how to improve.
			cutaway = self.switch_mount.hull() - self.switch_mount.hull().translate([-7,0,0]) #hack
			cutaway = cutaway.translate([0,0,-self.thickness]) #hack
			return self.transform(cutaway)
		else:
			return self.transform(self.switch_mount)

	def get_keyswitch(self):
		"""Returns model of switch in its place in the mount."""
		if self.switch_type == 'alps':
			return self.transform(self.alps_keyswitch.rotate([0, 0,0]).translate([0, 0, 14.5]))
		if self.switch_type == 'mx':
			return self.transform(self.mx_keyswitch.rotate([0, 0,0]).translate([0, 0, 14.5]))

	def get_keycap(self, down=False): 
		"""Returns model of keycap in it's rest position, or depressed position if 'down' == True."""
		if down: return self.transform(self.dsa_key[self.size].rotate([0,0,self.rotate]).translate([0, 0, 4]))
		return self.transform(self.dsa_key[self.size].rotate([0,0,self.rotate]).translate([0, 0, 7]))

	def get_side(self, side, thickness=.01, extrude=0, extend=True,zoffset=0,ztranslate=0):
		"""Returns Cube (rect. prism) of width 'thickness' that sticks out of the mount by length of 'extrude', specified by a given 'side' (front, back, left, or right).  'extend' will hull the returned Cube with the actual side of the mount."""
		if extrude > thickness and extend == True:
			thickness = extrude
		if side == 'left': cube = Cube([thickness, self.mount_length, self.thickness+zoffset]).translate([-self.mount_width/2 - extrude, -self.mount_length/2, -self.thickness/2+ztranslate])
		elif side == 'right': cube = Cube([thickness, self.mount_length, self.thickness+zoffset]).translate([self.mount_width/2 - thickness + extrude, -self.mount_length/2, -self.thickness/2+ztranslate])
		elif side == 'front': cube = Cube([self.mount_width, thickness, self.thickness+zoffset]).translate([-self.mount_width/2, self.mount_length/2 - thickness + extrude, -self.thickness/2+ztranslate])
		elif side == 'back': cube = Cube([self.mount_width, thickness, self.thickness+zoffset]).translate([-self.mount_width/2, -self.mount_length/2 - extrude, -self.thickness/2+ztranslate])
		if self.ignore_key == True: cube = cube.disable()
		return self.transform(cube)

	def get_front(self, thickness=.01, extrude=0, extend=True,zoffset=0,ztranslate=0): 
		"""Wrapper.  See get_side()."""
		return self.get_side('front', thickness, extrude, extend,zoffset,ztranslate)

	def get_back(self, thickness=.01, extrude=0, extend=True,zoffset=0,ztranslate=0): 
		"""Wrapper.  See get_side()."""
		return self.get_side('back', thickness, extrude, extend,zoffset,ztranslate)

	def get_left(self, thickness=.01, extrude=0, extend=True,zoffset=0,ztranslate=0): 
		"""Wrapper.  See get_side()."""
		return self.get_side('left', thickness, extrude, extend,zoffset,ztranslate)

	def get_right(self, thickness=.01, extrude=0, extend=True,zoffset=0,ztranslate=0): 
		"""Wrapper.  See get_side()."""
		return self.get_side('right', thickness, extrude, extend,zoffset,ztranslate)

	def get_corner(self, position, x, y, x_extrude=0, y_extrude=0, extend=True,ztranslate=0):
		"""Returns Cube (rect. prism) of length/width x/y that extrudes of the mount's corner (specified by fl, fr, bl, or br, for 'front left', 'front right', etc) by lengths x_extrude and y_extrude.  'extend will hull the returned Cube with the actual corner of the mount."""
		if extend == True:
			if x_extrude > x:
				x = x_extrude
			if y_extrude > y:
				y = y_extrude
		corner = Cube([x, y, self.thickness])
		if position == 'fl': corner = corner.translate([-self.mount_width/2 - x_extrude, self.mount_length/2 - y + y_extrude, -self.thickness/2+ztranslate])
		elif position == 'fr': corner = corner.translate([self.mount_width/2 - x + x_extrude, self.mount_length/2 - y + y_extrude, -self.thickness/2+ztranslate])
		elif position == 'bl': corner = corner.translate([-self.mount_width/2 - x_extrude, -self.mount_length/2 - y_extrude, -self.thickness/2+ztranslate])
		elif position == 'br': corner = corner.translate([self.mount_width/2 - x + x_extrude, -self.mount_length/2 - y_extrude, -self.thickness/2+ztranslate])
		if self.ignore_key == True: corner = corner.disable()
		return self.transform(corner)
