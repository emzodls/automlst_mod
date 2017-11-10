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
function addtolist(id1,id2) {
var optionList = [];
    $(id1+' > option:selected').each(function() {
    var speciesOption = "<option id='"+$(this).attr("id")+"' value='"+$(this).val()+"' class='"+hashCode($(this).val())+" picked' data-title='"+$(this).data("title")+"'>"+$(this).data("title")+"</option>";
    optionList.unshift(speciesOption);
    removeFromList($(this).val()); //removes any item that already has this class from the list it'll get added to
    });
    var i;
    for (i = 0; i < optionList.length; i++) {
    $(id2).prepend(optionList[i]);
    }
/*    var selectedValues=$(id1).val();
    console.log(selectedValues);
    var i;
    for (i = 0; i < selectedValues.length;i++) {
        //console.log(selectedValues[i]);
        var x = selectedValues[i];
        //var orgName = selectedOrg[i];
        selectedValues[i] = "<option class='"+hashCode(x)+"' "+ "value='" + x+ "'>"+x+"</option>";
        //console.log(i);
        removeFromList(x);
    }
    $(id2).prepend(selectedValues);
    //console.log(selectedValues); */
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
        $(this).removeClass("picked");
        console.log(this);
     } else {
        $(this).addClass("picked");
        $(this).removeClass("bg-danger text-danger");
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
function selectAndSend(id7) {
$(".picked").each(function() {
this.selected=true;
});
$(id7).submit();
}
function orgError(xhr,ajaxOptions,thrownError) { // communication error
console.log(xhr,ajaxOptions,thrownError);
}

function orgSuccess(data,textStatus,xhr) {
var counter;
var counter2;
var counter3;
var queryOrgs = data["queryorgs"];
var refOrgs = data["reforgs"];
var outgroups = data["outgroups"];
for (counter3 = 0; counter3<queryOrgs.length; counter3++) {
    var queryInfo = queryOrgs[counter3];
    $('#speciessel').append("<option value='"+queryInfo.id+"' data-title='(U) "+ queryInfo.orgname + " (distance: "+ queryInfo.dist+")"+"' id='" + queryInfo.id +"'> (U) "+queryInfo.orgname+ " (distance: "+ queryInfo.dist+") </option>");
}
for (counter = 0; counter<refOrgs.length; counter++) {
    var orgInfo = refOrgs[counter];
    typestr = (orgInfo.typestrain) ? orgInfo.typestrain : "false";
    if (typestr == "true") {
    $('#speciessel').append("<option value='"+orgInfo.id+"' data-title='(T) "+ orgInfo.orgname + " (distance: "+ orgInfo.dist+")"+"' id='" + orgInfo.id +"'>(T) "+orgInfo.orgname+ " (distance: "+ orgInfo.dist+") </option>");
    } else {
    $('#speciessel').append("<option value='"+orgInfo.id+"' data-title='"+ orgInfo.orgname + " (distance: "+ orgInfo.dist+")"+"' id='" + orgInfo.id +"'>"+orgInfo.orgname+ " (distance: "+ orgInfo.dist+") </option>");
   }
   }
for (counter2 = 0; counter2<outgroups.length; counter2++) {
    var outgrInfo = outgroups[counter2];
    $('#outgrsel').append("<option value='"+outgrInfo.id+"' data-title='"+ outgrInfo.orgname + " (distance: "+ outgrInfo.dist+")"+"' id='" + outgrInfo.id +"'>"+outgrInfo.orgname+ " (distance: "+ outgrInfo.dist+") </option>");
}
loadDefaults('#speciessel','#specieslist',5);
loadDefaults('#outgrsel','#outgrlist',5);
}

function getOrgs() {
var jobid = $('#jobinfo').val();
$.ajax({
        // Your server script to process the upload
        contentType: 'application/json',
        url: '/results/'+jobid+'/step2/orgs',
        async: true,
        cache: false,
        contentType: false,
        processData: false,
        success: orgSuccess,
        error: orgError});

}
function geneError(xhr,ajaxOptions,thrownError) { // communication error
console.log(xhr,ajaxOptions,thrownError);
}

function geneSuccess(data,textStatus,xhr) {
    var counter;
    for (counter=0; counter<data.length; counter++) {
        var geneInfo = data[counter];
        console.log(geneInfo);
        $('#mlstsel').append("<option id='" + geneInfo.acc + "' data-title='"+ geneInfo.name +": "+geneInfo.desc+"' value='"+geneInfo.acc+"'>" + geneInfo.name +": "+geneInfo.desc+"</option>");
        }
    loadDefaults('#mlstsel','#mlstlist',10);
}

function getGenes() {
var jobid = $('#jobinfo').val();
$.ajax({
        // Your server script to process the upload
        contentType: 'application/json',
        url: '/results/'+jobid+'/step3/genes',
        async: true,
        cache: false,
        contentType: false,
        processData: false,
        success: geneSuccess,
        error: geneError});

}