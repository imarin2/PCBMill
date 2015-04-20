<?php
require_once $_SERVER['DOCUMENT_ROOT'] . '/fabui/ajax/config.php';
require_once $_SERVER['DOCUMENT_ROOT'] . '/fabui/ajax/lib/utilities.php';


/** CREATE LOG FILES */
$_time                      = $_POST['time'];
/* $_time                      ='1417816594542'; */
$PYTHON_PATH = "/var/www/fabui/application/plugins/pcbmill/assets/python/";
$TEMP_PATH = "/var/www/temp/";
$_destination_trace         = $TEMP_PATH . 'joystickjog_' .$_time . '.trace';
$_destination_console         = $TEMP_PATH . 'joystickjog_console';


// shell_exec('sudo chmod 777 '.$TEMP_PATH);
write_file($_destination_trace, '', 'w');
chmod($_destination_trace, 0777);

write_file($_destination_console , '', 'w');
chmod($_destination_trace, 0777);


/** WAIT JUST 1 SECOND */
sleep(0.1);



/** EXEC COMMAND */

$_command = 'sudo python '.$PYTHON_PATH.'joyjog.py ' . $_destination_trace . ' ' . $_destination_console ;



$_output_command = shell_exec($_command); 
/** WAIT JUST 1 SECOND */
sleep(0.1);


$_response = 'Done!';

echo $_response; 
?>

