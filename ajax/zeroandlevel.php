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

$_destination_trace    = TEMP_PATH.'macro_trace';
$_destination_response = TEMP_PATH.'macro_response';

/** CREATE LOG FILES */
$_time                      = $_POST['time'];
/* $_time                      ='1417816594542'; */
$PYTHON_PATH = "/var/www/fabui/application/plugins/pcbmill/python/";
$TEMP_PATH = $PYTHON_PATH."temp/";
//$_destination_trace         = $TEMP_PATH . 'pcbmill_' . $_time . '.trace';
//$_destination_response      = $TEMP_PATH . 'pcbmill_' . $_time . '.json';
$_destination_points_file   = $TEMP_PATH . 'pcbmill_' . $_time . '.pts';
//$_accuracy                  = $_POST['accuracy'];
//$_calibration_method        = strtoupper($_POST['calibration_method']);
$_measured_points            = $_POST['measuredPoints'];  /* json_decode not done as this is done in python */
$_selected_file              = $_POST['file'];


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
fwrite($myfile, $_measured_points);
fclose($myfile);


/** EXEC COMMAND */
$h_over = 50;

$_command = 'sudo python '.$PYTHON_PATH.'ZeroToolAndLevelGcode.py ' . $_destination_response . ' ' . $_destination_trace . ' ' .$_destination_points_file.' '. $h_over .' ' .$_selected_file .' ';

$_output_command = shell_exec($_command); 
/** WAIT JUST 1 SECOND */
sleep(2);

/* $_response = json_decode(file_get_contents($_destination_response), TRUE); */

$_response = file($_destination_response);
//$_response = trim(preg_replace('/\s+/', ' ', $_response));
/*$_response = filenameofcorrectedfile*/
//echo $_response;

//file_put_contents('php://stderr', print_r($_response, TRUE));

/** RESPONSE */
//$_response_items['check_trace']        = $_destination_trace;
//$_response_items['check_response']     = $_destination_response;
$_response_items['command']            = $_command;
//$_response_items['pid']                = $_pid;
//$_response_items['url_check_response'] = host_name().'temp/response_'.$_time.'.log';
$_response_items['response']           = $_response[1];
//$_response_items['real_response']      = $_response;

//$_response_items['trace']              = $_trace;
$_response_items['status']             = $_response_items['response']  == true ? 200 : 500;
//$_response_items['status']             = 200;

$_response_items['leveled_file_path']  = str_replace(PHP_EOL, '', $_response[0]);

file_put_contents('php://stderr', print_r($_response_items, TRUE));


//<span class="hidden-xs">[26/03/2015 15:35:04] -</span> Current coordinates : (115.0,91.0,35.52)
//<span class="hidden-xs">[26/03/2015 15:35:11] -</span> Touching coordinates : (115.0,91.0,11.48)


/** WAIT JUST 1 SECOND */
sleep(1);
header('Content-Type: application/json');
echo minify(json_encode($_response_items));




?>


