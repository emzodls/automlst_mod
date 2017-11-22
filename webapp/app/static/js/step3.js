function geneError(xhr,ajaxOptions,thrownError) { // communication error
console.log(xhr,ajaxOptions,thrownError);
}

function geneSuccess(data,textStatus,xhr) {
    var counter;
    var mlstGenes = data["genes"];
    var selectedGenes = data["selected"];
    var deletedOrgs = data["deletedorgs"];
    for (counter=0; counter<mlstGenes.length; counter++) {
        var geneInfo = mlstGenes[counter];
        console.log(geneInfo);
        $('#mlstsel').append("<option id='" + geneInfo.acc + "' data-title='"+ geneInfo.name +": "+geneInfo.desc+"' value='"+geneInfo.acc+"'>" + geneInfo.name +": "+geneInfo.desc+"</option>");
        }
     if (data["selected"]) {
        loadSelected('#mlstsel','#mlstlist',selectedGenes);
     } else {
        loadDefaults('#mlstsel','#mlstlist',100);
    }
    if (data["deletedorgs"]) {
        var counter2;
        for (counter2=0;counter2<deletedOrgs.length;counter2++){
            var delInfo = deletedOrgs[counter2];
            $('#todelete').append("<li>"+delInfo.orgname+"</li>");
        }
        $('#deletewarning').removeClass("hidden");
    }
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

function validateForm() {
if ($('.selectablein').has('option').length>0) {
return "validated";
} else {
return "notvalidated";}
}