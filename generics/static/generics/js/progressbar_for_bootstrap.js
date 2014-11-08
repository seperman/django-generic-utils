
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
  var progressbar_updator;
  var terminate = 0;
  var jquery_dialog = options.jquery_dialog || false;
  var previous_err = "";
  var previous_sticky_msg = "";
  var msg_index_client = 0;
  var previous_msg_index_client = 0;
  var thedialogRef = null;


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
    thedialogRef.setClosable(true);
  };


  var progressbar_update = function(msg, percent) {
    progressbar.css('width', percent+'%');
    progressbar.text( msg +": "+ percent + "%");      
  }


  var get_task_status = function() {


    if (waiting===false){
      waiting = true;

      $.ajax( {
      url: "/generics/task_api",
      type: "POST",
      cache: false,
      data: {id: the_id, terminate: terminate, msg_index_client: msg_index_client}
      } )
      .done(function(celery_respone) {

        if (celery_respone !== null) {
          if (celery_respone.msg !== null && celery_respone.msg !=="") {
            task_name = celery_respone.msg.slice(0,32);
            msg_index_client = celery_respone.msg_index
            progressbar_update(task_name, celery_respone.progress_percent);
          }

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
      
      progressbar.text( task_name +": Waiting " + waiting_cycle);

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

    BootstrapDialog.show({
        title: task_name,
        message: "<div id='footerprogressbar-grp'></div><div id='container-"+the_id+"' class='progress'>\
            <div class='progress-bar progressbar' role='progressbar' aria-valuenow='0' aria-valuemin='0' aria-valuemax='100' style='width: 0%;'>\
              IN PROGRESS\
            </div>\
      </div>",
        closable: false,
        closeByBackdrop: false,
        closeByKeyboard: false,
        size: BootstrapDialog.SIZE_NORMAL,
        buttons: [{
            id: 'btn-cancel',   
            icon: 'glyphicon glyphicon-remove',       
            label: 'Cancel',
            cssClass: 'btn-warning buttons_classy', 
            autospin: false,
            action: function(dialogRef){    
              BootstrapDialog.confirm('Are you sure to terminate the task?', function(result){
                  if(result) {
                      terminate = 1;
                  }
              });
            }
        }],
        onshown: function(dialogRef){

          thedialogRef = dialogRef;

          progressbar = $( the_container+" .progressbar" );
          progressbar.text( task_name );


          progressbar_updator = setInterval(function() { get_task_status(); }, sec);


        }
    });    

  };


  if (task_url !== null){
    run_task();
  } else if (the_id !== null) {
    show_progressbar_again();
  }
}


