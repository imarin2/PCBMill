import subprocess
from SimpleCV import Image
import time

subprocess.call("sudo raspistill -hf -vf --exposure off -awb sun -ISO 400 -w 1920 -h 1080 -o /var/www/temp/photo.jpg -t 0", shell=True)

img = Image("/var/www/temp/photo.jpg")

img.show()
time.sleep(5)
