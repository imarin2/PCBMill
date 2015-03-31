import sys
sys.path = ["./lib"] + sys.path

import CNC
import json


gcode = CNC.GCode();

gcode.load("Tracks_thick.gcode")
points_file='probe.pts';
output_file='leveled_gcode.gcode';

#self.gcode.probe.load(filename);
#gcode.probe.save("model.txt");

pointsFile = open(points_file, "r") 
bedPoints=pointsFile.read()
bed_measurement_points = json.loads(bedPoints) #np.array(json.loads(bedPoints))
probed_points=bed_measurement_points[:-1] #all but last, because the dimensions are in the last

#calculate xmin, xmax, xn, ymin, ymax, yn, zmin, zmax
xn=bed_measurement_points[-1][0]+1;
yn=bed_measurement_points[-1][1]+1;
xmin=0
ymin=0
zmin=0
xmax=0
ymax=0
zmax=0
feed=200

xzero=bed_measurement_points[0][0];
yzero=bed_measurement_points[0][1];
zzero=bed_measurement_points[0][2];



for (p,point) in enumerate(probed_points):
	xt = point[0]-xzero;
	yt = point[1]-yzero;
	zt = point[2]-zzero;

	if xt < xmin:
		xmin = xt;
	if yt < ymin:
		ymin = yt;
	if zt < zmin:
		zmin = zt;
	if xt > xmax:
		xmax = xt;
	if yt > ymax:
		ymax = yt;
	if zt > zmax:
		zmax = zt;

gcode.probe.xmin=xmin;
gcode.probe.ymin=ymin;
gcode.probe.zmin=zmin;
gcode.probe.xmax=xmax;
gcode.probe.ymax=ymax;
gcode.probe.zmax=zmax;
gcode.probe.xn=xn;
gcode.probe.yn=yn;
gcode.probe.feed=feed;

gcode.probe.makeMatrix();
gcode.probe.xstep();
gcode.probe.ystep();


# now the header is known; insert values
for (p,point) in enumerate(probed_points):
	gcode.probe.add(point[0]-xzero,point[1]-yzero,point[2]-zzero);

#gcode.probe.setZero(0,0)

gcode.probe.save("bCNC_probe.txt")
# Here the probe should be initialized

gcode.save("gcode_as_Read.gcode")


lines,paths = gcode.prepare2Run(); # this autolevels the code

out_file = open(output_file,"w")

for line in lines:
	if line is not None:
		out_file.write(str(line) + "\n")
        	#self.queue.put(line+"\n")

out_file.close()

