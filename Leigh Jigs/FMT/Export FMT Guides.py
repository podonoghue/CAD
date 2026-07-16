#
# This is a FreeCAD script to export all Different Leigh FMT guide sizes.

import FreeCAD
import os.path
import datetime
import math
import Mesh

#==========================================================================
# Script to draw Mortise and Tenon outline (sketch)
#

import FreeCAD
import math

class DrawGuide:
			
	class SegmentHelper:
		
# class DrawGuide:.SegmentHelper
#========================================================
		__slots__ = ['sketch', 'reference', 'firstX', 'firstY', 'lastX', 'lastY', 'firstSegment', 'lastSegment']
		
		def __init__(self, sketch, reference):
			self.sketch  = sketch
			self.reference    = reference
			self.firstX  = None
			self.firstY  = None
			self.lastX   = None
			self.lastY   = None
			self.firstSegment = None
			self.lastSegment  = None

		def __addLineSegment(self, X1, Y1, X2, Y2):
			
			# Add segment
#			print(f"Edge # ({X1:4.2f},{Y1:4.2f}) -> ({X2:4.2f},{Y2:4.2f})" )

			segment = self.sketch.addGeometry(Part.LineSegment(App.Vector(X1, Y1, 0),  App.Vector(X2, Y2, 0)), self.reference)
			self.sketch.addConstraint(Sketcher.Constraint("Block", segment))
			
			if self.firstSegment == None:
				# Record first segment for closing
				self.firstSegment = segment
				
			if self.lastSegment != None:
				# Stitch segment together
				self.sketch.addConstraint(Sketcher.Constraint("Coincident", self.lastSegment, 2, segment, 1))
				
			# Record last segment for stitching
			self.lastSegment = segment
#			print('Edge #',segment+1,' (',X1,Y1,') -> (',X2,Y2,')' )
			
			return segment
					
		def addPoint(self, x, y):
			
			segment = None
			
			if (self.lastX != None):
				segment = self.__addLineSegment(self.lastX, self.lastY, x, y)
			else:
				self.firstX  = x
				self.firstY  = y
				self.lastX   = x
				self.lastY   = y
				
			self.lastX = x
			self.lastY = y
			return segment
		
		def closeOutline(self):
			# Close outline
			segment = self.__addLineSegment(self.lastX, self.lastY, self.firstX, self.firstY)
			
			# Stitch together
			if self.firstSegment != None:
				self.sketch.addConstraint(Sketcher.Constraint("Coincident", self.lastSegment, 2, self.firstSegment, 1))
			
# class DrawGuide: 
#========================================================
					
	__slots__ = ['sheet', 'sketch', 'pinDiameter', 'pinSpacing', 'lengthDelta', 'widthDelta', 'helper', 'referenceHelper'  ]
	
	
	def __init__(self, sheet, sketch, pinDiameter, reference=False):
		
		self.sheet  = sheet
		self.sketch = sketch

#		self.pinDiameter  = self.sheet.get("Pin_Bottom_Width")
		self.pinDiameter  = pinDiameter
		self.pinSpacing   = self.sheet.get("Pin_Spacing")
		
		self.lengthDelta  = self.sheet.get("Length_Delta")
		self.widthDelta   = self.sheet.get("Width_Delta")
			
		self.helper          = self.SegmentHelper(self.sketch, reference)
		self.referenceHelper = self.SegmentHelper(self.sketch, True)
		return
		
	def mapX(self, oldX, oldY):
		
		alpha = math.asin(2*oldY/self.pinSpacing)
		x     = oldX + ((self.pinSpacing/2) * (1-math.cos(alpha)))
#		x = oldX
		return x
		
	def mapY(self, oldX, oldY):
		
		y = 2*oldY
