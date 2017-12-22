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
$("#seqbtn").removeClass("disabled");
$("#ncbibtn").removeClass("disabled");
$("#ncbiload").addClass("hidden");
$('progress').removeClass("hidden");
if (data["filename"] == false) {
    $("#errorwarning").removeClass("hidden");
    } else {
       if ($("#filesrc").val() == 'ncbi') {
        $("#uploadprog").attr("value",100);
        console.log($("#uploadprog").attr("value"));
        }
    $("#upfiles").prepend("<option value='"+data["filename"]+"' class='"+hashCode(data["filename"])+" picked'>"+data["name"]+"</option>");
    maxSeqs();
    $("#uploadsuccess").removeClass("hidden");
    }
    clearProgress();
}
function uploadError(xhr,ajaxOptions,thrownError) { // communication error
console.log(thrownError);
$("#seqbtn").removeClass("disabled");
$("#ncbibtn").removeClass("disabled");
//unhide error message
$("#uploadwarning").removeClass("hidden");
$("#ncbiload").addClass("hidden");
clearProgress();
$("#uploadprog").attr("value",0);
}
function clearErrors(errorMessage) {
$(errorMessage).addClass("hidden");
}
function uploader(filesrc) {
if (maxSeqs()) {
$("#seqbtn").addClass("disabled");
$("#ncbibtn").addClass("disabled");
var uploadForm = {
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
        error: uploadError
        /*xhr: function() {
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
        }*/
};
if (filesrc == 'ncbi') {
    $('#ncbiload').removeClass("hidden");
    $('progress').addClass("hidden");
    $('progress').attr({
    value: 50,
    max: 100
    });
} else {
uploadForm.xhr = function() {
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
}
$.ajax(uploadForm);
}
}

function validateAcc() {
var userAcc = $("#ncbiacc1").val();
var allowedChars = /[A-Z0-9_]+$/i;
console.log(allowedChars.test(userAcc));
if (userAcc && (userAcc.search(" ") == -1) && allowedChars.test(userAcc)) { //check if userAcc is alphanumeric
    console.log('TESTING');
    return true;
    } else {
    return false;
    }
}

function checkDuplicateAcc() {
var userAcc = $('#ncbiacc1').val().trim();
var duplicateFound;
$('#upfiles>option').each(function() {
    var plainName = $(this).text().split(".");
    var fileName = plainName[0];
    if (userAcc && userAcc.toUpperCase() == fileName.toUpperCase()) {
        duplicateFound=true;
    }
});
if (duplicateFound == true) {
    return false;
} else {
    return true;
}
}

function uploadSequence(filesrc) {
clearErrors('#uploadwarning');
clearErrors('#errorwarning');
clearErrors('#uploadsuccess');
clearErrors('#accwarning');
clearErrors('#duplicatewarning');
clearErrors('.selectablewarn');
$("#filesrc").val(filesrc);
console.log($("#ncbiacc1").val());
if (filesrc == 'ncbi' && !(validateAcc())) {
    $("#accwarning").removeClass("hidden");
} else if (filesrc == 'ncbi' && !(checkDuplicateAcc())) {
    $('#duplicatewarning').removeClass("hidden");
}
else {
uploader(filesrc);
console.log($("#uploadprog")); // -> doesn't clear properly!
}
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
    removeFromList('#upfiles', selectedValues3[l]);
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

$(document).ready(function(){
    $('[data-toggle="tooltip"]').tooltip();
});

$(document).on("keydown","input:not(button)", function(e) {
    if (e.keyCode == 13) {
        e.preventDefault();
    }
});