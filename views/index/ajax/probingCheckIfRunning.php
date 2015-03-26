<?php
require_once $_SERVER['DOCUMENT_ROOT'] . '/fabui/ajax/config.php';
require_once $_SERVER['DOCUMENT_ROOT'] . '/fabui/ajax/lib/utilities.php';


/** CREATE LOG FILES */
$_time                      = $_POST['time'];

$_command = "sudo ps -ax | grep python | grep advancedBedCalibration.py | cut -d'/' -f20 | cut -d'_' -f2 | cut -d'.' -f1";
$_output_command = shell_exec($_command); 
$result = explode("\n", $_output_command);


echo $result[0]; 
?>

