<div id="row_1" class="row interstitial">
	<div class="col-sm-6">
		<h2 class="text-primary">Change tool and start manufacturing</h2>
                <h5 class="text-left">The file that will be manufactured in this step is:</h5>
                <h5 class="text-left"><div id="manufacture_filename"></div></h5>
                <h5 class="text-left">Please mount the right tool for the job before proceeding.</h5>
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

<div class="row button-print-container margin-bottom-10">
        <div class="col-sm-12 text-center ">
            <a id="exec_button" href="javascript:void(0);" class="btn btn-primary btn-lg">Click here if you are ready</a>
        </div>
</div>

<script type="text/javascript">

    //$('#manufacture_filename').html(files_selected[file_selected_index]);

    $('#exec_button').on('click', function(){

        var actual_row;
        var next_row;
        var action = $(this).attr('data-action');

        //$('#xysizes').html("("+files_max_x+","+files_max_y+")");

        $( ".interstitial" ).each(function( index ) {
            if($(this).is(":visible") ){
                actual_row = parseInt($(this).attr('id').replace('row_', ''));
            }
        });

        if(action == "zeroandcorrect"){
                //pre_print();
                return false; 
        }

    });

   function configure_zero(){
        openWait('Zeroing and Leveling');
        $('#exec_button').addClass('disabled');
        $("#res-icon").removeClass('fa-warning fa-check txt-color-green txt-color-red fa-spinner fa-spin');
        $("#res-icon").addClass('fa-spinner fa-spin');
        $('#modal_link').addClass('disabled');

        var timestamp = new Date().getTime();

        ticker_url = '/temp/check_' + timestamp + '.trace';

        $.ajax({
//                        url: ajax_endpoint + 'ajax/pre_print.php',
                          url: '/fabui/application/plugins/pcbmill/ajax/configure_zero.php',
                          dataType : 'json',
                  type: "POST",
                          async: true,
                  data : { file : file_selected.full_path, time:timestamp},
                          beforeSend: function( xhr ) {
                          }
                }).done(function(response) {

                var status = response.status;

                if(status == 200){

                    var zerocoords = JSON.parse(response.zerocoords);

                    x_zero = zerocoords.x;
                    y_zero = zerocoords.y;
                    z_zero = zerocoords.z;
                    zt_zero = zerocoords.zt;

                        $("#row_3").slideUp('slow', function(){});
                        $("#row_4").slideUp('slow', function(){
                        $("#row_5").slideDown('slow');
                    });

                    $("#res-icon").removeClass('fa-spin').removeClass('fa-spinner').addClass('fa-check').addClass('txt-color-green');
                    $("#exec_button").html('Start');
                    $('.check_result').html('');
                    $("#exec_button").attr('data-action', '');
                }else{
                    $("#res-icon").removeClass('fa-spin').removeClass('fa-spinner').addClass('fa-warning').addClass('txt-color-red');
                    $('.check_result').html(response.trace);
                    $("#exec_button").html('Oops.. try again');
                    $("#exec_button").attr('data-action', 'configzero');
                }

                ticker_url = '';
                closeWait();
                //$('#exec_button').removeClass('disabled');
                //$('#exec_button').addClass('disabled');
                //force execution of the step controlling loop
                //$('#exec_button').click();
                // initilize the probing window
                $('#exec_button').hide();
                $('#xysizes').html(files_max_x+" x "+files_max_y);
                $('#zeropoint').html("("+x_zero+", "+y_zero+", "+z_zero+")");
                $('#zerotouch').html("("+x_zero+", "+y_zero+", "+zt_zero+")");
                initialize_probing();
        });

    }

</script>

