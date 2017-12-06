function orgError(xhr,ajaxOptions,thrownError) { // communication error
console.log(xhr,ajaxOptions,thrownError);
}

function speciesSearch() {
    var searchval = $('#speciessearch').val().toLowerCase();
    $('#speciessel > option').each(function() {
        var test = ($(this).text().toLowerCase().indexOf(searchval) > -1);
        $(this).toggle(test);
        if (test && searchval.length) {
            $(this).css("color","#0000ff");
        } else {
            $(this).css("color","");
        }
    });
}

function outgrSearch() {
    var searchval = $('#outgroupsearch').val().toLowerCase();
    $('#outgrsel > option').each(function() {
        var test = ($(this).text().toLowerCase().indexOf(searchval) > -1);
        $(this).toggle(test);
        if (test && searchval.length) {
            $(this).css("color","#0000ff");
        } else {
            $(this).css("color","");
        }
        if (test && searchval.length && $(this).is(':disabled')) {
            $(this).toggle(false);
            $(this).css("color","");
        }
    });
}
var speciesTimer = 1000;
var speciesStarted = false;

function speciesQueue() {
    //console.log('SQ running');
    if (speciesTimer <= 0) {
        speciesSearch();
        speciesStarted = false;
    } else {
        speciesTimer -= 100;
        setTimeout(speciesQueue, 100);
    }
}
$(document).ready(function() {
$('#speciessearch').on("keyup", function() {
    //console.log('Search running');
    speciesTimer = 1000;
    if (speciesStarted == false) {
        speciesQueue();
        speciesStarted = true;
    }
});
});

var outgrTimer = 1000;
var outgrStarted = false;

function outgrQueue() {
    if (outgrTimer <= 0) {
        outgrSearch();
        outgrStarted = false;
    } else {
        outgrTimer -= 100;
        setTimeout(outgrQueue, 100);
    }
}
$(document).ready(function() {
$('#outgroupsearch').on("keyup", function() {
    outgrTimer = 1000;
    if (outgrStarted == false) {
        outgrQueue();
        outgrStarted = true;
    }
});
});


