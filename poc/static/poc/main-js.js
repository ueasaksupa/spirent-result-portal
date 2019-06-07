$(document).ready(function () {
	$('#table_template').DataTable({
		orderCellsTop: true,
		fixedHeader: true,
		pageLength: 100,
		dom: '<"float-right export-btn-grp mr-2"B>lfrtip',
		buttons: {
			buttons: [{
					extend: 'excelHtml5',
					text: 'Excel'
				},
				{
					extend: 'pdfHtml5',
					text: 'PDF'
				},
				{
					extend: 'csvHtml5',
					text: 'CSV'
				}
			],
		},
		initComplete: function () {
			$(".dt-buttons").attr('class', 'btn-group');
			$('.dt-button').removeClass('dt-button')
			this.api().columns().every(function () {
				if (this[0][0] != 0) {
					var column = this;
					var select = $('<select><option value=""></option></select>')
						.appendTo($(column.footer()).empty())
						.on('change', function () {
							var val = $.fn.dataTable.util.escapeRegex(
								$(this).val()
							);
							column
								.search(val ? '^' + val + '$' : '', true, false)
								.draw();
						});
					column.data().unique().sort().each(function (d, j) {
						select.append('<option value="' + d + '">' + d + '</option>')
					});
				}
			});
		},
	});

	$('#table_alltestcases').DataTable({
		orderCellsTop: true,
		fixedHeader: true,
		pageLength: 50,
		order: [
			[0, "desc"]
		],
		/* Tell the DataTable that we need server-side processing. */
		serverSide: true,
		processing: true,
		/* Set up the data source */
		ajax: {
			url: "/server_side_endpoint"
		},
	});

	$('#edit_remark_modal').on('show.bs.modal', function (e) {
		//get data attribute of the clicked element
		var text = $(e.relatedTarget).data('text');
		var set = $(e.relatedTarget).data('set');
		//populate the textbox
		$(e.currentTarget).find('input[name="remark"]').val(text);
		$(e.currentTarget).find('input[name="test_set"]').val(set);
	});
	
	$("input[name|='testcase']").change(function(){
		$.ajax({
			url: "auto/form",
			type: "get", //send it through get method
			data: { 
			  testcase: $("input[name|='testcase']").val()
			},
			success: function(response) {
				$("input[name|='description']").val(response['description'])
			},
			error: function(xhr) {
			  //Do Something to handle error
			}
		  });
	});

	$('#table_resultdetail').DataTable({
		orderCellsTop: true,
		fixedHeader: true,
		pageLength: 100,
		autoWidth: true,
		columnDefs: [{
			targets: [6],
			orderData: [6, 4]
		}],
		dom: '<"float-right export-btn-grp mr-2"B>lfrtip',
		buttons: {
			buttons: [{
					extend: 'excelHtml5',
					text: 'Excel',
					className: 'btn btn-sm btn-outline-primary'
				},
				{
					extend: 'pdfHtml5',
					text: 'PDF',
					className: 'btn btn-sm btn-outline-primary'
				},
				{
					extend: 'csvHtml5',
					text: 'CSV',
					className: 'btn btn-sm btn-outline-primary'
				}
			],
		},
		initComplete: function () {
			$(".dt-buttons").attr('class', 'btn-group');
			$('.dt-button').removeClass('dt-button')
			this.api().columns().every(function () {
				if (this[0][0] != 0) {
					var column = this;
					var select = $('<select><option value=""></option></select>')
						.appendTo($(column.footer()).empty())
						.on('change', function () {
							var val = $.fn.dataTable.util.escapeRegex(
								$(this).val()
							);
							column
								.search(val ? '^' + val + '$' : '', true, false)
								.draw();
						});
					column.data().unique().sort().each(function (d, j) {
						select.append('<option value="' + d + '">' + d + '</option>')
					});
				}
			});
		},
		//
	});
});