#		y = oldY
		return y
		
	def addPoint(self, X, Y):
		
		mappedX = self.mapX(X,Y)
		mappedY = self.mapY(X,Y)
		
		return self.helper.addPoint(mappedX, mappedY)
					
	def drawOutline(self):
	
		width			= self.sheet.get("Width")
		length			= self.sheet.get("Length")
		routerDiameter	= self.sheet.get("Router_Diameter")
		
		radius        = (width + routerDiameter + (self.widthDelta-self.pinDiameter)/2)/2
		reducedLength = length + routerDiameter - self.pinDiameter + self.lengthDelta - 2*radius

		# Make sure the widthDelta isn't overwhelming the length
		if (reducedLength < 0):
			reducedLength = 0.1
		
		self.addPoint(reducedLength/2, -radius)
		self.referenceHelper.addPoint(self.pinSpacing/2+(reducedLength/2), -radius)
		
		for angle in range(-85, 95, 5):
			radiansAngle = math.radians(angle)
			x = math.cos(radiansAngle)*radius+reducedLength/2
			y = math.sin(radiansAngle)*radius
			self.addPoint(x,y)
			self.referenceHelper.addPoint(x+self.pinSpacing/2,y)
		
		for angle in range(90, -95, -5):
			radiansAngle = math.radians(angle)
			x = -math.cos(radiansAngle)*radius-reducedLength/2
			y = math.sin(radiansAngle)*radius
			self.addPoint(x,y)
			self.referenceHelper.addPoint(x+self.pinSpacing/2,y)
			
		self.helper.closeOutline()
		self.referenceHelper.closeOutline()

	#sketch.addConstraint(Sketcher.Constraint('DistanceX',54,2,17,2,0)) 
		return

def drawGuide(doc):

	# Spreadsheet for parameters
	theSheet = doc.Spreadsheet
	
	theSketch = doc.getObjectsByLabel('Guide Outline')[0]
	
	theSketch.deleteAllGeometry()

	drawGuide = DrawGuide(theSheet,theSketch,theSheet.get("Pin_Bottom_Width"),False)
	drawGuide.drawOutline()
	
#	drawGuide = DrawGuide(theSheet,theSketch,0,True)
#	drawGuide.drawOutline()
	
#	print("Completed drawing M&T Guide outline")

#=====================================================================================================================

def export_object(obj, name):
	
	filepath = os.path.join(export_folder, name+'.3mf')
	objs = []
	objs.append(obj)
	try:
		if hasattr(Mesh, "exportOptions"):
			options = Mesh.exportOptions(filepath)
			Mesh.export(objs, filepath, options)
		else:
			Mesh.export(objs, filepath)
			
		FreeCAD.Console.PrintMessage(f"Exporting {name}\n")
	except Exception as e:
		FreeCAD.Console.PrintError(f"Error exporting {name} --> {export_folder}: {str(e)}\n")
	
	return


def Xexport_object(obj, name):
	if hasattr(obj, 'Shape') and obj.ViewObject.Visibility:
		filepath = os.path.join(export_folder, name+'.stl')
		try:
			obj.Shape.exportStl(filepath)
#			FreeCAD.Console.PrintMessage(f"Exporting {filename} --> {export_folder}\n")
			FreeCAD.Console.PrintMessage(f"Exporting {name}\n")
		except Exception as e:
			FreeCAD.Console.PrintError(f"Error exporting {name} --> {export_folder}: {str(e)}\n")

def get_design_object(label):
	for obj in doc.Objects:
		# Check if the object is a root object (not used by any other objects)
		if not obj.InList:
			if obj.Label == label:
				if hasattr(obj, 'Shape') and obj.ViewObject.Visibility:
					return obj
	return
		
# ==== Mortise & Tenon Guides ========================================

