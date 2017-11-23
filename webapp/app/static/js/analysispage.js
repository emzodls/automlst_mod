function maxSeqs() {
if ($("#upfiles > option").length >= 3) {
            $("#seqbtn").addClass("disabled");
            $("#ncbibtn").addClass("disabled");
            $("#seqwarn").removeClass("hidden");
            return false;
        } else {
            $("#seqbtn").removeClass("disabled");
            $("#ncbibtn").removeClass("disabled");
            $("#seqwarn").addClass("hidden");
            return true;
        }
}
function clearProgress() {
if ($("#uploadprog").attr("value") == $("#uploadprog").attr("max")) {
    $("#uploadprog").attr("value",0);
}
}

function uploadSuccess(data,textStatus,xhr) { //communication success
var data = JSON.parse(data);
console.log(data["filename"]);
if (data["filename"] == false) {
    $("#errorwarning").removeClass("hidden");
    } else {
    $("#upfiles").prepend("<option value='"+data["filename"]+"' class='"+hashCode(data["filename"])+" picked'>"+data["name"]+"</option>");
    maxSeqs();
    $("#uploadsuccess").removeClass("hidden");
    }
    clearProgress();
}
function uploadError(xhr,ajaxOptions,thrownError) { // communication error
console.log(xhr,ajaxOptions,thrownError);
//unhide error message
$("#uploadwarning").removeClass("hidden");
clearProgress();
}
function clearErrors(errorMessage) {
$(errorMessage).addClass("hidden");
}
function uploader() {
if (maxSeqs()) {
$.ajax({
        // Your server script to process the upload
        contentType: 'application/json',
        url: '/upload',
        async: true,
        type: 'POST',
        //Form data
        data: new FormData($("#sequpload")[0]),
        cache: false,
        contentType: false,
        processData: false,
        success: uploadSuccess,
        error: uploadError,
        xhr: function() {
            var myXhr = $.ajaxSettings.xhr();
            if (myXhr.upload) {
                // For handling the progress of the upload
                myXhr.upload.addEventListener('progress', function(e) {
                    if (e.lengthComputable) {
                        $('progress').attr({
                            value: e.loaded,
                            max: e.total,
                        });
                    }
                } , false);
            }
            return myXhr;
        }
});
}
}
function uploadSequence(filesrc) {
clearErrors('#uploadwarning');
clearErrors('#errorwarning');
clearErrors('#uploadsuccess')
$("#filesrc").val(filesrc);
uploader();
console.log($("#uploadprog")); // -> doesn't clear properly!
}

function genusSuccess(data,textStatus,xhr) {
var counter;
for (counter=0;counter<data.length;counter++) {
    var genusInfo = data[counter];
    $('#genusselect').append("<option id='"+genusInfo.genusid+"' value='"+genusInfo.genusid+"'>"+genusInfo.genusname+"</option>");
}
}

function genusError(xhr,ajaxOptions,thrownError) { // communication error
console.log(xhr,ajaxOptions,thrownError);
}

function refGenus() {
$.ajax({
    contentType: 'application/json',
    url: '/results2/refgenus',
    async: true,
    cache: false,
    contentType: false,
    processData: false,
    success: genusSuccess,
    error: genusError

});
}

function removeAllSeqs() {
    var selectedValues3=$("#upfiles").val();
    var l;
    for (l = 0; l < selectedValues3.length;l++) {
    removeFromList(selectedValues3[l]);
    }
    maxSeqs();
}
function selectToggle() {
if (($('input[name="workflow"]:checked', '#sequpload').val()) == "2") {
    $('#genusform').removeClass("hidden");
    } else {
    $('#genusform').addClass("hidden");
    }
}

function validateForm() {
if ($('.selectablein').has('option').length>0) {
return "validated";
} else {
return "notvalidated";}
}

$(document).on("keydown","input:not(button)", function(e) {
    if (e.keyCode == 13) {
        e.preventDefault();
    }
});