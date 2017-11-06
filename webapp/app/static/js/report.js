var dataObject = null;
Smits.PhyloCanvas.Render.Parameters.Rectangular["paddingY"] = 40;
Smits.PhyloCanvas.Render.Parameters.Rectangular["paddingX"] = 90;
function renderTree(dataObject,width,height) {
$('#svgCanvas').empty();
$('#sizebtns').attr("style","display:block");
phylocanvas = new Smits.PhyloCanvas(
				dataObject,
				'svgCanvas',
				width, height
				);
				/* var canvasHeight = parseInt($('svg').attr("height"));
				var canvasWidth = parseInt($('svg').attr("width")); */
				console.log($($('tspan')[0])[0]);
				$('tspan:contains(###)').attr("fill","#0000ff");
/*				$('tspan').each(function(objindex,obj) {
				console.log($(obj));
				console.log(Object.keys($(obj)));
				if ($(obj).html().substring(0,3) == "___") {
				$(obj).attr("fill","#0000ff");
				}
				}); */
}
function repairSize() {
var canvasHeight = parseInt($('svg').attr("height"));
$('text:has(tspan)').each(function(objindex, obj) {
    var textHeight = parseInt($(this).attr("y"));
    if (textHeight > canvasHeight) {
        console.log(textHeight);
        $('svg').attr("height",textHeight +10);
        $('#svgCanvas').attr("height",textHeight + 10);
        }
});
}

function resizeTree(resizeDir) {
var canvasHeight = parseInt($('svg').attr("height"));
var canvasWidth = parseInt($('svg').attr("width"));
if (resizeDir == "upV") {
    renderTree(dataObject,canvasWidth,canvasHeight + 100);
    /*$('#svgCanvas').attr("height", canvasHeight+100 + Math.round((2*((canvasHeight+100)/100))));
    $('svg').attr("height", canvasHeight+100 + Math.round((2*((canvasHeight+100)/100))));*/
    } else if (resizeDir == "downV") {
    renderTree(dataObject,canvasWidth,canvasHeight - 100);
    /*$('#svgCanvas').attr("height", canvasHeight - 100 + Math.round((2*((canvasHeight - 100)/100))));
    $('svg').attr("height", canvasHeight - 100 + Math.round((2*((canvasHeight - 100)/100)))); */
    } else if (resizeDir == "upH") {
    renderTree(dataObject,canvasWidth + 100, canvasHeight);
    } else if (resizeDir == "downH") {
    renderTree(dataObject,canvasWidth - 100, canvasHeight);
    }
    repairSize();
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