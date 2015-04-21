<?php
//require_once $_SERVER['DOCUMENT_ROOT'] . '/fabui/ajax/config.php';
//require_once $_SERVER['DOCUMENT_ROOT'] . '/fabui/ajax/lib/utilities.php';


/** CREATE LOG FILES */
//$_time                      = $_POST['time'];

$PYTHON_PATH = "/var/www/fabui/application/plugins/pcbmill/python/";
$TEMP_PATH = $PYTHON_PATH."temp/";


$_coordcommand = "ls -t -1 /var/www/fabui/application/plugins/pcbmill/python/temp/*.json | head -1";
/* */
$_output_command = shell_exec($_coordcommand);

$_lastpointjson = explode("\n", $_output_command);

if ( "" != $_lastpointjson) {

 
       //$_lastcalibrationinfo = json_decode($_lastpointjson, TRUE);

	$contents=file_get_contents($_lastpointjson[0]);

	file_put_contents('php://stderr', print_r($contents, TRUE));

	print $contents;
}

?>

