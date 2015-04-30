<?php
require_once $_SERVER['DOCUMENT_ROOT'] . '/fabui/ajax/config.php';
require_once $_SERVER['DOCUMENT_ROOT'] . '/fabui/ajax/lib/utilities.php';

$_destination_trace    = TEMP_PATH.'macro_trace';
$_destination_response = TEMP_PATH.'macro_response';

/** CREATE LOG FILES */
$_time                      = $_POST['time'];
$PYTHON_PATH = "/var/www/fabui/application/plugins/pcbmill/python/";
$TEMP_PATH = $PYTHON_PATH."temp/";

write_file($_destination_trace, '', 'w');
chmod($_destination_trace, 0777);

write_file($_destination_response, '', 'w'); 
chmod($_destination_response, 0777);

$_command = 'sudo python /var/www/fabui/application/plugins/pcbmill/python/gmacro_extensions.py energize_motors '.$_destination_trace.' '.$_destination_response.' > /dev/null';

$_output_command = shell_exec($_command); 

sleep(1);

$_response = file_get_contents($_destination_response);

/** RESPONSE */
//$_response_items['check_trace']        = $_destination_trace;
//$_response_items['check_response']     = $_destination_response;
$_response_items['command']            = $_command;
//$_response_items['pid']                = $_pid;
//$_response_items['url_check_response'] = host_name().'temp/response_'.$_time.'.log';
$_response_items['response']           = str_replace(PHP_EOL, '', $_response) == 'true' ? true : false;
//$_response_items['real_response']      = $_response;

//$_response_items['trace']              = $_trace;
$_response_items['status']             = $_response_items['response']  == true ? 200 : 500;

file_put_contents('php://stderr', print_r($_response_items, TRUE));


/** WAIT JUST 1 SECOND */
sleep(1);
header('Content-Type: application/json');
echo minify(json_encode($_response_items));




?>


