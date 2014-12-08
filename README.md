PCBMill
=======

PCBMill FABtotum plugin

How to Install
==============

Linux
=====

git clone https://github.com/imarin2/PCBMill.git

mv PCBMill pcbmill

zip -r pcbmill.zip pcbmill -x \*.git\*

Now go to the FAB-UI, plugins (plug icon on the top right of the screen), and upload the generated zip file.

NOTE: If you are seeing this file as a normal text file (not from github), not that \* is markdown for *, so actually the zip command is: zip -r pcbmill.zip pcbmill -x .git . This makes only sense if you are seeing this file as text (e.g. cat README.md)

Windows
=======

I have not tried this instructions, because I do not have a windows machine.

1. Download zip file from: https://github.com/imarin2/PCBMill

2. Extract the zip

3. Delete the folder ".git" inside the extracted folder

4. Rename the extracted folder to "pcbmill"

5. zip this folder to generate "pcbmill.zip".

Now go to the FAB-UI, plugins (plug icon on the top right of the screen), and upload the generated zip file.