# List of tenon dimensions in mm
guideList  = [
#  width             Wdelta Ldelta Sdelta
# 1/4" FMT Guide Set: 5/16", 3/8", 1/2", 5/8", 3/4", 1", 1-1/4" and 1-1/2"
 [[25.4/4,'1/4"',     1.75, 1.0,  1.35],  [[25.4*5/16,'5/16"'],[25.4*3/8,'3/8"'],[25.4*1/2,'1/2"'],[25.4*5/8,'5/8"'],[25.4*3/4,'3/4"'],[25.4,'1"'],[25.4*5/4,'1-1/4"'],[25.4*3/2,'1-1/2"']]],
# 5/16" FMT Guide Set: 1/2", 3/4", 1", 1-1/4" and 1-1/2"
 [[25.4*5/16,'5/16"', 1.75, 1.0,  1.35],  [[25.4*1/2,'1/2"'],[25.4*3/4,'3/4"'],[25.4,'1"'],[25.4*5/4,'1-1/4"'],[25.4*3/2,'1-1/2"']]],
# 3/8" FMT Guide Set: 1", 1-1/2", 2" and 2-1/2"
 [[25.4*3/8,'3/8"',   1.75, 1.0,  1.35],  [[25.4,'1"'],[25.4*3/2,'1-1/2"'],[25.4*2,'2"'],[25.4*5/2,'2-1/2"']]],
# 1/2" FMT Guide Set: 1", 1-1/2", 2" and 2-1/2"
 [[25.4*1/2,'1/2"',   1.75, 1.0,  1.35],  [[25.4,'1"'],[25.4*3/2,'1-1/2"'],[25.4*2,'2"'],[25.4*5/2,'2-1/2"']]],
# 6mm FMT Guide Set: 8mm, 10mm, 15mm, 20mm, 25mm, 30mm, 35mm and 40mm
[[6,'6mm',            1.75, 1.0,  1.35],  [[8,'8mm'],  [10,'10mm'],[15,'15mm'],[20,'20mm'],[25,'25mm'],[30,'30mm'],[35,'35mm'],[40,'40mm'],[45,'45mm']]], 
# 8mm FMT Guide Set: 15mm, 20mm, 25mm, 30mm, 35mm and 40mm
[[8,'8mm',            1.75, 1.0,  1.35],  [[15,'15mm'],[20,'20mm'],[25,'25mm'],[30,'30mm'],[35,'35mm'],[40,'40mm'],[45,'45mm']]],
# 10mm FMT Guide Set: 25mm, 35mm, 45mm, 55mm and 65mm
[[10,'10mm',          1.75, 1.0,  1.35],  [[25,'25mm'],[35,'35mm'],[45,'45mm'],[55,'55mm'],[65,'65mm']]],
# 12mm FMT Guide Set: 25mm, 35mm, 45mm, 55mm and 65mm
[[12,'12mm',          1.75, 1.0,  1.35],  [[25,'25mm'],[35,'35mm'],[45,'45mm'],[55,'55mm'],[65,'65mm']]]]

class ExtendedEnum(Enum):

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))
    
class GuideSet(ExtendedEnum):
    Inch_1_4	= '1/4"'
    Inch_5_16	= '5/16"'
    Inch_3_8   	= '3/8"'
    Inch_1_2  	= '1/2"'
    mm_6		= "6 mm"
    mm_8		= "8 mm"
    mm_10		= "10 mm"
    mm_12		= "12 mm"
    
def export_MotiseAndTenon():
	label='M & T Guide'
	obj = get_design_object(label)
	if obj == None:
		print("'"+label+"' not found or not visible")
		return
	
	for guideSet in guideList:
		width       = guideSet[0][0]
		widthName   = guideSet[0][1]
		widthDelta  = guideSet[0][2]
		lengthDelta = guideSet[0][3]
		slotDelta   = guideSet[0][4]
		
		sheet.set("Width",        str(width))
		sheet.set("Width_Delta",  str(widthDelta))
		sheet.set("Length_Delta", str(lengthDelta))
		sheet.set("Slot_Delta",   str(slotDelta))
		
		for guide in guideSet[1]:
			length     = guide[0]
			lengthName = guide[1]

			fix = 0;			
#			if (width<=7):
#				if (length <= 7.95):
#					fix = 0.3
#				elif (length<=8):
#					fix = 0.81
#				
#			if (fix >0):
#				print("Width = ",  width, "Length = ", length, "Fix = ", fix)
				
			name = (widthName+'x'+lengthName+' ('+str(lengthDelta)+'-'+str(widthDelta)+'-'+str(slotDelta)+')').replace('/','.').replace('"','')
	#			print (name, '=>', f"{width:.1f}", f"{length:.1f}")
			
			sheet.set("Length", str(length))
			sheet.set("Fix", str(fix))
			sheet.set("Upper_Title", "'"+lengthName)
			sheet.set("Lower_Title", "'"+widthName)
			sheet.recompute()
			drawGuide(doc)
			doc.getObjectsByLabel('Slot Outline')[0].recompute()
			doc.recompute()
			export_object(obj=obj, name='FMT M and T Guide '+name)
			
	sheet.set("Width_Delta",  "0")
	sheet.set("Length_Delta", "0")
	sheet.set("Fix", ".01")

