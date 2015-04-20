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
$_xcoord		    = $_POST['xcoord'];
$_ycoord		    = $_POST['ycoord'];

/* $_time                      ='1417816594542'; */
$PYTHON_PATH = "/var/www/fabui/application/plugins/pcbmill/python/";
$TEMP_PATH = $PYTHON_PATH."temp/";

write_file($_destination_trace, '', 'w');
chmod($_destination_trace, 0777);

write_file($_destination_response, '', 'w'); 
chmod($_destination_response, 0777);

/** WAIT JUST 1 SECOND */
//sleep(1);

/** EXEC COMMAND */
$_command = 'sudo python '.$PYTHON_PATH.'JogToXY.py ' . $_destination_response . ' ' . $_destination_trace . ' ' .$_xcoord.' '. $_ycoord .' ';

$_output_command = shell_exec($_command); 
/** WAIT JUST 1 SECOND */
sleep(1);


$_response = file($_destination_response);
$_response_items['command']            = $_command;
$_response_items['response']           = $_response[0];
$_response_items['status']             = $_response_items['response']  == true ? 200 : 500;

//file_put_contents('php://stderr', print_r($_response_items, TRUE));


//<span class="hidden-xs">[26/03/2015 15:35:04] -</span> Current coordinates : (115.0,91.0,35.52)
//<span class="hidden-xs">[26/03/2015 15:35:11] -</span> Touching coordinates : (115.0,91.0,11.48)


/** WAIT JUST 1 SECOND */
sleep(1);
header('Content-Type: application/json');
echo minify(json_encode($_response_items));




?>


