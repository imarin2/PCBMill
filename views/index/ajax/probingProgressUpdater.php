<?php
require_once $_SERVER['DOCUMENT_ROOT'] . '/fabui/ajax/config.php';
require_once $_SERVER['DOCUMENT_ROOT'] . '/fabui/ajax/lib/utilities.php';

/** CREATE LOG FILES */
$_time                      = $_POST['time'];
$PYTHON_PATH = "/var/www/fabui/application/plugins/advancedBedCalibration/assets/python/";
$TEMP_PATH = $PYTHON_PATH."temp/";
$_destination_response      = $TEMP_PATH . 'advancedBedCalibration_' . $_time . '.json';
$_destination_points_file   = $TEMP_PATH . 'advancedBedCalibration_' . $_time . '.pts';

$_response = file_get_contents($_destination_response);
$_response = trim(preg_replace('/\s+/', ' ', $_response));

echo $_response;
?>