tests = [
[0,0],	# 0		-	1/4 x 5/16
[0,1],	# 1		-	1/4 x 3/8
[1,1],	# 2		-	5/16 x 3/4
[1,2],	# 3		-	5/16 x 1
[1,3],	# 4		-	5/16 x 1-1/4
[1,4],	# 5		-	5/16 x 1-1/2
[4,0],	# 6		-	6mm x 8mm
[4,1],	# 7		-	6mm x 10mm
[4,3],	# 8		-	6mm x 20mm
[4,6],	# 9		-	6mm x 35mm
[4,7],	# 10	-	6mm x 40mm
[4,8],	# 11	-	6mm x 45mm
[5,0],	# 12	-	8mm x 15mm
[5,1],	# 13	-	8mm x 20mm
[5,2],	# 14	-	8mm x 25mm
[5,3],	# 15	-	8mm x 30mm
[5,4],	# 16	-	8mm x 35mm
[5,5],	# 17	-	8mm x 40mm
[5,6],	# 18	-	8mm x 45mm
[6,0],	# 19	-	10mm x 25mm
[6,1],	# 20	-	10mm x 35mm
[6,2],	# 21	-	10mm x 45mm
[6,3],	# 22	-	10mm x 55mm
[6,4]	# 23	-	10mm x 65mm
]

def export_TestMotiseAndTenon():
	
	label='M & T Guide'
	obj = get_design_object(label)
	if obj == None:
		print("'"+label+"' not found or not visible")
		return
		
	test = tests[1]

	guideSet = guideList[test[0]]
	guide    = guideSet[1][test[1]]
	
	width       = guideSet[0][0]
	widthName   = guideSet[0][1]
	widthDelta  = guideSet[0][2]
	lengthDelta = guideSet[0][3]
	slotDelta   = guideSet[0][4]

	sheet.set("Width",        str(width))
	sheet.set("Width_Delta",  str(widthDelta))
	sheet.set("Length_Delta", str(lengthDelta))
	sheet.set("Slot_Delta",   str(slotDelta))
	
	length     = guide[0]
	lengthName = guide[1]
	
	fix = 0;			
#	if (width<=7):
#		if (length <= 7.95):
#			fix = 0.3
#		elif (length<=8):
#			fix = 0.81
#		
#	if (fix >0):
#		print("Width = ",  width, "Length = ", length, "Fix = ", fix)
		
	name = (widthName+'x'+lengthName+' ('+str(lengthDelta)+'-'+str(widthDelta)+'-'+str(slotDelta)+')').replace('/','.').replace('"','')
#			print (name, '=>', f"{width:.1f}", f"{length:.1f}")
	
	sheet.set("Length", str(length))
	sheet.set("Fix", str(fix))
	sheet.set("Upper_Title", "'"+lengthName)
	sheet.set("Lower_Title", "'"+widthName)
	sheet.recompute()
	
	drawGuide(doc)
   
	doc.getObjectsByLabel('Slot Outline')[0].recompute()
	doc.recompute()
#	export_root(name='FMT M and T Guide '+name, label='M & T Guide')
	export_object(obj=obj, name='FMT M and T Guide '+name)

# ==== Doweling Guides ==========================================

# List for dowels [extent, number of dowels]
dowelList = [
[20,2],
[25,2],
[30,3],
[35,3],
[40,3],
[50,4]]

def export_DowelCentres():
	label='Dowling Guides'
	obj = get_design_object(label)
	if obj == None:
		print("'"+label+"' not found or not visible")
		return
	
	for dowelSet in dowelList:
		extent  = dowelSet[0]
		number  = dowelSet[1]
		name = str(extent) + 'mm-' +str(number)
#		print(name)
		sheet.set("Dowel_Extent", str(extent))
		sheet.set("Dowel_Number", str(number))
		sheet.set("Upper_Title", "'"+str(extent)+"mm")
		sheet.set("Lower_Title", "'X "+str(number))
		sheet.recompute()
		doc.recompute()
#		export_root(name="FMT Dowling Guide "+name, label='Dowling Guides')
		export_object(obj=obj, name='FMT Dowling Guide '+name)

