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

base_path = os.path.dirname(doc.FileName)
base_filename = os.path.splitext(os.path.basename(doc.FileName))[0]

sketch = doc.addObject("Sketcher::SketchObject", "Sketch")
sketch.addGeometry(Part.LineSegment(App.Vector(1.2, 1.8, 0),  App.Vector(5.2, 5.3, 0)), False)
sketch.addGeometry(Part.LineSegment(App.Vector(6.5, 1.5, 0),  App.Vector(10.2, 5.0, 0)), False)
sketch.addGeometry(Part.LineSegment(App.Vector(12.2, 1.0, 0), App.Vector(15.4, 5.0, 0)), False)

doc.recompute()

exit
