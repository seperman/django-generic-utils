/*
Written by Erasmose 2014
www.ZepWorks.com
MIT Licence
*/


function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


var csrftoken = getCookie('csrftoken');


var csrfSafeMethod = function(method) {
  // these HTTP methods do not require CSRF protection
  return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

// adds these default headers to all ajax calls
$.ajaxSetup({
    crossDomain: false, // obviates need for sameOrigin test
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type)) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});



function progress_class(options){

  var task_url = options.task_url;
  var task_name = options.task_name || "task";
  var sec = options.sec*1000 || 5000;
  var waiting = false;
  var waiting_for_cycles = options.waiting_for_cycles || 4;
  var waiting_for_cycles_major = options.waiting_for_cycles || 5;  // waiting_for_cycles*waiting_for_cycles_major*sec = TIMEOUT time 
  var waiting_cycle = 0;
  var waiting_cycle_major = 0;
  var err_count = 0;
  var the_id;
  var the_container;
  var progressbar;
  var progressLabel;
  var progressbar_updator;
  var terminate = 0;
  var jquery_dialog = options.jquery_dialog || "true";



  var run_task = function(task_url) {
    $.ajax( {
    url: task_url,
    type: "POST",
    data: {}
    } )
    .done(function(msg) {
      // checking to see if the msg startswith error
      if (msg.lastIndexOf("Err", 0) === 0 ){
        alert( task_name + " :: " + msg );
      } else {
        the_id = msg;
        the_container = "#container-" + the_id;

        make_progress_bar();
      }
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
      url: "/generics/task_api",
      type: "POST",
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
          if (msg.state !== null && msg.state !=="") {
            task_name = msg.state.slice(0,32);
          }
          progress(msg.progress_percent);

          // checking to see if the state starts with error:
          if (msg.state.lastIndexOf("Err", 0) === 0 ){
            alert(msg.state);
            waiting = true;
            terminate = 1;
          }
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
      
      progressLabel.text( task_name +": Waiting " + waiting_cycle);

      if (waiting_cycle > waiting_for_cycles){
        waiting_cycle_major=++waiting_cycle_major;
        waiting_cycle = 0;
        waiting = false;
      }
      if (waiting_cycle_major > waiting_for_cycles_major){
        alert(task_name + ":TIMEOUT! Please try again later.");
        terminate = 1;
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
          <button type='button' class='cancel-task'>X</button>\
        </div>\
      </div>");


    $(the_container+' .cancel-task').click(function(){
        if (jquery_dialog===true){
          dialog_delete_task();
        } else {
          dialog_delete_task_simple();
        }
      } 
    ).button({ icons: { primary: "ui-icon-circle-close" }, text: false });


    progressbar = $( the_container+" #progressbar" );
    progressLabel = $( the_container+" .progress-label" );
    progressLabel.text( task_name );

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
        dialogClass: 'no-close delete-task-dialog',
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
  var dialog_delete_task_simple = function()
    {
      var r=confirm("Are you sure?");
      if (r===true)
        {
          terminate = 1;
        }
    }

  run_task(task_url);
}