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

	$('#table_alltestcases, #result-report').DataTable({
		orderCellsTop: true,
		fixedHeader: true,
		pageLength: 50,
		order: [
			[0, "desc"]
		],
		/* Tell the DataTable that we need server-side processing. */
		// serverSide: true,
		// processing: true,
		/* Set up the data source */
		// ajax: {
		// 	url: "/server_side_endpoint"
		// },
	});

	$('#table_summary').DataTable({
		orderCellsTop: true,
		fixedHeader: true,
		pageLength: 100,
		autoWidth: true,
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
				// if (this[0][0] != 0) {
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
				// }
			});
		},
		//
	});

	$('#edit_remark_modal').on('show.bs.modal', function (e) {
		//get data attribute of the clicked element
		var text = $(e.relatedTarget).data('text');
		var set = $(e.relatedTarget).data('set');
		//populate the textbox
		$(e.currentTarget).find('input[name="remark"]').val(text);
		$(e.currentTarget).find('input[name="test_no"]').val(set);
	});

	$("input[type=number]").bind('keyup input', function(){
		$.ajax({
			url: "ajax/form",
			type: "get",
			data: { 
			  testno: $("input[name|='testno']").val()
			},
			success: function(response) {
				$('.selDiv option:contains("'+response['description']+'")').prop('selected', true)
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
			orderData: [6, 0]
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