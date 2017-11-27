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




function addtolist(id1,id2) {
var optionList = [];
    $(id1+' > option:selected').each(function() {
    var speciesOption = "<option value='"+$(this).val()+"' class='"+hashCode($(this).val())+" picked' data-title='"+$(this).data("title")+"'>"+$(this).data("title")+"</option>";
    optionList.unshift(speciesOption);
    removeFromList(id2, $(this).val()); //removes any item that already has this class from the list it'll get added to -> problem on step 2 if same species in outgroups and regular species
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
function removeFromList(id10, selectedValue) {
    var y = "."+hashCode(selectedValue);
    $(id10+" > option").remove(y);
    //console.log(selectedValue,hashCode(selectedValue));
}

function removeAllFromList(id3) {
    var selectedValues2=$(id3).val();
    var k;
    for (k = 0; k < selectedValues2.length;k++) {
    removeFromList(id3, selectedValues2[k]);
    }
}


function refreshView(id4,max,warnbox) {
var counter = 0;
$(id4+" > option").each(function() {
     counter++;
    if (counter > max) {
        $(this).addClass("bg-danger text-danger");
        $(this).removeClass("picked");
        $(warnbox).removeClass("hidden");
        console.log(this);
     } else {
        $(this).addClass("picked");
        $(this).removeClass("bg-danger text-danger");
        $(warnbox).addClass("hidden");
     }
});
}
function loadDefaults(id5,id6,max2) {
var counter = 0;
$(id5+" > option").each(function() {
    counter++;
    if (counter <= max2) {
        this.selected=true;
        /*console.log(counter);
        console.log($(this));
        console.log(this.selected);*/
    }
});
addtolist(id5,id6);
}

function loadSelected(id8,id9,idList) {
$(id8+" >option").each(function() {
    // iterate over idlist, set selected to true if matches?
    for (organismId in idList) {
        if ($(this).attr("id") == idList[organismId]) {
        this.selected=true;
        }
    }
});
addtolist(id8,id9);
}

function resetSels(id11,id12,max3) {
    $(id11+'> option:selected').each(function() {
    this.selected = false;
    });
    $(id12).empty();
    loadDefaults(id11,id12,max3);
    }

function selectAndSend(id7) {
var validation = validateForm();
if (validation == "validated") {
$('.selectablewarn').addClass('hidden');
$(".picked").each(function() {
this.selected=true;
});
$(id7).submit();
} else {
$('.selectablewarn').removeClass('hidden');
}
}

