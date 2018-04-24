
(function ($) {
	"use strict";

	$.getJSON("/channels", function(channels) {
		console.log("in here?");
		var tableBody = document.getElementById("table_body");
		if (Array.isArray(channels)) {
			console.log("isArray");
			var str = ""
			if (channels.length > 0) {
				channels.forEach(function(channel) {
					console.log(channel);
					var row = tableBody.insertRow(tableBody.rows.length-1);
					row.setAttribute("class", "row100");

					var cellOne = row.insertCell(0);
					cellOne.setAttribute("class", "column100 column1");
					cellOne.setAttribute("data-column", "column1");
					var button = document.createElement("BUTTON");
					button.innerHTML = channel;
					cellOne.appendChild(button);

					var cellTwo = row.insertCell(1);
					cellOne.setAttribute("class", "column100 column2");
					cellOne.setAttribute("data-column", "column2");
					cellTwo.innerHTML = "CHANNEL TOPIC HERE";

					console.log(row);
					//str = str.concat("<tr class=\"row100\">\n<td class=\"column100 column1\" data-column=\"column1\">");
					//str = str.concat(channel);
					//str = str.concat("</td>\n<td class=\"column100 column2\" data-column=\"column2\">Channel topic [FILL OUT]</td></tr>");
				});
			}
		}
	});


	$('.column100').on('mouseover',function(){
		var table1 = $(this).parent().parent().parent();
		var table2 = $(this).parent().parent();
		var verTable = $(table1).data('vertable')+"";
		var column = $(this).data('column') + ""; 

		$(table2).find("."+column).addClass('hov-column-'+ verTable);
		$(table1).find(".row100.head ."+column).addClass('hov-column-head-'+ verTable);
	});

	$('.column100').on('mouseout',function(){
		var table1 = $(this).parent().parent().parent();
		var table2 = $(this).parent().parent();
		var verTable = $(table1).data('vertable')+"";
		var column = $(this).data('column') + ""; 

		$(table2).find("."+column).removeClass('hov-column-'+ verTable);
		$(table1).find(".row100.head ."+column).removeClass('hov-column-head-'+ verTable);
	});

	    /*==================================================================
	    [ Validate ]*/
	    var input = $('.validate-input .input100');

	    $('.validate-form').on('submit',function(){
	    	var check = true;

	    	for(var i=0; i<input.length; i++) {
	    		if(validate(input[i]) == false){
	    			showValidate(input[i]);
	    			check=false;
	    		}
	    	}

	    	return check;
	    });


	    $('.validate-form .input100').each(function(){
	    	$(this).focus(function(){
	    		hideValidate(this);
	    	});
	    });

	    function validate (input) {
	    	if($(input).attr('type') == 'email' || $(input).attr('name') == 'email') {
	    		if($(input).val().trim().match(/^([a-zA-Z0-9_\-\.]+)@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.)|(([a-zA-Z0-9\-]+\.)+))([a-zA-Z]{1,5}|[0-9]{1,3})(\]?)$/) == null) {
	    			return false;
	    		}
	    	}
	    	else {
	    		if($(input).val().trim() == ''){
	    			return false;
	    		}
	    	}
	    }

	    function showValidate(input) {
	    	var thisAlert = $(input).parent();

	    	$(thisAlert).addClass('alert-validate');
	    }

	    function hideValidate(input) {
	    	var thisAlert = $(input).parent();

	    	$(thisAlert).removeClass('alert-validate');
	    }


	})(jQuery);

	function closeModal(){
		var modal = document.getElementById('myModal');
		modal.style.display = "none";
	};

	document.getElementById('myModal').style.display = "none";
	var modal = document.getElementById('myModal');
	var span = document.getElementsByClassName("close")[0];
	var btn = document.getElementById("add_chan_btn");

	btn.onclick = function() {
		modal.style.display = "block";
	}
	span.onclick = function() {
		modal.style.display = "none";
	}
	window.onclick = function(event) {
		if (event.target == modal) {
			modal.style.display = "none";
		}
	}
