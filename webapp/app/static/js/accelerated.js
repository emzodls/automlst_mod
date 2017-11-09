var genusKeys = false;
function genusSuccess(data,textStatus,xhr) {
    var genusList = data["genuslist"];
    if (String(genusKeys) != String(Object.keys(genusList))) {
    genusKeys = Object.keys(genusList);
    //need to clear the counter?
    console.log(genusKeys.length);
    var genusVals = Object.values(genusList);
    var maxValue = Math.max.apply(null,genusVals);
    var queries = data["queryfiles"];
    var counter;
    var counter2;
    console.log(maxValue);
    if (genusKeys.length > 1) {
        $('#genuswarn').removeClass("hidden");
        $('#genustable >tbody').empty();
        for (counter=0;counter<genusKeys.length;counter++) {
            $('#genusoptions').append("<option id='"+genusKeys[counter]+"' value='"+genusKeys[counter]+"'>"+genusKeys[counter]+": "+genusList[genusKeys[counter]]+" sequences </option>");
            if (genusList[genusKeys[counter]] == maxValue){
                $('#'+genusKeys[counter]).attr("selected","selected");
            }
        }
        for (counter2=0; counter2<queries.length;counter2++) {
            var currentSeq = queries[counter2];
            $('#genustable >tbody').append("<tr><td>"+currentSeq.file+"</td><td>"+currentSeq.genus+"</td></tr>");
        }
    } else if (genusKeys.length == 1) {
        $('#selectedgenus').text(genusKeys[0]);
        $('#genuswarn').addClass("hidden");
        clearInterval(timer3);
    } else {
        $('#genuswarning').removeClass("hidden");
    }
}
}

function genusError(xhr,ajaxOptions,thrownError) { // communication error
console.log(xhr,ajaxOptions,thrownError);
}

function getRefGenus() {
var jobid = $('#jobinfo').val();
$.ajax({
        // Your server script to process the upload
        contentType: 'application/json',
        url: '/results2/'+jobid+'/refs',
        async: true,
        cache: false,
        contentType: false,
        processData: false,
        success: genusSuccess,
        error: genusError});
}
function selectError(xhr,ajaxOptions,thrownError) { // communication error
console.log(xhr,ajaxOptions,thrownError);
}
function selectSuccess(data,textStatus,xhr){
console.log(data);
}

function selectGenus() {
$.ajax({
        // Your server script to process the upload
        contentType: 'application/json',
        url: '/results2/selectgenus',
        async: true,
        type: 'POST',
        //Form data
        data: new FormData($("#multigenus")[0]),
        cache: false,
        contentType: false,
        processData: false,
        success: selectSuccess,
        error: selectError});
}

var timer3 = setInterval(getRefGenus, 1000);