var jsonOrgs = false;
function commonGroup() {
var counter, counter2, commonTaxId;
//var selectedList = [];
var allGroup = {};
var groupList = ["genus","family","order","phyl"];
var refOrgs = $.extend(jsonOrgs["reforgs"], jsonOrgs["queryorgs"]); //how to handle if only query orgs remaining?
 for (var group in groupList) {
                var groupId = groupList[group]+"id";
                var groupName = groupList[group]+"name";
                $("#specieslist > .picked").each(function(){
                    var currId = $(this).val();
                    var currGroup = $(this).data(groupId);
                    var currName = $(this).data(groupName)
                    if (currGroup != "N/A" && currName != "N/A") {
                                allGroup[currGroup] = currName;
                                //console.log(allGroup);
                                }
                    /*for (counter=0; counter<refOrgs.length; counter++) {
                        var refInfo = refOrgs[counter];
                            if (currId == refInfo.id) {
                                //selectedList.push(refInfo);
                                var currGroup = refInfo[groupId];
                                var currName = refInfo[groupName];
                                if (currGroup != "N/A" && currName != "N/A") {
                                allGroup[currGroup] = currName;
                                console.log(allGroup);
                                }
                                }
                        }*/
                });
                if (Object.keys(allGroup).length == 1) {
                commonTaxId = Object.keys(allGroup);
                var commonInfo = [groupList[group], commonTaxId[0], allGroup[commonTaxId[0]]];
                //console.log(commonInfo);
                return commonInfo;
                } else if (groupList[group] == "phyl" && Object.keys(allGroup).length > 1){
                commonTaxId = Object.keys(allGroup);
                var multiGroups = [];
                for (var idkey in commonTaxId) {
                multiGroups.push(allGroup[commonTaxId[idkey]]);
                }
                var commonInfo = [groupList[group], commonTaxId, multiGroups];
                console.log(commonInfo);
                return commonInfo
                }
                allGroup = {};
}
}
function outgroupPick() {
var commonTax = commonGroup();
console.log(typeof commonTax[1]);
if (typeof commonTax[1] == "string") {
//var allOutgroups = jsonOrgs["outgroups"]; // change?
var groupId = commonTax[0]+"id";
//var counter;
$('#outgrsel > option').each(function() {
    var currId = $(this).attr("id");
    if ($(this).data(groupId) == commonTax[1]) {
    $(this).attr("disabled", true);
                this.selected = false;
                removeFromList('#outgrlist', $(this).val());
    } else {
    $(this).removeAttr("disabled"); // faster to remove disabled from the start?
    }
    /*for (counter=0; counter<allOutgroups.length; counter++) {
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
    }*/
});
$('#commgroup').text(commonTax[2]);
if (!($('#outgrsel > option:not([disabled])').length)) {
    $('#nooutgroups').removeClass("hidden");
} else {
    $('#nooutgroups').addClass("hidden");
}
refreshView('#outgrlist',5,'#outgrlimit');
outgrSearch();
} else if (typeof commonTax[1] == "object") {
    //var allOutgroups = jsonOrgs["outgroups"]; // change?
    var groupId = commonTax[0]+"id";
    var counter2;
    $('#outgrsel > option').each(function() {
    //var currId = $(this).attr("id");
    $(this).removeAttr("disabled");
    for (counter2=0; counter2<commonTax[1].length; counter2++) {
            currTax = commonTax[1][counter2];
            if ($(this).data(groupId) == currTax) {
            $(this).attr("disabled", true);
            this.selected = false;
            removeFromList('#outgrlist', $(this).val());
            $(this).remove();
            $('#outgrsel').append($(this));
            console.log(currTax);
            }
            }
    /*for (counter=0; counter<allOutgroups.length; counter++) {
    var outgrInfo = allOutgroups[counter];
    if (currId == outgrInfo.id) {
        for (counter2=0; counter2<commonTax[1].length; counter2++) {
            currTax = commonTax[1][counter2];
            if (outgrInfo[groupId] == currTax) {
            $(this).attr("disabled", true);
            this.selected = false;
            removeFromList('#outgrlist', $(this).val());
            $(this).remove();
            $('#outgrsel').append($(this));
            console.log(currTax);
            }
        }
    }
    }*/
    });
    $('#commgroup').text(commonTax[2].join(", "));
if (!($('#outgrsel > option:not([disabled])').length)) {
    $('#nooutgroups').removeClass("hidden");
} else {
    $('#nooutgroups').addClass("hidden");
}
refreshView('#outgrlist',5,'#outgrlimit');
outgrSearch();
} else {
    $('#nooutgroups').removeClass("hidden");
    $('#outgrsel > option').each(function() {
    $(this).attr("disabled", true);
    this.selected = false;
    removeFromList('#outgrlist', $(this).val());
    $('#commgroup').text("No common group found");
    });
    outgrSearch();
}
}

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
    $('#speciessel').append("<option value='"+queryInfo.id+"' data-title='(U) "+ queryInfo.orgname + " (detected genus: "+ queryInfo.genusname +")"+"' id='" + queryInfo.id +"' data-genusid='"+queryInfo.genusid+"' data-genusname='"+queryInfo.genusname+"' data-familyid='"+queryInfo.familyid+"' data-familyname='"+queryInfo.familyname+"' data-orderid='"+queryInfo.orderid + "' data-ordername='"+queryInfo.ordername+"' data-phylid='"+queryInfo.phylid+"' data-phylname='"+queryInfo.phylname+"'> (U) "+queryInfo.orgname+ " (detected genus: "+ queryInfo.genusname+") </option>");
}
for (counter = 0; counter<refOrgs.length; counter++) {
    var orgInfo = refOrgs[counter];
    typestr = (orgInfo.typestrain) ? orgInfo.typestrain : "false";
    if (typestr == true) {
    $('#speciessel').append("<option value='"+orgInfo.id+"' data-title='(T) "+ orgInfo.orgname + " (mean distance: "+ parseFloat(orgInfo.dist).toFixed(3)+")"+"' id='" + orgInfo.id + "' data-genusid='"+orgInfo.genusid+"' data-genusname='"+orgInfo.genusname+"' data-familyid='"+orgInfo.familyid+"' data-familyname='"+orgInfo.familyname+"' data-orderid='"+orgInfo.orderid + "' data-ordername='"+orgInfo.ordername+"' data-phylid='"+orgInfo.phylid+"' data-phylname='"+orgInfo.phylname+"'>(T) "+orgInfo.orgname+ " (mean distance: "+ parseFloat(orgInfo.dist).toFixed(3)+") </option>");
    } else {
    $('#speciessel').append("<option value='"+orgInfo.id+"' data-title='"+ orgInfo.orgname + " (mean distance: "+ parseFloat(orgInfo.dist).toFixed(3)+")"+"' id='" + orgInfo.id +"' data-genusid='"+orgInfo.genusid+"' data-genusname='"+orgInfo.genusname+"' data-familyid='"+orgInfo.familyid+"' data-familyname='"+orgInfo.familyname+"' data-orderid='"+orgInfo.orderid + "' data-ordername='"+orgInfo.ordername+"' data-phylid='"+orgInfo.phylid+"' data-phylname='"+orgInfo.phylname+"'>"+orgInfo.orgname+ " (mean distance: "+ parseFloat(orgInfo.dist).toFixed(3)+") </option>");
   }
   }
