(function () {
    var channel_name = document.getElementById("channel_name").textContent;
    var Message;

    $.getJSON("/get_list/" + channel_name, function(members_and_files) {
        var fileList = document.getElementById("file_list");
        var memberList = document.getElementsById("member_list");
        var members = members_and_files[0];
        var files = members_and_files[1];
        if (Array.isArray(members)) {
            if (members.length > 0) {
                members.forEach(function(member) {
                    var member = document.createElement("P");
                    member.innerHTML = member;
                    memberList.appendChild(member);
                });
            }
        }
        if (Array.isArray(files)) {
            if (files.length > 0) {
                files.forEach(function(file) {
                    var iconDiv = document.createElement("DIV");
                    iconDiv.setAttribute("id", "icons");
                    var downloadButton = document.createElement("IMG");
                    downloadButton.setAttribute("src", "../static/channel/images/ic_insert_drive_file_black_48dp/web/ic_insert_drive_file_black_48dp_1x.png");
                    //downloadButton.setAttribute("onclick", "downloadFile(file)");
                    downloadButton.onclick = downloadFile(file);
                    var deleteButton = document.createElement("IMG");
                    deleteButton.setAttribute("src", "../static/channel/images/ic_delete_white_18dp/web/ic_delete_white_18dp_1x.png");
                    //deleteButton.setAttribute("onclick", "deleteFile(file)");
                    deleteButton.onclick = deleteFile(file);
                    var filename = document.createElement("P");
                    filename.innerHTML = file;
                    iconDiv.appendChild(downloadButton);
                    iconDiv.appendChild(deleteButton);
                    iconDiv.appendChild(filename);
                    fileList.appendChild(iconDiv);
                });
            }
        }
    });    

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
        update();
        //setInterval(update, 200);
        
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
    [ Validate 2]*/
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
};

addAdminBtn.onclick = function() {
    adminModal.style.display = "block";
};
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

function downloadFile(filepath){
    var channel_name = document.getElementById("channel_name").textContent;
    var link = document.createElement("A");
    link.download = filepath;
    link.href = '/download_file/' + channel_name + '/' + filepath;
    link.click();
};

function deleteFile(filepath){
    var channel_name = document.getElementById("channel_name").textContent;
    $.ajax
            ({
                type: "POST",
                url: '/delete_file/' + channel_name + '/' + filepath,
            });
};