# ==== Y Axis Guides ==========================================

# List for [Width, Length, upper-name, lower-name, slotDelta]
yAxisList = [
# 6mm x 8mm, 6mm x 10mm, 6mm x 15mm, 6mm x 20mm
[6,        8,        '6mm',  '8mm' , 1.0],
[6,        10,       '6mm',  '10mm', 1.0],
[6,        15,       '6mm',  '15mm', 1.0],
[6,        20,       '6mm',  '20mm', 1.0],

# 8mm x 15mm, 8mm x 20mm
[8,        15,       '8mm',  '15mm', 1.0],
[8,        20,       '8mm',  '20mm', 1.0],

# 10mm x 25mm
[10,        25,      '10mm',  '25mm', 1.0],

# 12mm x 25mm
[12,        25,      '12mm',  '25mm', 1.0],

# 1/4"x 3/8", 1/4"x 1/2", 1/4"x 3/4"
[25.4*1/4, 25.4*3/8,  '1/4"', '3/8"', 1.0],
[25.4*1/4, 25.4*1/2,  '1/4"', '1/2"', 1.0],
#[25.4*1/4, 25.4*3/4,  '1/4"', '3/4"', 1.0],

# 5/16"x 1/2", 5/16"x 3/4"
[25.4*5/16, 25.4*1/2, '5/16"', '1/2"', 1.0],
[25.4*5/16, 25.4*3/4, '5/16"', '3/4"', 1.0],

# 1/2"x 1" + 1/4"x 3/4"
[25.4*1/2, 25.4*1,    '1/2",1/4"', '1",3/4"', 1.0],
]

def export_YAxisGuides():
	label='Y Tenon'
	obj = get_design_object(label)
	if obj == None:
		print("'"+label+"' not found or not visible")
		return
		
	for yAxis in yAxisList:
		width     = yAxis[0]
		length    = yAxis[1]
		lowerName = yAxis[2]
		upperName = yAxis[3]
		slotDelta = yAxis[4]
		name      = (lowerName + 'x' + upperName+' ('+str(slotDelta)+')').replace('/','.')
		sheet.set("Width",       str(width))
		sheet.set("Length",      str(length))
		sheet.set("Upper_Title", "'"+upperName)
		sheet.set("Lower_Title", "'"+lowerName)
		sheet.set("Slot_Delta",  str(slotDelta))
		sheet.recompute()
		doc.recompute()
#		export_root(name="Y-Axis Guide "+name, label='Y Tenon')
		export_object(obj=obj, name='Y-Axis Guide '+name)

# ==== Centering Jig ==========================================

# [Diameter, Name]
diameterList = [
[8,     '8 mm'],
[12,    '12 mm'],
[25.4/4,'1/4"'],
[25.4/2,'1/2"']]

def export_Centres():
	label='Centering'
	obj = get_design_object(label)
	if obj == None:
		print("'"+label+"' not found or not visible")
		return

	for entry in diameterList:
		diameter = entry[0]
		title    = entry[1]
		name     = title.replace('/','.')
		sheet.set("Centering_Post_Diameter", str(diameter))
		sheet.set("Centering_Title", "'"+title)
		sheet.recompute()
		doc.recompute()
#		export_root(name="FMT Centering jig "+name, label='Centering')
		export_object(obj=obj, name='FMT Centering jig '+name)


# Main document
doc = FreeCAD.activeDocument()

# Check if the document is saved (i.e., has a file name)
if not doc.FileName:
	FreeCAD.Console.PrintError("Document has not been saved. Please save the document first.\n")
	exit()

# Spreadsheet for parameters
sheet = doc.Spreadsheet

base_path = os.path.dirname(doc.FileName)
base_filename = os.path.splitext(os.path.basename(doc.FileName))[0]

# Get current date and time in the desired format
current_datetime = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# Ensure the "exported_YYYY-MM-DD_HH-mm-ss" subfolder exists
export_folder = os.path.join(base_path, f"FMT Guides - {current_datetime}")
if not os.path.exists(export_folder):
	os.makedirs(export_folder)

export_TestMotiseAndTenon()
#export_MotiseAndTenon()
#export_DowelCentres()
#export_YAxisGuides()
#export_Centres()
exit
