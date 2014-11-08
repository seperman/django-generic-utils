/*jshint multistr: true */
/*
Written by Erasmose 2014
www.ZepWorks.com
MIT Licence
*/


(function(){
    var cookies;

    function readCookie(name,c,C,i){
        if(cookies){ return cookies[name]; }

        c = document.cookie.split('; ');
        cookies = {};

        for(i=c.length-1; i>=0; i--){
           C = c[i].split('=');
           cookies[C[0]] = C[1];
        }

        return cookies[name];
    }

    window.readCookie = readCookie; // or expose it however you want
})();



var csrftoken = readCookie('csrftoken');


var csrfSafeMethod = function(method) {
  // these HTTP methods do not require CSRF protection
  return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
};

// adds these default headers to all ajax calls
$.ajaxSetup({
    crossDomain: false, // obviates need for sameOrigin test
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type)) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});


//-------------------------------------------------------------------------------
// Celery Progress Bar
//-------------------------------------------------------------------------------


function progress_class(options){

  var task_url = options.task_url || null;
  var task_name = options.task_name || "task";
  var original_task_name = options.original_task_name || "task";
  var sec = options.sec*1000 || 5000;
  var waiting = false;
  var waiting_for_cycles = options.waiting_for_cycles || 4;
  var waiting_for_cycles_major = options.waiting_for_cycles || 5;  // waiting_for_cycles*waiting_for_cycles_major*sec = TIMEOUT time 
  var waiting_cycle = 0;
  var waiting_cycle_major = 0;
  var err_count = 0;
  var the_id = options.the_id || null;
  var the_container;
  var progressbar;
  var progressLabel;
  var progressbar_updator;
  var terminate = 0;
  var jquery_dialog = options.jquery_dialog || false;
  var previous_err = "";
  var previous_sticky_msg = "";
  var msg_index_client = 0;
  var previous_msg_index_client = 0;



  var run_task = function() {
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
    });
  };


  var show_progressbar_again = function() {
    the_container = "#container-" + the_id;
    make_progress_bar();
  };


  var terminate_progressbar = function() {
    clearInterval(progressbar_updator);
    setTimeout( function(){progressbar.parent().parent().remove();} , 100 );
  };


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
      data: {id: the_id, terminate: terminate, msg_index_client: msg_index_client}
      } )
      .done(function(celery_respone) {  //?? I changed (celery_respone, s) to (celery_respone)

        if (celery_respone !== null) {
          if (celery_respone.msg !== null && celery_respone.msg !=="") {
            task_name = celery_respone.msg.slice(0,32);
            msg_index_client = celery_respone.msg_index
          }
          progress(celery_respone.progress_percent);

          // checking to see if the msg starts with error:
          if (celery_respone.msg_chunk !== "" && msg_index_client !== previous_msg_index_client){
            previous_msg_index_client = msg_index_client;
            if ($("#tasks_err_log").length == 0){
              $("#footerprogressbar-grp").prepend('<div id="tasks_err_log">');
            }
            $("#tasks_err_log").append(celery_respone.msg_chunk);
          }
          if (celery_respone.sticky_msg && celery_respone.sticky_msg !== previous_sticky_msg ){
            previous_sticky_msg = celery_respone.sticky_msg;
            if ($("#tasks_sticky_msg").length == 0){
              $("#footerprogressbar-grp").prepend('<div id="tasks_sticky_msg">');
            }
            $("#tasks_sticky_msg").html(celery_respone.sticky_msg);
          }
          if (celery_respone.is_killed === true || celery_respone.progress_percent == 100 ){
            terminate_progressbar();
          }
          waiting = false;
        }
      })
      .fail(function(err) {
        console.log(the_id + "ERROR!!! count" +err_count);
        err_count=++err_count;

        if (err_count > 1){
          alert("Error in retrieving task status for: " + task_name);
          waiting = false;
          terminate_progressbar();
        }
        else if (err_count === 1){
          waiting = true;
        }
        else {
          waiting = false;
        }
      });
      
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
        terminate_progressbar();
        alert(task_name + ":TIMEOUT! Please refresh the page later.");
      }
    }
  };



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
          $("#footerprogressbar-grp").prepend('<div id="task_finished">');
          $('#task_finished')
            .append('<input type="button" value="' + original_task_name + ' finished.">')
            .button()
            .click(function(){ window.location.reload(1);});
        }
      });

    });

    progressbar_updator = setInterval(function() { get_task_status(); }, sec);
  };

  var dialog_delete_task = function(){
    $(function() {
      var task_delete_dialog = $( "#task-delete-dialog-confirm" );
      task_delete_dialog.show();
      task_delete_dialog.dialog({
        dialogClass: 'no-close delete-task-dialog',
        resizable: false,
        height: 180,
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
  };
  var dialog_delete_task_simple = function()
    {
      var r=confirm("Are you sure to terminate the task?");
      if (r===true)
        {
          terminate = 1;
        }
    };

  if (task_url !== null){
    run_task();
  } else if (the_id !== null) {
    show_progressbar_again();
  }
}