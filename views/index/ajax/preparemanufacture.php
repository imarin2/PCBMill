<div id="row_1" class="row interstitial">
	<div class="col-sm-6">
		<h2 class="text-primary">Change tool and start manufacturing</h2>
                <h5 class="text-left">The file that will be manufactured in this step is:</h5>
                <h5 class="text-left"><b><div id="manufacture_filename"></div></b></h5>
                <h5 class="text-left">Please mount the right tool for the job before proceeding.</h5>
                <h5 class="text-left">You may introduce a tool offset correction here:</h5>
 
               <fieldset style="background: none;">
	               <div class="row">
        	               <section class="col col-4">
                	               <label for="ZOffset" class="inline-label">Z Offset (mm): </label>
                                       <input name="ZOffset" class="text-center" type="text" id="ZOffset" value="0">
                               </section>
        		</div>
               </fieldset>

        </div>
</div>
<div id="row_2" class="row interstitial" style="display: none;">
    <div class="col-sm-12">
        <div class="well text-center">
            <h1>Zeroing and leveling gcode</h1>
            <h2 id="res-icon" class="fa fa-spinner"></h2>
            <p class="check_result"></p>
        </div>
    </div>

</div>
<div id="row_3" class="row interstitial" style="display: none;">
        <div class="col-sm-6">
        </div>
</div>

<div class="row button-print-container margin-bottom-10">
        <div class="col-sm-12 text-center ">
            <a id="exec_man_button" href="javascript:void(0);" class="btn btn-primary btn-lg">Click here if you are ready</a>
        </div>
</div>

<script type="text/javascript">

var leveled_file_path="";

    //$('#manufacture_filename').html(files_selected[file_selected_index]);

    $('#exec_man_button').on('click', function(){

        var actual_row;
        var next_row;
        var action = $(this).attr('data-action');

        //$('#xysizes').html("("+files_max_x+","+files_max_y+")");

        $( ".interstitial" ).each(function( index ) {
            if($(this).is(":visible") ){
                actual_row = parseInt($(this).attr('id').replace('row_', ''));
            }
        });

	if(actual_row == 3 || action =='doprint'){
	    $("#exec_man_button").attr('data-action', '');
            print_object();
            return false; 
        }

        if( actual_row == 1 || action =='zeroandlevel'){
                tool_zero_and_level_gcode();
                return false; 
        }


    });

   function tool_zero_and_level_gcode(){
        openWait('Zeroing and Leveling');
        $('#exec_man_button').addClass('disabled');
        $("#res-icon").removeClass('fa-warning fa-check txt-color-green txt-color-red fa-spinner fa-spin');
        $("#res-icon").addClass('fa-spinner fa-spin');
        $('#modal_link').addClass('disabled');

        var timestamp = new Date().getTime();

        ticker_url = '/temp/check_' + timestamp + '.trace';

        $.ajax({
                          url: '/fabui/application/plugins/pcbmill/ajax/zeroandlevel.php',
                          dataType : 'json',
                  type: "POST",
                          async: true,
                  data : { 
			    file : files_selected[currently_manufacturing].full_path, 
			    time: timestamp,
	                    measuredPoints: JSON.stringify(measuredpoints),
			    dozero: is_zeroed?0:1, // if not yet zeroed to localsystem, do it now
			    zoffset: $("#ZOffset").val()
			  },
                          beforeSend: function( xhr ) {
                          },
                dataType: "html"

                }).done(function(response) {


		var status = JSON.parse(response)['status'];
                //var status = response.status;

                if(status == 200){

                    leveled_file_path = JSON.parse(response)['leveled_file_path'];

                    $("#row_2").slideUp('slow', function(){
                    	$("#row_3").slideDown('slow');
                    });

                    $("#res-icon").removeClass('fa-spin').removeClass('fa-spinner').addClass('fa-check').addClass('txt-color-green');
                    $("#exec_man_button").html('Manufacture');
                    $('.check_result').html('');
                    $("#exec_man_button").attr('data-action', 'doprint');
		    $("#exec_man_button").click();
                }else{
                    $("#res-icon").removeClass('fa-spin').removeClass('fa-spinner').addClass('fa-warning').addClass('txt-color-red');
                    $('.check_result').html(response.trace);
                    $("#exec_man_button").html('Oops.. try again');
                    $("#exec_man_button").attr('data-action', 'zeroandlevel');
                }

                ticker_url = '';
                closeWait();
                $('#exec_man_button').removeClass('disabled');
                //$('#exec_button').addClass('disabled');
                //force execution of the step controlling loop
                //$('#exec_button').click();
                // initilize the probing window
                //$('#exec_man_button').hide();
                //$('#xysizes').html(files_max_x+" x "+files_max_y);
                //$('#zeropoint').html("("+x_zero+", "+y_zero+", "+z_zero+")");
                //$('#zerotouch').html("("+x_zero+", "+y_zero+", "+zt_zero+")");
                //initialize_probing();
        });

    }

</script>

