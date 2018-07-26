$(document).ready(function() {
    $(".clickable-row").click(function() {
        window.location = $(this).data("href");
    });
    $('#table_template').DataTable({
        orderCellsTop: true,
        fixedHeader: true,
        pageLength: 200,
    });
    $('#table_alltestcases').DataTable({
        orderCellsTop: true,
        fixedHeader: true,
        pageLength: 40,
    });
    $('#table_resultdetail').DataTable( {
        orderCellsTop: true,
        fixedHeader: true,
        pageLength: 210,
        columnDefs: [ {
            targets: [ 6 ],
            orderData: [ 6, 4 ]
        }],
        //
        initComplete: function () {
            this.api().columns().every( function () {
                var column = this;
                var select = $('<select><option value=""></option></select>')
                    .appendTo( $(column.footer()).empty() )
                    .on( 'change', function () {
                        var val = $.fn.dataTable.util.escapeRegex(
                            $(this).val()
                        );
 
                        column
                            .search( val ? '^'+val+'$' : '', true, false )
                            .draw();
                    } );
 
                column.data().unique().sort().each( function ( d, j ) {
                    select.append( '<option value="'+d+'">'+d+'</option>' )
                } );
            } );
        },
        //
    } );
} );