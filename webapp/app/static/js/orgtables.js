$(document).ready(function() {
    $('#refinfo').DataTable();
} );
var jobid = $('#jobinfo').val();
refInfo = $('#refinfo').DataTable({
    ajax: {
        contentType: 'application/json',
        url: '/results/'+jobid+'/step2/orgs',
        dataSrc: 'reforgs'
    },
    columns: [
        {data: 'orgname'},
        {data: 'strain',
        defaultContent: 'N/A'},
        {data : 'taxid'},
        {data: 'dist',
        render: function(data,type,row,meta){
        return parseFloat(data).toFixed(3);}},
        {data: 'maxorg'},
        {data: 'maxdist',
        visible: false},
        {data: 'mindist',
        visible: false},
        {data : 'genusname'},
        {data: 'genusid',
        visible: false},
        {data: 'familyname'},
        {data: 'familyid',
        visible: false},
        {data: 'ordername'},
        {data: 'orderid',
        visible: false},
        {data: 'phylname'},
        {data: 'phylid',
        visible: false},
        {data: 'id',
        visible: false}
    ],
    order: [[3, 'asc']],
    aLengthMenu: [
        [10, 25, 50, 100, 200, -1],
        [10, 25, 50, 100, 200, "All"]
        ],
        iDisplayLength: 10,
     fnInitComplete: function(oSettings, json) {
      idSearch();
    }

});

function idSearch() {
var idList = "";
$('#specieslist .picked').each(function(){
    idList += ("|"+($(this).attr("id")));
});
console.log(idList);
var searchTerm = idList.slice(1);
refInfo.search(searchTerm, true,false).draw();
}

$('a.toggle-vis').on( 'click', function (e) {
        e.preventDefault();
        // Get the column API object
        var column = refInfo.column( $(this).attr('data-column') );
        // Toggle the visibility
        column.visible( ! column.visible() );
        } );