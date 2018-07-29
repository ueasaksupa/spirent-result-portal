
$(document).ready(function() {
    $('#table_template').DataTable({
        orderCellsTop: true,
        fixedHeader: true,
        pageLength: 100,
    });
    
    $('#table_alltestcases').DataTable({
        orderCellsTop: true,
        fixedHeader: true,
        pageLength: 50,
    });

    $('#edit_remark_modal').on('show.bs.modal', function(e) {
        //get data attribute of the clicked element
        var text = $(e.relatedTarget).data('text');
        var set = $(e.relatedTarget).data('set');
        //populate the textbox
        $(e.currentTarget).find('input[name="remark"]').val(text);
        $(e.currentTarget).find('input[name="test_set"]').val(set);
    });

    $('#table_resultdetail').DataTable( {
        orderCellsTop: true,
        fixedHeader: true,
        pageLength: 100,
        autoWidth: true,
        columnDefs: [ {
            targets: [ 6 ],
            orderData: [ 6, 4 ]
            }
        ],
        initComplete: function () {
            this.api().columns().every( function () {
                if (this[0][0] != 0) {
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
                }
            } );
        },
        //
    } );
} );