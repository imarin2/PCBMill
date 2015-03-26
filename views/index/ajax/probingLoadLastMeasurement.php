<?php
//require_once $_SERVER['DOCUMENT_ROOT'] . '/fabui/ajax/config.php';
//require_once $_SERVER['DOCUMENT_ROOT'] . '/fabui/ajax/lib/utilities.php';


/** CREATE LOG FILES */
//$_time                      = $_POST['time'];

$PYTHON_PATH = "/var/www/fabui/application/plugins/advancedBedCalibration/assets/python/";
$TEMP_PATH = $PYTHON_PATH."temp/";

$_command = "ls -al ../../python/temp |  cut -d'_' -f2 | cut -d'.' -f1";
$_output_command = shell_exec($_command); 
$result = explode("\n", $_output_command);


$contents=file_get_contents($TEMP_PATH."advancedBedCalibration_".$result[count($result)-2].".json");
print $contents;
?>

