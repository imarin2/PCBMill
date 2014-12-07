<?php
/*
 Plugin Name: PCBMill
 Plugin URI: https://github.com/imarin2/PCBMill
 Version: 0.1
 Description: Plugin to mill insulation milling files, as the ones created with FlatCAM
 Author: Imarin (if you contribute code, put your name here)
 Author URI: http://forum.fabtotum.cc/showthread.php?1589-PCBMill-A-new-FABtotum-pluging-to-mill-PCBs&p=5319#post5319
 Plugin Slug: pcbmill
 Icon: fa fa-bullseye
 */
class PCBMill extends Plugin {

	public function __construct() {
		parent::__construct();

	}

	public function index() {

		$this -> layout -> view('index', '');

	}

	public function remove(){

		/** TO DO  */

		/** remove files */
		shell_exec('sudo rm -rf '.PLUGINSPATH.strtolower(get_class($this)));

		/** SET MESSAGE TO DISPLAY */
		$this->session->set_flashdata('message', "Plugin <strong>".get_class($this)."</strong> removed");
		$this->session->set_flashdata('message_type', 'info');

		/** REDIRECT TO PLUGINS PAGE */
		redirect('plugin');

	}
}
?>
