function geneError(xhr,ajaxOptions,thrownError) { // communication error
console.log(xhr,ajaxOptions,thrownError);
}

function geneSuccess(data,textStatus,xhr) {
    var counter;
    var mlstGenes = data;
    /*var mlstGenes = data["genes"];
    var selectedGenes = data["selected"];*/
    for (counter=0; counter<mlstGenes.length; counter++) {
        var geneInfo = mlstGenes[counter];
        console.log(geneInfo);
        $('#mlstsel').append("<option id='" + geneInfo.acc + "' data-title='"+ geneInfo.name +": "+geneInfo.desc+"' value='"+geneInfo.acc+"' data-del='"+geneInfo.orgdel +"'>" + geneInfo.name +": "+geneInfo.desc+"</option>");
        }
     if (data["selected"]) { //currently an useless check
        loadSelected('#mlstsel','#mlstlist',selectedGenes);
     } else {
        loadDefaults('#mlstsel','#mlstlist',100);
    }
    /*if (data["deletedorgs"]) {
        var counter2;
        for (counter2=0;counter2<deletedOrgs.length;counter2++){
            var delInfo = deletedOrgs[counter2];
            $('#todelete').append("<li>"+delInfo.orgname+"</li>");
        }
        $('#deletewarning').removeClass("hidden");
    } */
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
// not elegant but at least it works
function findDeleted() {
var deletedList = [];
$('#deletewarning').addClass('hidden');
$('#todelete').empty();
$('#mlstlist > option').each(function() {
    if ($(this).data("del")) {
        var currDel = $(this).data("del").split(",");
        var i;
        for (i in currDel) {
            console.log(currDel[i]);
            console.log(deletedList);
            if (deletedList.indexOf(currDel[i]) == -1) {
                deletedList.push(currDel[i]);
                console.log(deletedList);
            }
        }
    }
});
if (deletedList.length > 0) {
    var j;
    for (j in deletedList) {
        $('#todelete').append("<li>"+deletedList[j]+"</li>");
    }
    $('#deletewarning').removeClass("hidden");
    $('#removeorgs').val(deletedList.toString());
}
}

function validateForm() {
if ($('.selectablein').has('option').length>0) {
return "validated";
} else {
return "notvalidated";}
}