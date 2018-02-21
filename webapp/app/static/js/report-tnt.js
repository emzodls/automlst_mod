var jobid = $('#jobinfo').val();

function nodeFill(node) {
    //var nodeIndex = node.node_name().search('ANIid_95');
    var nodeAni = node.property('ANIid');
    if (nodeAni in aniTable) {
        return aniTable[nodeAni];
    } else {
        //console.log(nodeAni);
        return "black";
    }

}

function subtreeFill(node, searchId) {
if (node.property('ANIid') == searchId) {
    if (searchId in aniTable) {
        return aniTable[searchId];
    } else {
        return "black";
    }
} else {
    return "black";
}
}

function strainTypeNodes(node) {
//if (node.is_leaf()) {
if (node.node_name().search("QS--") != -1) {
              return '#0000ff';
            }
            else if (node.node_name().search("OG--") != -1) {
              return '#cc3300';
            }
            else if (node.node_name().search("TS--") != -1) {
              return '#1f7a1f';
            }
            return '#888888';
}
/*return '#888888';
}*/

function setSvg() {
$('svg').attr('xmlns',"http://www.w3.org/2000/svg");
$('svg').attr('xmlns:xlink', "http://www.w3.org/1999/xlink");
var treeSvg = $('#svgCanvas').html();
                var fileNameToSave = "treetest3.svg";
                treeSvg = '<?xml version="1.0" standalone="no"?>\r\n' + treeSvg;
                var url = "data:image/svg+xml;charset=utf-8,"+encodeURIComponent(treeSvg);
                //console.log(url);
                $('#imgdownl').attr("href",url);
                $('#imgdownl').attr("download", fileNameToSave);
                }


function treeSuccess(data,textStatus,xhr) {
if (data != "false") {
	$('#svgCanvas').empty();
	//$('#svgCanvas').addClass("hidden");
    $('#sizebtns').attr("style","display:block");
    $('#searchdiv').attr("style","display:block");
    var newick = data.toString();
    //console.log(newick);
    tree = tnt.tree();
     tree
     .data (tnt.tree.parse_newick(newick))
    .node_display(tree.node_display()
            .size(function(node) {
            if (node.is_leaf()) {
                return 4;
            } else {
                return 3;
            }
            })
            .fill(function(node) {
            if (node.is_leaf()) {
                return strainTypeNodes(node);
            }
            return '#888888';
            })
        )
        .label (tnt.tree.label.text()
            .fontsize(12)
            .height(30)
            .text (function (node) {
            return node.node_name();
        })
            .color("black")
        )
        .layout(tnt.tree.layout.vertical()
            .width(1000)
            .scale(false)
        );
        root = tree.root();
        leaves = root.get_all_leaves();
        for (var leafNode in leaves) {
        var nodeIndex = leaves[leafNode].node_name().search('ANIid_95');
        var nodeAni = leaves[leafNode].node_name().slice(nodeIndex+9);
        leaves[leafNode].property('ANIid', nodeAni); // store as property so the name won't have to be searched every time
        }
        /*streptonodes = root.find_all(function(node) {
            return (node.node_name().toString().search('Streptomyces') != -1);
        });
        console.log(streptonodes);*/
      tree(document.getElementById("svgCanvas"));
          clearInterval(timer);
      //console.log(tree.layout().width());
      var aniDict = {};
      $('text.tnt_tree_label:contains("ANIid_95")').each(function() { // still needed, since node height can only be accessed by labels' offsets
        var aniIndex = $(this).text().search('ANIid_95');
        var aniId = $(this).text().slice(aniIndex+9).replace(/_/g, "");
        if (!(aniId in aniDict)) {
            aniDict[aniId] = [];
        }
        aniDict[aniId].push($(this).offset().top); //get y-position of branches relative to page
      });
      // create array of arrays storing highest branch height (lowest y-offset) & ANI id
      var sortableAni = [];
      for (var z in aniDict) {
      if (aniDict[z].length > 1) {
      higherBranch = Math.min.apply(null,aniDict[z]);
      sortableAni.push([higherBranch, z]);
      }
      }
      //sort by y-position
      sortableAni.sort(function(a,b){
        return a[0]-b[0];
      });
      /*var sortedAni = {};
      for (var a in sortableAni) {
      sortedAni[sortableAni[a][0]] = sortableAni[a][1];
      }

      console.log(sortedAni);*/
      //var aniList = [];
      //var prettyColors = ["#8B0000","#cc3600","#b36200","#7b7737","#556B2F","#006400"," #2d8653","#008080","#396a93","#00008B","#4B0082","#800080","#C71585","#DC143C"]; //sorted array of colors -> rainbow
      var prettyColors = [ "#00990d", "#9900ff", " #e6007a", "#0000CD"];
      var amountColors = prettyColors.length;
      /*for (var x in sortedAni) {
        aniList.push(sortedAni[x]);
      }*/
      aniTable = {};
      /*for (var y in aniList) {
      aniTable[aniList[y]] = prettyColors[y % amountColors]
      }*/
      // iterate through list, pair each entry with color value
      for (var y in sortableAni) {
      aniTable[sortableAni[y][1]] = prettyColors[y % amountColors];
      }
      /*tree.label().color(function(node) {
        return nodeFill(node);
      });
      tree.update_nodes();*/

        tree.on("click", function(node) {
            if (node.is_leaf()) {
            var ani95 = node.property('ANIid');
            //console.log(ani95);
            tree.label().color(function(node) {
                return subtreeFill(node,ani95);
            });
            } else {
                tree.label().color('black')
            }
            $('#colorkey').removeClass("hidden");
            $('#tscolorscheme').addClass('hidden');
            $('#anicolorscheme').addClass('hidden');
            $('#aniicon').css('color',subtreeFill(node,ani95));
            $('#selectedani').text(ani95);
            $('#singleani').removeClass('hidden');
            tree.update_nodes();
            setSvg();
        });
        setSvg();
        $('#svgCanvas').addClass('printable');
        $('#svgCanvas *').addClass('printable');

} else {
    $('#treefail').removeClass("hidden");
    $('#svgCanvas').addClass("hidden");
    clearInterval(timer);
}
}

