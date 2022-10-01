function child_data( d ) {
    return '<table cellpadding="5" cellspacing="0" border="0" style="padding-left:50px;">'+
    '<tr>'+
        '<td>Image:</td>'+
        '<td><img src = "'+d[6]+'" width = "200" height = "200"></td>'+
    '</tr>'+
'</table>';
}
$(document).ready(function() {
    var grapheneTable = $('#graphene').DataTable({
        columnDefs: [
            {
                target: 6,
                visible: false,
                searchable: false,
            }
        ],
    });
    var hBNTable = $('#hBN').DataTable({
        columnDefs: [
            {
                target: 6,
                visible: false,
                searchable: false,
            }
        ],
    });

    // Add event listener for opening and closing details
    $('#graphene tbody').on('click', function(){
        var tr = $(this).closest('tr');
        var row = table.row( tr );

        if(row.child.isShown()){
            // This row is already open - close it
            row.child.hide();
            tr.removeClass('shown');
        } else {
            // Open this row
            row.child(child_data(row.data())).show();
            tr.addClass('shown');
        }
    });

    // Handle click on "Expand All" button
    $('button.show-children').click(function(){
        // Enumerate all rows
        var datatable = $("#" + this.value).DataTable();
        datatable.rows({ page: 'current' }).every(function(){
            // If row has details collapsed
            if(!this.child.isShown()){
                // Open this row
                this.child(child_data(this.data())).show();
                $(this.node()).addClass('shown');
            }
        });
    });

    // Handle click on "Collapse All" button
    $('button.hide-children').click(function(){
        // Enumerate all rows
        var datatable = $("#" + this.value).DataTable();
        datatable.rows().every(function(){
        // If row has details expanded
        if(this.child.isShown()){
            // Collapse row details
            this.child.hide();
            $(this.node()).removeClass('shown');
            }
        });
    });

    $('input.filter-used').change(function() {
        var datatable = $("#" + this.value).DataTable();
        datatable.draw()
      });

    $('input.filter-owned').change(function() {
        var tables = $.fn.dataTable.tables();
        tables.forEach(function(element){
            var datatable = $(element).DataTable();
            datatable.draw()
        });
      });

    $.fn.dataTable.ext.search.push(
    function(settings, searchData, index, rowData, counter) {
        // Unchecked, filter out flakes used in devices.
        var found = true;
        $('input.filter-used').each(function(index, elem) {
        if (!elem.checked && elem.value == settings.nTable.id && rowData[4] != "None") {
            found = false;
            }
        });
        // Unchecked, filter out flakes which are not owned by the current user
        $('input.filter-owned').each(function(index, elem) {
            if (!elem.checked && (rowData[7] != elem.value && rowData[7] != null)) {
                found = false;
                }
            });
        return found;
    }
    );
    grapheneTable.draw();
    hBNTable.draw();
});