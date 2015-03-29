<?php
require_once $_SERVER['DOCUMENT_ROOT'] . '/fabui/ajax/config.php';
require_once $_SERVER['DOCUMENT_ROOT'] . '/fabui/ajax/lib/utilities.php';

function debug_to_console( $data ) {

    if ( is_array( $data ) )
        $output = "<script>console.log( 'Debug Objects: " . implode( ',', $data) . "' );</script>";
    else
        $output = "<script>console.log( 'Debug Objects: " . $data . "' );</script>";

    echo $output;
}

/** CREATE LOG FILES */
$_time                      = $_POST['time'];
/* $_time                      ='1417816594542'; */
$PYTHON_PATH = "/var/www/fabui/application/plugins/pcbmill/python/";
$TEMP_PATH = $PYTHON_PATH."temp/";
$_destination_trace         = $TEMP_PATH . 'pcbmill_' . $_time . '.trace';
$_destination_response      = $TEMP_PATH . 'pcbmill_' . $_time . '.json';
$_destination_points_file   = $TEMP_PATH . 'pcbmill_' . $_time . '.pts';
$_accuracy                  = $_POST['accuracy'];
$_calibration_method        = strtoupper($_POST['calibration_method']);
$_pointsToMeasure           = $_POST['pointsToMeasure'];  /* json_decode not done as this is done in python */


function eliminateEmptyArrayValues($myArray) {

	foreach ($myArray as $key => $value) {
    		if (empty($value)) {
			unset($myArray[$key]);
		}
	}

	$myArray = array_values($myArray);
	return $myArray;
}

//file_put_contents('php://stderr', print_r($_calibration_method, TRUE));

write_file($_destination_trace, '', 'w');
chmod($_destination_trace, 0777);

write_file($_destination_response, '', 'w'); 
chmod($_destination_response, 0777);

/** WAIT JUST 1 SECOND */
sleep(1);

/** Write Points file for bed calibration **/
$myfile = fopen($_destination_points_file, "w") or die("Unable to open file!".$_destination_points_file);
fwrite($myfile, $_pointsToMeasure);
fclose($myfile);


/** EXEC COMMAND */
$h_over = 50;

$_command = 'sudo python '.$PYTHON_PATH.'ExternalEndstopProbe.py ' . $_destination_response . ' ' . $_destination_trace . ' ' .$_destination_points_file.' '. $h_over . ' '.$_calibration_method.' '.$_accuracy.' ';

$_output_command = shell_exec($_command); 
/** WAIT JUST 1 SECOND */
sleep(2);

/* $_response = json_decode(file_get_contents($_destination_response), TRUE); */

$_response = file_get_contents($_destination_response);
$_response = trim(preg_replace('/\s+/', ' ', $_response));

echo $_response; 
?>

