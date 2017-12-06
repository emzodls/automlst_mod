function progressSuccess(data,textStatus,xhr) {
//var data = JSON.parse(data);
var jobid = $('#jobinfo').val();
var lastStep = $('#laststep').val();
//console.log(lastStep);
if (data["redirect"]) {
//console.log('TESTING');
    if (data["redirect"] == "step2" && lastStep != "step2") {
        window.location.replace("/results/"+jobid+"/step2");
    } else if (data["redirect"] == "step3" && lastStep != "step3") {
        window.location.replace("/results/"+jobid+"/step3");
    } else if (data["redirect"] == "report") {
        window.location.replace("/results/"+jobid+"/report");
    } else if ((data["redirect"] == "step2" && lastStep == "step2") || (data["redirect"] == "step3" && lastStep == "step3")) {
        $('#workflow2stat').attr("style", "width:"+data["progress"]+"%");
        $('#workflow2stat').attr("aria-valuenow",data["progress"]);
        $('#currentstatus').text(data["status"]);
    }
} else {
//console.log('WORKING');
$('#workflow2stat').attr("style", "width:"+data["progress"]+"%");
//console.log($('#workflow2stat').attr("style"));
$('#workflow2stat').attr("aria-valuenow",data["progress"]);
$('#currentstatus').text(data["status"]);
if (data["mash"] == "finished") {
    getRefGenus();
}
if (data["progress"] == 100) {
    $('#viewreport').removeClass("hidden");
    clearInterval(timer2);
}
}
}

function progressError(xhr,ajaxOptions,thrownError) {
console.log(xhr,ajaxOptions,thrownError);
}

function getStatus() {
var jobid = $('#jobinfo').val();
/*var workflow = $('#workinfo').val();
var statusForm = {

    async: true,
        cache: false,
        contentType: false,
        processData: false,
        success: progressSuccess,
        error: progressError};
if (workflow == 2) {
statusForm.url = '/jobstatus/'+jobid;
} else if (workflow == 1) {
var check1 = $('#skip2').is(":checked");
var check2 = $('#skip3').is(":checked");
statusForm.url = '/jobstatus/'+jobid+'?c1='+check1+'&c2='+check2;
}
console.log(statusForm);
$.ajax(statusForm);*/
$.ajax({

    async: true,
        cache: false,
        contentType: false,
        processData: false,
        url: '/jobstatus/'+jobid,
        success: progressSuccess,
        error: progressError});
}
$('body').onload = getStatus();
var timer2 = setInterval(getStatus, 10000);