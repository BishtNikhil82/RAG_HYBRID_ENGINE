hideChat(1);

$('#prime').click(function() {
  toggleFab();
});

// Toggle chat and links
function toggleFab() {
  $('.prime').toggleClass('zmdi-comment-outline');
  $('.prime').toggleClass('zmdi-close');
  $('.prime').toggleClass('is-active');
  $('.prime').toggleClass('is-visible');
  $('#prime').toggleClass('is-float');
  $('.chat').toggleClass('is-visible');
  $('.fab').toggleClass('is-visible');
}

$('#chatSend').keypress(function (e) {
  var key = e.which;
  if(key == 13)  // the enter key code
   {
     $('.zmdi-mail-send').click();
     return false;  
   }
});   

function setFocusOnDivWithId(elementId) {   
  const scrollIntoViewOptions = { behavior: "smooth", block: "center" }; 
  elementId.scrollIntoView(scrollIntoViewOptions);
}; 

$('.zmdi-mail-send').click(function(e){
  var curchatmsg = $('#chatSend').val();

  let HTMLstr = `
    <span class="chat_msg_item chat_msg_item_user">` + curchatmsg + `</span>
    <span class="status">20m ago</span>
    <span id="loading-icon" class="chat_msg_item chat_msg_item_admin">
      <img src="./loading.gif" height="40px" width="40px" />
    </span>
  `;

  $('#chat_converseid').append(HTMLstr);
  setFocusOnDivWithId(document.getElementById("loading-icon"));
  $('#chatSend').val(``);

  const body = {
    query: curchatmsg,
    client_id: "client2" // Ensure the clientID is set here
  };

  $.ajax({
    url: "http://127.0.0.1:5000/query",  // Your server URL
    type: "POST",
    data: JSON.stringify(body),  // Sending the updated body with clientID and query
    contentType: "application/json; charset=utf-8",  // Set Content-Type header
    dataType: "json",  // Specify the expected response type
    success: function(response) {
      console.log("Success:", response);

      $('#loading-icon').remove();

      HTMLstr = `
        <span class="chat_msg_item chat_msg_item_admin">
          <div class="chat_avatar"><img src="avatar_ma6vug.png" /></div>` + response.response + `</span>`;
      $('#chat_converseid').append(HTMLstr);
    },
    error: function(xhr, status, error) {
      console.error("Error:", error);
    }
  });
});

$('#chat_fullscreen_loader').click(function(e) {
  $('.fullscreen').toggleClass('zmdi-window-maximize');
  $('.fullscreen').toggleClass('zmdi-window-restore');
  $('.chat').toggleClass('chat_fullscreen');
  $('.fab').toggleClass('is-hide');
  $('.header_img').toggleClass('change_img');
  $('.img_container').toggleClass('change_img');
  $('.chat_header').toggleClass('chat_header2');
  $('.fab_field').toggleClass('fab_field2');
  $('.chat_converse').toggleClass('chat_converse2');
});

function hideChat(hide) {
  $('#chat_converse').css('display', 'block');
  $('.chat_fullscreen_loader').css('display', 'block');
}
