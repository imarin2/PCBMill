<?php
require_once $_SERVER['DOCUMENT_ROOT'] . '/fabui/ajax/config.php';
require_once $_SERVER['DOCUMENT_ROOT'] . '/fabui/ajax/lib/utilities.php';


/** CREATE LOG FILES */
$_time                      = $_POST['time'];
$PYTHON_PATH = "/var/www/fabui/application/plugins/advancedBedCalibration/assets/python/";

$_command = "sudo kill -9 `sudo ps -ax | grep python | grep advancedBedCalibration.py | cut -d' ' -f1`";

$_output_command = shell_exec($_command); 

$_command = "sudo kill -9 `sudo ps -ax | grep python | grep advancedBedCalibration.py | cut -d' ' -f2`";

$_output_command = shell_exec($_command); 

$_command = 'sudo python ' . $PYTHON_PATH . 'retractNozzle.py ';

$_output_command = shell_exec($_command); 

/*
$myfile = fopen("/var/www/temp/debug.txt", "w") or die("Unable to open file!");
fwrite($myfile, $_command);
fwrite($myfile, $_output_command);
fclose($myfile);
*/

echo "done" ;
?>

