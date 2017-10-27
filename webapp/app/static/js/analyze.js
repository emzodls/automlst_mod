function hashCode(input) {
	var hash = 0;
	var j;
	if (input.length == 0) return hash;
	for (j = 0; j < input.length; j++) {
		c = input.charCodeAt(j);
		hash = ((hash<<5)-hash)+c;
		hash = hash & hash; // Convert to 32bit integer
	}
	return hash;
}
// clear up variables!
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
    $("#upfiles").prepend("<option value='"+data["filename"]+"' class='"+hashCode(data["filename"])+"'>"+data["name"]+"</option>");
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
function addtolist(id1,id2) {
    var selectedValues=$(id1).val();
    var i;
    for (i = 0; i < selectedValues.length;i++) {
        //console.log(selectedValues[i]);
        var x = selectedValues[i];
        selectedValues[i] = "<option class='"+hashCode(x)+"'>"+x+"</option>";
        //console.log(i);
        removeFromList(x);
    }
    $(id2).prepend(selectedValues);
    //console.log(selectedValues);
}
function removeFromList(selectedValue) {
    var y = "."+hashCode(selectedValue);
    $("option").remove(y);
    //console.log(selectedValue,hashCode(selectedValue));
}

function removeAllFromList(id3) {
    var selectedValues2=$(id3).val();
    var k;
    for (k = 0; k < selectedValues2.length;k++) {
    removeFromList(selectedValues2[k]);
    }
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

function refreshView(id4,max) {
var counter = 0;
$(id4+" > option").each(function() {
     counter++;
    if (counter > max) {
        $(this).addClass("bg-danger text-danger");
        console.log(this);
     } else {
        $(this).addClass("picked");
     }
});
}
function loadDefaults(id5,id6,max2) {
var counter = 0;
$(id5+" > option").each(function() {
    counter++;
    if (counter <= max2) {
        this.selected=true;
        //console.log($(this));
    }
});
addtolist(id5,id6);
}
var dataObject = null;
Smits.PhyloCanvas.Render.Parameters.Rectangular["paddingY"] = 40;
function renderTree(dataObject,width,height) {
$('#svgCanvas').empty();
phylocanvas = new Smits.PhyloCanvas(
				dataObject,
				'svgCanvas',
				width, height
				);
				var canvasHeight = parseInt($('svg').attr("height"));
				$('svg').attr("height", canvasHeight + Math.round((2*(canvasHeight/100))));
				$('tspan').each(function() {
				if ($(this).html().substring(0,3) == "___") {
				$(this).attr("fill","#0000ff");
				}
				});
}
function resizeTree(vertDir) {
var canvasHeight = parseInt($('svg').attr("height"));
if (vertDir == "up") {
    renderTree(dataObject,1000,canvasHeight + 100);
    } else if (vertDir == "down") {
    renderTree(dataObject,1000,canvasHeight - 100);
    }
}

function treeSuccess(data,textStatus,xhr) {
if (data != "false") {
dataObject = {
				newick: data,
				fileSource: true
			};
			renderTree(dataObject,1000,1000);
			clearInterval(timer);
}
}

function treeError(xhr,ajaxOptions,thrownError) { // communication error
console.log(xhr,ajaxOptions,thrownError);
}
function drawTree() {
var jobid = $('#jobinfo').val();
console.log(jobid);
$.ajax({
        // Your server script to process the upload
        url: '/results/'+jobid+'/tree',
        async: true,
        cache: false,
        contentType: false,
        processData: false,
        success: treeSuccess,
        error: treeError});

}
var timer = setInterval(drawTree, 3000);