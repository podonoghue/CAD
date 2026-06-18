#
# This is a FreeCAD script to export all Different Leigh FMT guide sizes.

import FreeCAD
import os.path
import datetime

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

def export_object_to_stl(obj, name):
	if hasattr(obj, 'Shape') and obj.ViewObject.Visibility:
		filename = name + ".stl"
		filepath = os.path.join(export_folder, filename)
		try:
			obj.Shape.exportStl(filepath)
#			FreeCAD.Console.PrintMessage(f"Exporting {filename} --> {export_folder}\n")
			FreeCAD.Console.PrintMessage(f"Exporting {filename}\n")
		except Exception as e:
			FreeCAD.Console.PrintError(f"Error exporting {filename} --> {export_folder}: {str(e)}\n")


def export_root(name,label):
	for obj in doc.Objects:
		# Check if the object is a root object (not used by any other objects)
		if not obj.InList:
			if obj.Label == label:
				export_object_to_stl(obj, name)

# ==== Mortise & Tenon Guides ========================================

# List of tenon dimensions in mm
guideList  = [
#  width             Wdelta Ldelta 
# 1/4" FMT Guide Set: 5/16", 3/8", 1/2", 5/8", 3/4", 1", 11/4" and 1 1/2"
 [[25.4/4,'1/4"',    1.1, 1.25],  [[25.4*5/16,'5/16"'],[25.4*3/8,'3/8"'],[25.4*1/2,'1/2"'],[25.4*5/8,'5/8"'],[25.4*3/4,'3/4"'],[25.4,'1"'],[25.4*5/4,'1-1/4"'],[25.4*3/2,'1-1/2"']]],
# 5/16" FMT Guide Set: 1/2", 3/4", 1", 1 1/4" and 1 1/2"
 [[25.4*5/16,'5/16"',0.5, 0.50],  [[25.4*1/2,'1/2"'],[25.4*3/4,'3/4"'],[25.4,'1"'],[25.4*5/4,'1-1/4"'],[25.4*3/2,'1-1/2"']]],
# 3/8" FMT Guide Set: 1", 1 1/2", 2" and 2 1/2"
 [[25.4*3/8,'3/8"',  1.1, 1.25],  [[25.4,'1"'],[25.4*3/2,'1-1/2"'],[25.4*2,'2"'],[25.4*5/2,'2-1/2"']]],
# 1/2" FMT Guide Set: 1", 1 1/2", 2" and 2 1/2"
 [[25.4*1/2,'1/2"',  1.1, 1.25],  [[25.4,'1"'],[25.4*3/2,'1-1/2"'],[25.4*2,'2"'],[25.4*5/2,'2-1/2"']]],
# 6mm FMT Guide Set: 8mm, 10mm, 15mm, 20mm, 25mm, 30mm, 35mm and 40mm
[[6,'6mm',           1.3, 0.50],  [[8,'8mm'],  [10,'10mm'],[15,'15mm'],[20,'20mm'],[25,'25mm'],[30,'30mm'],[35,'35mm'],[40,'40mm']]],
# OK@2 8mm FMT Guide Set: 15mm, 20mm, 25mm, 30mm, 35mm and 40mm
[[8,'8mm',           0.5, 0.50],  [[15,'15mm'],[20,'20mm'],[25,'25mm'],[30,'30mm'],[35,'35mm'],[40,'40mm']]],
# 10mm FMT Guide Set: 25mm, 35mm, 45mm, 55mm and 65mm
[[10,'10mm',         1.0, 0.50],  [[25,'25mm'],[35,'35mm'],[45,'45mm'],[55,'55mm'],[65,'65mm']]],
# 12mm FMT Guide Set: 25mm, 35mm, 45mm, 55mm and 65mm
[[12,'12mm',         1.1, 1.25],  [[25,'25mm'],[35,'30mm'],[45,'45mm'],[55,'55mm'],[65,'65mm']]]]

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
	for guideSet in guideList:
		width       = guideSet[0][0]
		widthName   = guideSet[0][1]
		widthDelta  = guideSet[0][2]
		lengthDelta = guideSet[0][3]
		
		sheet.set("Width",        str(width))
		sheet.set("Width_Delta",  str(widthDelta))
		sheet.set("Length_Delta", str(lengthDelta))
		
		for guide in guideSet[1]:
			length     = guide[0]
			lengthName = guide[1]

			fix = 0;			
			if (width<=7):
				if (length <= 7.95):
					fix = 0.3
				elif (length<=8):
					fix = 0.81
				
			if (fix >0):
				print("Width = ",  width, "Length = ", length, "Fix = ", fix)
				
			name       = (widthName+'x'+lengthName).replace('/','.').replace('"','')
	#			print (name, '=>', f"{width:.1f}", f"{length:.1f}")
			
			sheet.set("Length", str(length))
			sheet.set("Fix", str(fix))
			sheet.set("Upper_Title", "'"+lengthName)
			sheet.set("Lower_Title", "'"+widthName)
			sheet.recompute()
			doc.getObjectsByLabel('Slot Outline')[0].recompute()
			doc.recompute()
			export_root(name='FMT M and T Guide '+name, label='M & T Guide')

