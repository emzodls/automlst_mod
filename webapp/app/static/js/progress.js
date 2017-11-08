function progressSuccess(data,textStatus,xhr) {
var data = JSON.parse(data);
$('#workflow2stat').attr("style", "width:"+data["status"]+"%");
$('#workflow2stat').attr("aria-valuenow",data["status"]);
clearInterval(timer2); //in final version, only if data["status"] == 100
}

function progressError(xhr,ajaxOptions,thrownError) {
console.log(xhr,ajaxOptions,thrownError);
}

function getStatus() {
var jobid = $('#jobinfo').val();
$.ajax({
    url: '/jobstatus/'+jobid,
    async: true,
        cache: false,
        contentType: false,
        processData: false,
        success: progressSuccess,
        error: progressError});
}

var timer2 = setInterval(getStatus, 5000);