function orgError(xhr,ajaxOptions,thrownError) { // communication error
console.log(xhr,ajaxOptions,thrownError);
}
var jsonOrgs = false;
function orgSuccess(data,textStatus,xhr) {
var counter;
var counter2;
var counter3;
jsonOrgs = data;
var queryOrgs = data["queryorgs"];
var refOrgs = data["reforgs"];
var outgroups = data["outgroups"];
for (counter3 = 0; counter3<queryOrgs.length; counter3++) {
    var queryInfo = queryOrgs[counter3];
    $('#speciessel').append("<option value='"+queryInfo.id+"' data-title='(U) "+ queryInfo.orgname + " (detected genus: "+ queryInfo.genusname +")"+"' id='" + queryInfo.id +"'> (U) "+queryInfo.orgname+ " (detected genus: "+ queryInfo.genusname+") </option>");
}
for (counter = 0; counter<refOrgs.length; counter++) {
    var orgInfo = refOrgs[counter];
    typestr = (orgInfo.typestrain) ? orgInfo.typestrain : "false";
    if (typestr == true) {
    $('#speciessel').append("<option value='"+orgInfo.id+"' data-title='(T) "+ orgInfo.orgname + " (mean distance: "+ parseFloat(orgInfo.dist).toFixed(3)+")"+"' id='" + orgInfo.id +"'>(T) "+orgInfo.orgname+ " (mean distance: "+ parseFloat(orgInfo.dist).toFixed(3)+") </option>");
    } else {
    $('#speciessel').append("<option value='"+orgInfo.id+"' data-title='"+ orgInfo.orgname + " (mean distance: "+ parseFloat(orgInfo.dist).toFixed(3)+")"+"' id='" + orgInfo.id +"'>"+orgInfo.orgname+ " (mean distance: "+ parseFloat(orgInfo.dist).toFixed(3)+") </option>");
   }
   }
for (counter2 = 0; counter2<outgroups.length; counter2++) {
    var outgrInfo = outgroups[counter2];
    $('#outgrsel').append("<option value='"+outgrInfo.id+"' data-title='"+ outgrInfo.orgname + " (mean distance: "+ parseFloat(outgrInfo.dist).toFixed(3)+")"+"' id='" + outgrInfo.id +"'>"+outgrInfo.orgname+ " (mean distance: "+ parseFloat(outgrInfo.dist).toFixed(3)+") </option>");
}
if (data["selspecies"] && data["seloutgroups"]) {
    var selectedSpecies = data["selspecies"];
    var selectedOutgroups = data["seloutgroups"];
    loadSelected('#speciessel','#specieslist',selectedSpecies);
    loadSelected('#outgrsel','#outgrlist',selectedOutgroups);
} else {
    loadDefaults('#speciessel','#specieslist',50);
    loadDefaults('#outgrsel','#outgrlist',5);
}
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


function commonGroup() {
var counter, counter2, commonTaxId;
var selectedList = [];
var allGroup = {};
var groupList = ["genus","family","order","phyl"];
var refOrgs = jsonOrgs["reforgs"];
 for (var group in groupList) {
                var groupId = groupList[group]+"id";
                var groupName = groupList[group]+"name";
                $("#specieslist > .picked").each(function(){
                    var currId = $(this).attr("id");
                    for (counter=0; counter<refOrgs.length; counter++) {
                        var refInfo = refOrgs[counter];
                            if (currId == refInfo.id) {
                                selectedList.push(refInfo);
                                var currGroup = refInfo[groupId];
                                var currName = refInfo[groupName];
                                if (currGroup != "N/A" && currName != "N/A") {
                                allGroup[currGroup] = currName;
                                //console.log(allGroup);
                                }
                                }
                        }
                });
                if (Object.keys(allGroup).length == 1) {
                commonTaxId = Object.keys(allGroup);
                var commonInfo = [groupList[group], commonTaxId[0], allGroup[commonTaxId[0]]];
                //console.log(commonInfo);
                return commonInfo;
                }
                allGroup = {};
}
}


function validateForm() {
if ($('.selectablein').has('option').length>0 && $('.selectablein2').has('option').length>0) {
return "validated";
} else {
return "notvalidated";}
}