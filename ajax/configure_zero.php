<?php
require_once $_SERVER['DOCUMENT_ROOT'] . '/lib/config.php';
require_once $_SERVER['DOCUMENT_ROOT'] . '/lib/utilities.php';


/** CREATE LOG FILES */
$_time = $_POST['time'];
$_type = isset($_POST['type']) ? $_POST['type'] : '';



$_destination_trace    = TEMP_PATH.'macro_trace';
$_destination_response = TEMP_PATH.'macro_response';

write_file($_destination_trace, '', 'w');
chmod($_destination_trace, 0777);

write_file($_destination_response, '', 'w');
chmod($_destination_response, 0777);



/** WAIT JUST 1 SECOND */
sleep(1);

/** EXEC COMMAND */
//$_command        = "sudo python /var/www/fabui/application/plugins/pcbmill/python/gmacro_extensions.py external_endstop_coords " + $_destination_trace + " " + $_destination_response +" > /dev/null";
//$_command        = 'sudo python '.PYTHON_PATH.'gmacro.py home_all '.$_destination_trace.' '.$_destination_response.' > /dev/null';
$_command        = 'sudo python /var/www/fabui/application/plugins/pcbmill/python/gmacro_extensions.py external_endstop_coords '.$_destination_trace.' '.$_destination_response.' > /dev/null';
$_output_command = shell_exec ( $_command );
$_pid            = trim(str_replace('\n', '', $_output_command));

/** WAIT JUST 1 SECOND */
sleep(5);

$_response = file($_destination_response);
$_trace    = file_get_contents($_destination_trace);
$_trace    = str_replace(PHP_EOL, '<br>', $_trace);

//unlink($_destination_response);
//unlink($_destination_trace);



/** RESPONSE */
//$_response_items['check_trace']        = $_destination_trace;
//$_response_items['check_response']     = $_destination_response;
$_response_items['command']            = $_command;
//$_response_items['pid']                = $_pid;
//$_response_items['url_check_response'] = host_name().'temp/response_'.$_time.'.log';
$_response_items['response']           = str_replace(PHP_EOL, '', $_response[1]) == 'true' ? true : false;
//$_response_items['real_response']      = $_response;

$_response_items['trace']              = $_trace;
$_response_items['status']             = $_response_items['response']  == true ? 200 : 500;
//$_response_items['status']             = 200;

$_response_items['zerocoords']         = str_replace(PHP_EOL, '', $_response[0]);

//file_put_contents('php://stderr', print_r($_response_items, TRUE));


//<span class="hidden-xs">[26/03/2015 15:35:04] -</span> Current coordinates : (115.0,91.0,35.52)
//<span class="hidden-xs">[26/03/2015 15:35:11] -</span> Touching coordinates : (115.0,91.0,11.48)


/** WAIT JUST 1 SECOND */
sleep(1);
header('Content-Type: application/json');
echo minify(json_encode($_response_items));

?>
