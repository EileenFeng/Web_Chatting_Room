(function () {
    function banUser(user, channel_name, banned_user){

    }
    var channel_name = document.getElementById("channel_name").textContent;
    var Message;
    Message = function (arg) {
        this.text = arg.text, this.message_side = arg.message_side;
        this.draw = function (_this) {
            return function () {
                var $message;
                $message = $($('.message_template').clone().html());
                $message.addClass(_this.message_side).find('.text').html(_this.text);
                $('.messages').append($message);
                return setTimeout(function () {
                    return $message.addClass('appeared');
                }, 0);
            };
        }(this);
        return this;
    };
    $(function () {
        var getMessageText, message_side, putMessage, sendMessage;
        message_side = 'right';
        getMessageText = function () {
            var $message_input;
            $message_input = $('.message_input');
            return $message_input.val();
        };
        putMessage = function (text) {
            var $messages, message;
            if (text.trim() === '') {
                return;
            }
            $('.message_input').val('');
            $messages = $('.messages');
            message_side = 'left';
            message = new Message({
                text: text,
                message_side: message_side
            });
            message.draw();
            return $messages.animate({ scrollTop: $messages.prop('scrollHeight') }, 300);
        };
        // Track all of the chats we've seen -- Don't strictly need
        // this / use it right now
        var messages = [];
        // Keeps track of the last element we've seen
        var getChatsFrom = 0;

        update = function() {
            $.getJSON("/chats/" + channel_name, function(chats) {
                if (Array.isArray(chats)) {
                    messages.push(chats);
                    if (chats.length > 0) {
                        chats.forEach(function(chat) {
                            putMessage(chat);
                        });
                    }
                }
            });
        };

        // Update the chats every 200 milliseconds
        setInterval(update, 200);
        //update();
        
        var sendMessage = function (text) {
            $.ajax
            ({
                type: "POST",
                //the url where you want to sent the userName and password to
                url: '/chat',
                dataType: 'json',
                contentType: 'application/json',
                data: '{"uid": "' + $('#uid').val() + '", "content" : "' + text + '"}',
            });
        };

        $('.send_message').click(function (e) {
            return sendMessage(getMessageText());
        });
        
        $('.message_input').keyup(function (e) {
            if (e.which === 13) {
                return sendMessage(getMessageText());
            }
        });
    });

    /*==================================================================
    [ Validate 1]*/
    var input1 = $('.validate-input-1 .input100');

    $('.validate-form-1').on('submit',function(){
        var check = true;

        for(var i=0; i<input1.length; i++) {
            if(validate(input1[i]) == false){
                showValidate(input1[i]);
                check=false;
            }
        }

        return check;
    });


    $('.validate-form-1 .input100').each(function(){
        $(this).focus(function(){
            hideValidate(this);
        });
    });


    /*==================================================================
    [ Validate ]*/

    var input2 = $('.validate-input-2 .input100');

    $('.validate-form-2').on('submit',function(){
        var check = true;

        for(var i=0; i<input2.length; i++) {
            if(validate(input2[i]) == false){
                showValidate(input2[i]);
                check=false;
            }
        }

        return check;
    });


    $('.validate-form-2 .input100').each(function(){
        $(this).focus(function(){
            hideValidate(this);
        });
    });

    /*================================================================== */

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

}.call(this));

function closeBanModal(){
    var banModal = document.getElementById('ban_modal');
    banModal.style.display = "none";
};

function closeAdminModal(){
    var adminModal = document.getElementById('admin_modal');
    adminModal.style.display = "none";
};

document.getElementById('ban_modal').style.display = "none";
document.getElementById('admin_modal').style.display = "none";

var banModal = document.getElementById('ban_modal');
var adminModal = document.getElementById('admin_modal');
var span = document.getElementsByClassName("close")[0];
var banUserBtn = document.getElementById("ban_user_btn");
var addAdminBtn = document.getElementById("add_admin_btn");

banUserBtn.onclick = function() {
    banModal.style.display = "block";
}

addAdminBtn.onclick = function() {
    adminModal.style.display = "block";
}
/*
span.onclick = function() {
    modal.style.display = "none";
}

window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
}
*/


function myFunction(){
    var x = document.getElementById("myFile");
    var txt = "";
    if ('files' in x) {
        if (x.files.length == 0) {
            txt = "Select one or more files.";
        } else {
            for (var i = 0; i < x.files.length; i++) {
                txt += "<br><strong>" + (i+1) + ". file</strong><br>";
                var file = x.files[i];
                if ('name' in file) {
                    txt += "name: " + file.name + "<br>";
                }
                if ('size' in file) {
                    txt += "size: " + file.size + " bytes <br>";
                }
            }
        }
    } 
    else {
        if (x.value == "") {
            txt += "Select one or more files.";
        } else {
            txt += "The files property is not supported by your browser!";
            txt  += "<br>The path of the selected file: " + x.value; // If the browser does not support the files property, it will return the path of the selected file instead. 
        }
    }
    document.getElementById("demo").innerHTML = txt;
}
