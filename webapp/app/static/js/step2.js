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
var refOrgs = jsonOrgs["reforgs"]; //how to handle if only query orgs remaining?
 for (var group in groupList) {
                var groupId = groupList[group]+"id";
                var groupName = groupList[group]+"name";
                $("#specieslist > .picked").each(function(){
                    var currId = $(this).val();
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


function outgroupPick() {
var commonTax = commonGroup();
var allOutgroups = jsonOrgs["outgroups"]; // change?
var groupId = commonTax[0]+"id";
var counter;
$('#outgrsel > option').each(function() {
    var currId = $(this).attr("id");
    for (counter=0; counter<allOutgroups.length; counter++) {
        var outgrInfo = allOutgroups[counter];
        if (currId == outgrInfo.id) {
            if (outgrInfo[groupId] == commonTax[1]) {
                console.log(outgrInfo[groupId]);
                $(this).attr("disabled", true);
                this.selected = false;
                removeFromList('#outgrlist', $(this).val());
            } else {
                $(this).removeAttr("disabled");
            }
        }
    }
});
if (!($('#outgrsel > option:not([disabled])').length)) {
    $('#nooutgroups').removeClass("hidden");
} else {
    $('#nooutgroups').addClass("hidden");
}
}


function outgroupError(xhr,ajaxOptions,thrownError) { // communication error
console.log(xhr,ajaxOptions,thrownError);
}

function outgroupSuccess(data,textStatus,xhr) {
//console.log(data);
var counter;
for (counter=0; counter<data.length;counter++) {
    var outgrInfo = data[counter];
    $('#outgrsel > option').remove('#'+outgrInfo.id);
    $('#outgrsel').prepend("<option value='"+outgrInfo.id+"' data-title='"+ outgrInfo.orgname + " (mean distance: "+ parseFloat(outgrInfo.dist).toFixed(3)+")"+"' id='" + outgrInfo.id +"'>"+outgrInfo.orgname+ " (mean distance: "+ parseFloat(outgrInfo.dist).toFixed(3)+") </option>");
}
if (!($('#outgrsel > option:not([disabled])').length)) {
    $('#nooutgroups').removeClass("hidden");
} else {
    $('#nooutgroups').addClass("hidden");
}
}

function outgroupLoad() {
var jobid = $('#jobinfo').val();
var commonTax = commonGroup();
//console.log(commonTax);
$.ajax({
        // Your server script to process the upload
        contentType: 'application/json',
        url: '/results/'+jobid+'/step2/outgroups?group='+commonTax[0]+'&id='+commonTax[1],
        async: true,
        cache: false,
        contentType: false,
        processData: false,
        success: outgroupSuccess,
        error: outgroupError});
}
function moreSeqsError(xhr,ajaxOptions,thrownError) { // communication error
console.log(xhr,ajaxOptions,thrownError);
}

function moreSeqsSuccess(data,textStatus,xhr) {
var counter;
var refOrgs=data["reforgs"];
for (counter=0; counter<refOrgs.length;counter++) {
    var orgInfo = refOrgs[counter];
    typestr = (orgInfo.typestrain) ? orgInfo.typestrain : "false";
    if (typestr == true) {
    $('#speciessel').append("<option value='"+orgInfo.id+"' data-title='(T) "+ orgInfo.orgname + " (mean distance: "+ parseFloat(orgInfo.dist).toFixed(3)+")"+"' id='" + orgInfo.id +"'>(T) "+orgInfo.orgname+ " (mean distance: "+ parseFloat(orgInfo.dist).toFixed(3)+") </option>");
    } else {
    $('#speciessel').append("<option value='"+orgInfo.id+"' data-title='"+ orgInfo.orgname + " (mean distance: "+ parseFloat(orgInfo.dist).toFixed(3)+")"+"' id='" + orgInfo.id +"'>"+orgInfo.orgname+ " (mean distance: "+ parseFloat(orgInfo.dist).toFixed(3)+") </option>");
   }
    }
    refInfo.rows.add(data["reforgs"]).draw();
}


function loadMore() {
var jobid = $('#jobinfo').val();
var loadedSeqs = $('#speciessel > option').length - jsonOrgs["queryorgs"].length;
console.log(loadedSeqs);
$.ajax({
        // Your server script to process the upload
        contentType: 'application/json',
        url: '/results/'+jobid+'/step2/orgs?start='+loadedSeqs,
        async: true,
        cache: false,
        contentType: false,
        processData: false,
        success: moreSeqsSuccess,
        error: moreSeqsError});
}


/*function validateForm() {
if ($('.selectablein').has('option').length>0 && $('.selectablein2').has('option').length>0) {
return "validated";
} else {
return "notvalidated";}
} */

function validateForm() {
if ($('.selectablein >option').length>4 && $('.selectablein2 > option').length>0) {
return "validated";
} else {
return "notvalidated";}
}