tests = [
[0,0],	# 0		-	1/4" x 5/16
[1,1],	# 1		-	5/16 x 3/4
[1,2],	# 2		-	5/16 x 1
[1,3],	# 3		-	5/16 x 1-1/4
[1,4],	# 4		-	5/16 x 1-1/2
[4,0],	# 5		-	6mm x 8mm
[4,1],	# 6		-	6mm x 10mm
[4,3],	# 7		-	6mm x 20mm
[4,5],	# 8		-	6mm x 30mm
[4,7],	# 9		-	6mm x 40mm
[5,1],	# 10	-	8mm x 20mm
[5,2],	# 11	-	8mm x 25mm
[5,3],	# 12	-	8mm x 30mm
[5,4],	# 13	-	8mm x 35mm
[5,5],	# 14	-	8mm x 40mm
[6,0],	# 15	-	10mm x 25mm
[6,1],	# 16	-	10mm x 35mm
[6,2],	# 17	-	10mm x 45mm
[6,3],	# 18	-	10mm x 55mm
[6,4]	# 19	-	10mm x 65mm
]

def export_TestMotiseAndTenon():

	test = tests[15]

	guideSet = guideList[test[0]]
	guide    = guideSet[1][test[1]]
	
	width       = guideSet[0][0]
	widthName   = guideSet[0][1]
	widthDelta  = guideSet[0][2]
	lengthDelta = guideSet[0][3]

	sheet.set("Width",        str(width))
	sheet.set("Width_Delta",  str(widthDelta))
	sheet.set("Length_Delta", str(lengthDelta))
	
	length     = guide[0]
	lengthName = guide[1]
	
	fix = 0;			
	if (width<=7):
		if (length <= 7.95):
			fix = 0.3
		elif (length<=8):
			fix = 0.81
		
	if (fix >0):
		print("Width = ",  width, "Length = ", length, "Fix = ", fix)
		
	name       = (widthName+'x'+lengthName).replace('/','.').replace('"','')
#			print (name, '=>', f"{width:.1f}", f"{length:.1f}")
	
	
	sheet.set("Length", str(length))
	sheet.set("Fix", str(fix))
	sheet.set("Upper_Title", "'"+lengthName)
	sheet.set("Lower_Title", "'"+widthName)
	sheet.recompute()
	doc.getObjectsByLabel('Slot Outline')[0].recompute()
	doc.recompute()
	export_root(name='FMT M and T Guide '+name, label='M & T Guide')

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
		export_root(name="FMT Dowling Guide "+name, label='Dowling Guides')

# ==== Y Axis Guides ==========================================

# List for [Width, Length, upper-name, lower-name]
yAxisList = [
# 8mm x 10mm, 8mm x 15mm, 8mm x 20mm
[6,        8,        '6mm',  '8mm' ],
[6,        10,       '6mm',  '10mm'],
[6,        15,       '6mm',  '15mm'],
[6,        20,       '6mm',  '20mm'],

# 8mm x 15mm, 8mm x 20mm
[8,        15,       '8mm',  '15mm'],
[8,        20,       '8mm',  '20mm'],

# 10mm x 25mm
[10,        25,      '10mm',  '25mm'],

# 12mm x 25mm
[12,        25,      '12mm',  '25mm'],

# 1/4"x 3/8", 1/4"x 1/2", 1/4"x 3/4"
[25.4*1/4, 25.4*3/8,  '1/4"', '3/8"'],
[25.4*1/4, 25.4*1/2,  '1/4"', '1/2"'],
[25.4*1/4, 25.4*3/4,  '1/4"', '3/4"'],

# 5/16"x 1/2", 5/16"x 3/4"
[25.4*5/16, 25.4*1/2, '5/16"', '1/2"'],
[25.4*5/16, 25.4*3/4, '5/16"', '3/4"'],

# 1/2"x 1"
[25.4*1/2, 25.4*1,    '1/2"', '1"'],
]

def export_YAxisGuides():
	for yAxis in yAxisList:
		width     = yAxis[0]
		length    = yAxis[1]
		lowerName = yAxis[2]
		upperName = yAxis[3]
		name      = (lowerName + 'x' + upperName).replace('/','.')
		sheet.set("Width",  str(width))
		sheet.set("Length", str(length))
		sheet.set("Upper_Title", "'"+upperName)
		sheet.set("Lower_Title", "'"+lowerName)
		sheet.recompute()
		doc.recompute()
		export_root(name="Y-Axis Guide "+name, label='Y Tenon')

# ==== Centering Jig ==========================================

# [Diameter, Name]
diameterList = [
[8,     '8 mm'],
[12,    '12 mm'],
[25.4/4,'1/4"'],
[25.4/2,'1/2"']]

def export_Centres():
	for entry in diameterList:
		diameter = entry[0]
		title    = entry[1]
		name     = title.replace('/','.')
		sheet.set("Centering_Post_Diameter", str(diameter))
		sheet.set("Centering_Title", "'"+title)
		sheet.recompute()
		doc.recompute()
		export_root(name="FMT Centering jig "+name, label='Centering')

#export_TestMotiseAndTenon()
export_MotiseAndTenon()
export_DowelCentres()
export_YAxisGuides()
#export_Centres()
exit
