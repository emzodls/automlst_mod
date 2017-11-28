function progressSuccess(data,textStatus,xhr) {
var data = JSON.parse(data);
$('#workflow2stat').attr("style", "width:"+data["progress"]+"%");
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
$('body').onload = getStatus();
var timer2 = setInterval(getStatus, 10000);