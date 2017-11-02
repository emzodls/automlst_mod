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