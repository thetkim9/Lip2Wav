var controller;
document.body.onload = function() {
    document.getElementById("load").style.visibility = "hidden";
}
window.onbeforeunload = function() {
    if (timer!=null) {
        clearInterval(timer);
    }
    if (controller!=null) {
        //alert("abort");
        controller.abort();
    }
    if (user_id!=null) {
        //alert("abort");
        $.get('remove/' + user_id);
        console.log("abort");
    }
    return "Do you really want to leave this page?";
}
var timer;
var timer2;
function check_progress(task_id, progress_bar) {
    document.getElementById("load").style.visibility = "visible";
    var progress_bar = document.getElementById("progress_bar");
    var pending = document.getElementById("pending");
    var dots = document.getElementById("dots");
    var time_spent = document.getElementById("time");
    var temp = [".", "..", "..."];
    var time = 0;
    function worker() {
      $.get('progress/' + task_id, function(progress) {
          progress_bar.value = Math.min(parseInt(progress), 100).toString();
          time += 1;
          time_spent.innerHTML = time;
          dots.innerHTML = temp[time%3];
          if (parseInt(progress)>=100) {
            dots.innerHTML = " complete";
            clearInterval(timer);
          }
      })
    }
    timer = setInterval(worker, 1000);
    function worker2() {
      $.get('pending/' + task_id, function(order) {
          pending.innerHTML = order;
          if (parseInt(progress_bar.value)==100) {
            clearInterval(timer2);
          }
      })
    }
    timer2 = setInterval(worker2, 3000);
}

document.getElementById("submit").onclick = () => {
    document.getElementById("result").src = "";
    var formData = new FormData();
    var source = document.getElementById('source').files[0];
    var submit = document.getElementById('submit');
    submit.style.visibility = "hidden";
    //const { v4: uuidv4 } = require('uuid');
    //var user_id = uuidv4();
    user_id = Math.floor(Math.random()*1000000000);
    var progress_bar = document.getElementById('progress_bar');
    formData.append('lip_video', source);
    formData.append('user_id', user_id);
    $.get('setup/' + user_id);
    check_progress(user_id, progress_bar);
    controller = new AbortController();
    var abort = controller.signal;
    fetch(
        '/lip2wav',
        {
            method: 'POST',
            body: formData,
            signal: abort
        }
    )
    .then(response => {
        if ( response.status == 200){
            return response;
        }
        else{
            throw Error("rendering error:");
        }
    })
    .then(response => {return response.blob();})
    .then(blob => URL.createObjectURL(blob))
    .then(audioURL => {
        document.getElementById("result").src = audioURL;
        //document.body.innerHTML += imageURL;
        document.getElementById("errorbox").innerHTML = "";
        //$.get('remove/' + user_id);
        submit.style.visibility = "visible";
    })
    .catch(e =>{
        document.getElementById("errorbox").innerHTML = e;
        $.get('remove/' + user_id);
    })
}
