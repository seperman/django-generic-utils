/*
Written by Erasmose 2014
www.ZepWorks.com
MIT Licence
*/



function progess_class(options){

  var task_url = options.task_url;
  var task_name = options.task_name || "task";
  var sec = options.sec*1000 || 5000;
  var waiting = false;
  var waiting_for_cycles = options.waiting_for_cycles || 4;
  var waiting_cycle = 0;
  var err_count = 0;
  var the_id;
  var the_container;
  var progressbar;
  var progressLabel;
  var progressbar_updator;
  var terminate = 0;


  var run_task = function(task_url) {
    $.ajax( {
    url: task_url,
    data: {}
    } )
    .done(function(msg) {
      the_id = msg;
      the_container = "#container-" + the_id;

      make_progress_bar();
    })
    .fail(function(err) {
      alert( "error running the task: " + err );
    })
  }
  

  var get_task_status = function() {
    function progress(msg) {
      progressbar.progressbar( "value", msg );
    }

    if (waiting===false){
      waiting = true;

      $.ajax( {
      url: "generics/task_api",
      cache: false,
      data: {id: the_id, terminate: terminate}
      } )
      .done(function(msg, s) {

        if (terminate==1){
          clearInterval(progressbar_updator);
          setTimeout( function(){progressbar.parent().parent().remove();} , 1000 );
        }

        if (msg !== null) {
          // console.log(the_id + " :: " + msg.progress_percent + " " + s)
          progress(msg.progress_percent);
          waiting = false;
        };
      })
      .fail(function(err) {
        console.log(the_id + "ERROR!!!");
        err_count=++err_count;

        if (err_count > 4){
          alert("Error in retrieving task status for: " + task_name);
          waiting = true;
        } else {
          waiting = false;
        }
      })
      
      //waiting is True
    } else {
      waiting_cycle = ++waiting_cycle;
      if (waiting_cycle > waiting_for_cycles){
        waiting_cycle = 0;
        waiting = false;
      }
    }
  }



  var make_progress_bar = function() {
    $("#progressbar-container").append("<div id='container-"+the_id+"'>\
        <div style='display: inline-block;'>\
          <div id='progressbar'>\
            <div class='progress-label'></div>\
          </div>\
        </div>\
        <div style='display: inline-block;'>\
          <button class='cancel-task'>X</button>\
        </div>\
      </div>");


    $(the_container+' .cancel-task').click(function(){
        dialog_delete_task();
      } 
    ).button({ icons: { primary: "ui-icon-circle-close" }, text: false });
    // $(the_container+' .cancel-task')


    progressbar = $( the_container+" #progressbar" );
    progressLabel = $( the_container+" .progress-label" );

    $(function() {

      progressbar.progressbar({
        value: false,
        change: function() {
          progressLabel.text( task_name +" "+ progressbar.progressbar( "value" ) + "%" );
        },
        complete: function() {
          progressLabel.text( "finished!" );
          clearInterval(progressbar_updator);
          setTimeout( function(){progressbar.parent().parent().remove();} , 5000 );
        }
      });

    });

    progressbar_updator = setInterval(function() { get_task_status(); }, sec);
  }

  var dialog_delete_task = function(){
    $(function() {
      var task_delete_dialog = $( "#task-delete-dialog-confirm" );
      task_delete_dialog.show();
      task_delete_dialog.dialog({
        resizable: false,
        height:180, 
        modal: true,
        buttons: {
          "Delete": function() {
            terminate = 1;
            $( this ).dialog( "close" );
          },
          Cancel: function() {
            $( this ).dialog( "close" );
          }
        }
      });
    });
  }

  run_task(task_url);
}