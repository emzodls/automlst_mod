var jobid = $('#jobinfo').val();
function treeSuccess(data,textStatus,xhr) {
if (data != "false") {
	$('#svgCanvas').empty();
    $('#sizebtns').attr("style","display:block");
    $('#searchdiv').attr("style","display:block");
    var newick = data.toString();
    //console.log(newick);
    tree = tnt.tree();
     tree
     .data (tnt.tree.parse_newick(newick))
    .node_display(tree.node_display()
            .size(4)
            .fill("#888888")
        )
        .label (tnt.tree.label.text()
            .fontsize(12)
            .height(30)
            .text (function (node) {
            return node.node_name();
        })
            .color(function(node) {
            if (node.node_name().search("QS--") != -1) {
              return '#0000ff';
            }
            else if (node.node_name().search("TS--") != -1) {
              return '#1f7a1f';
            }
            else if (node.node_name().search("OG--") != -1) {
              return '#cc3300';
            }
            return 'black';
   })
        )
        .layout(tnt.tree.layout.vertical()
            .width(800)
            .scale(false)
        );
        root = tree.root();
      tree(document.getElementById("svgCanvas"));
      console.log(tree.layout().width());
    clearInterval(timer);
}
}

function treeError(xhr,ajaxOptions,thrownError) { // communication error
console.log(xhr,ajaxOptions,thrownError);
}
function drawTree() {
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

/*function downloadPng() {
    var pngExport = tnt.utils.png()
        .filename(jobid+"tree._png");
    pngExport(d3.select("#svgCanvas"));
}*/

function resizeTree(resizeDir) {
    var treeWidth = tree.layout().width();
    console.log(treeWidth);

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
}

function treeColor(node,value) {
    var name = node.node_name();
    if (name.toLowerCase().search(value.toLowerCase()) != -1) {
        return 'red';
    }
    return "#888888";
}

function searchTree(value) {
if (value.length) {
    tree.node_display()
    .fill(function(node) {
        return treeColor(node,value);
    });
    tree.update_nodes();
    }
    else {
    tree.node_display().fill('#888888');
    tree.update_nodes();
    }
}

function toggleScale() {
if (tree.layout().scale()) {
    tree.layout().scale(false);
} else {
    tree.layout().scale(true);
    }
    tree.update();
}

$("button[data-toggle='tooltip']").on('click',function(){
    $(this).blur();
})

var timer = setInterval(drawTree, 3000);