for (counter2 = 0; counter2<outgroups.length; counter2++) {
    var outgrInfo = outgroups[counter2];
    $('#outgrsel').append("<option value='"+outgrInfo.id+"' data-title='"+ outgrInfo.orgname + " (mean distance: "+ parseFloat(outgrInfo.dist).toFixed(3)+")"+"' id='" + outgrInfo.id +"' data-genusid='"+outgrInfo.genusid+"' data-genusname='"+outgrInfo.genusname+"' data-familyid='"+outgrInfo.familyid+"' data-familyname='"+outgrInfo.familyname+"' data-orderid='"+outgrInfo.orderid + "' data-ordername='"+outgrInfo.ordername+"' data-phylid='"+outgrInfo.phylid+"' data-phylname='"+outgrInfo.phylname+"'>"+outgrInfo.orgname+ " (mean distance: "+ parseFloat(outgrInfo.dist).toFixed(3)+") </option>");
}
if (data["selspecies"] && data["seloutgroups"]) {
    var selectedSpecies = data["selspecies"];
    var selectedOutgroups = data["seloutgroups"];
    loadSelected('#speciessel','#specieslist',selectedSpecies);
    outgroupPick();
    loadSelected('#outgrsel','#outgrlist',selectedOutgroups);
} else {
    loadDefaults('#speciessel','#specieslist',50);
    outgroupPick();
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








function outgroupError(xhr,ajaxOptions,thrownError) { // communication error
console.log(xhr,ajaxOptions,thrownError);
}

function outgroupSuccess(data,textStatus,xhr) {
//console.log(data);
var counter;
for (counter=0; counter<data.length;counter++) {
    var outgrInfo = data[counter];
    $('#outgrsel > option').remove('#'+outgrInfo.id); //fix ordering?
    $('#outgrsel').prepend("<option value='"+outgrInfo.id+"' data-title='"+ outgrInfo.orgname + " (mean distance: "+ parseFloat(outgrInfo.dist).toFixed(3)+")"+"' id='" + outgrInfo.id +"' data-genusid='"+outgrInfo.genusid+"' data-genusname='"+outgrInfo.genusname+"' data-familyid='"+outgrInfo.familyid+"' data-familyname='"+outgrInfo.familyname+"' data-orderid='"+outgrInfo.orderid + "' data-ordername='"+outgrInfo.ordername+"' data-phylid='"+outgrInfo.phylid+"' data-phylname='"+outgrInfo.phylname+"'>"+outgrInfo.orgname+ " (mean distance: "+ parseFloat(outgrInfo.dist).toFixed(3)+") </option>");
}
if (!($('#outgrsel > option:not([disabled])').length)) {
    $('#nooutgroups').removeClass("hidden");
} else {
    $('#nooutgroups').addClass("hidden");
}
$('#outgroupsearch').val("");
outgrSearch();
}

function outgroupLoad() {
var jobid = $('#jobinfo').val();
var commonTax = commonGroup();
//add check for if no options in outgrsel?
if (!($('#outgrsel > option:not([disabled])').length)) {
if (typeof commonTax[1] == "string") {
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
} else if (typeof commonTax[1] == "object") {
$.ajax({
        // Your server script to process the upload
        contentType: 'application/json',
        url: '/results/'+jobid+'/step2/outgroups?group='+commonTax[0]+'&id='+commonTax[1].toString()+'&multiple=True',
        async: true,
        cache: false,
        contentType: false,
        processData: false,
        success: outgroupSuccess,
        error: outgroupError});
}
}
}

function moreSeqsError(xhr,ajaxOptions,thrownError) { // communication error
console.log(xhr,ajaxOptions,thrownError);
}

function moreSeqsSuccess(data,textStatus,xhr) {
var counter;
var refOrgs=data["reforgs"];
jsonOrgs["reforgs"] = $.extend(jsonOrgs["reforgs"],data["reforgs"]);
for (counter=0; counter<refOrgs.length;counter++) {
    var orgInfo = refOrgs[counter];
    typestr = (orgInfo.typestrain) ? orgInfo.typestrain : "false";
    if (typestr == true) {
    $('#speciessel').append("<option value='"+orgInfo.id+"' data-title='(T) "+ orgInfo.orgname + " (mean distance: "+ parseFloat(orgInfo.dist).toFixed(3)+")"+"' id='" + orgInfo.id +"' data-genusid='"+orgInfo.genusid+"' data-genusname='"+orgInfo.genusname+"' data-familyid='"+orgInfo.familyid+"' data-familyname='"+orgInfo.familyname+"' data-orderid='"+orgInfo.orderid + "' data-ordername='"+orgInfo.ordername+"' data-phylid='"+orgInfo.phylid+"' data-phylname='"+orgInfo.phylname+"'>(T) "+orgInfo.orgname+ " (mean distance: "+ parseFloat(orgInfo.dist).toFixed(3)+") </option>");
    } else {
    $('#speciessel').append("<option value='"+orgInfo.id+"' data-title='"+ orgInfo.orgname + " (mean distance: "+ parseFloat(orgInfo.dist).toFixed(3)+")"+"' id='" + orgInfo.id +"' data-genusid='"+orgInfo.genusid+"' data-genusname='"+orgInfo.genusname+"' data-familyid='"+orgInfo.familyid+"' data-familyname='"+orgInfo.familyname+"' data-orderid='"+orgInfo.orderid + "' data-ordername='"+orgInfo.ordername+"' data-phylid='"+orgInfo.phylid+"' data-phylname='"+orgInfo.phylname+"'>"+orgInfo.orgname+ " (mean distance: "+ parseFloat(orgInfo.dist).toFixed(3)+") </option>");
   }
    }
    refInfo.rows.add(data["reforgs"]).draw();
    $('#speciessearch').val("");
    speciesSearch();
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
//



/*$(document).ready(function() {
    $('#speciessearch').on("keyup", function() {
        var searchval = $(this).val().toLowerCase();
        $('#speciessel > option').each(function() {
        var test = ($(this).text().toLowerCase().indexOf(searchval) > -1);
        $(this).toggle(test);
        if (test && searchval.length) {
            $(this).css("color","#0000ff");
        } else {
            $(this).css("color","");
        }
        });
    });
});

$(document).ready(function() {
    $('#outgroupsearch').on("keyup", function() {
        var searchval2 = $(this).val().toLowerCase();
        $('#outgrsel > option').each(function() {
        var test = ($(this).text().toLowerCase().indexOf(searchval2) > -1);
        $(this).toggle(test);
        if (test && searchval2.length) {
            $(this).css("color","#0000ff");
        } else {
            $(this).css("color","");
        }
        });
    });
}); */

function validateForm() {
if ($('.selectablein >option').length>4 && $('.selectablein2 > option').length>0) {
return "validated";
} else {
return "notvalidated";}
}