function treeError(xhr,ajaxOptions,thrownError) { // communication error
console.log(xhr,ajaxOptions,thrownError);
}
function drawTree() {
//console.log(jobid);
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

/*function downloadPng() {
    var pngExport = tnt.utils.png()
        .filename(jobid+"tree._png");
    pngExport(d3.select("#svgCanvas"));
}*/

function resizeTree(resizeDir) {
    var treeWidth = tree.layout().width();

    if (resizeDir == 'upH') {
        /*var treeLayout = tnt.tree.layout.vertical().width(treeWidth+100).scale(false);
        tree.layout(treeLayout);*/
        tree.layout().width(treeWidth+100);
    } else if (resizeDir == 'downH' && treeWidth > 500) {
        /*var treeLayout = tnt.tree.layout.vertical().width(treeWidth - 100).scale(false);
        tree.layout(treeLayout);*/
        tree.layout().width(treeWidth - 100);
    }
    tree.update();
    setSvg();
}

function treeFontSize(node,value) {
//console.log('TEST');
if (node.is_leaf()) {
    var name = node.node_name();
    if (name.toLowerCase().search(value.toLowerCase()) != -1) {
        return 14;
    }
    return 12;
}
    return 12;
    }

function searchTree() {
var value = $('#searchtree').val().toLowerCase();
if (value.length) {
    tree.label().fontsize(function(node) {
        return treeFontSize(node,value);
    });
    tree.update();
    }
    else {
    tree.label().fontsize(12);
    tree.update();
    }
}

function showAniGroups() {
$('#colorkey').removeClass('hidden');
$('#tscolorscheme').addClass('hidden');
$('#singleani').addClass('hidden');
$('#anicolorscheme').removeClass('hidden');
tree.label().color(function(node) {
if (node.is_leaf()) {
    return nodeFill(node);
    }
    else {
    return 'black';
    }
});
tree.update_nodes();
setSvg();
}

function showTypeStrains() {
$('#colorkey').removeClass('hidden');
$('#anicolorscheme').addClass('hidden');
$('#singleani').addClass('hidden');
$('#tscolorscheme').removeClass('hidden');
tree.label().color(function(node) {
    return strainTypeNodes(node);
});
tree.update_nodes();
setSvg();
}

function resetColor() {
$('#colorkey').addClass("hidden");
$('#tscolorscheme').addClass('hidden');
$('#anicolorscheme').addClass('hidden');
$('#singleani').addClass('hidden');
tree.label().color('black');
tree.update_nodes();
setSvg();
}

treeTimer = 0;

function startSearch() {
clearTimeout(treeTimer);
treeTimer = setTimeout(searchTree, 1000);
}

$(document).ready(function () {
$('#searchtree').on("keyup", startSearch);
});

/*function treeQueue() {
    console.log('TQ running');
    if (treeTimer <= 0) {
        searchTree();
        treeStarted = false;
    } else {
        treeTimer -= 100;
        setTimeout(treeQueue, 100);
    }
}
$(document).ready(function() {
$('#searchtree').on("change", function() {
    //console.log('Search running');
    treeTimer = 1000;
    if (treeStarted == false) {
        treeQueue();
        treeStarted = true;
    }
});
}); */

function toggleScale() {
if (tree.layout().scale()) {
    tree.layout().scale(false);
} else {
    tree.layout().scale(true);
    }
    tree.update();
    setSvg();
}

function treePopup() {
    var treeWindow = window.open("","Tree View");
    treeWindow.document.write($('#svgCanvas *').html());
}


function uploadSuccess(data,textStatus,xhr) {
console.log('SUCCESS');
}
function uploadError(xhr,ajaxOptions,thrownError) {
console.log('FAIL');
}

function uploadTree() {
var treeToSvg = $('#svgCanvas').html();
treeToSvg = '<?xml version="1.0" standalone="no"?>\r\n' + treeToSvg;
$.ajax({
    contentType: 'image/svg+xml',
        url: '/sendtree',
        async: true,
        type: 'POST',
        //Form data
        data: treeToSvg,
        cache: false,
        contentType: false,
        processData: false,
        success: uploadSuccess,
        error: uploadError
});
}

$("button[data-toggle='tooltip']").on('click',function(){
    $(this).blur();
})

var timer = setInterval(drawTree, 3000);