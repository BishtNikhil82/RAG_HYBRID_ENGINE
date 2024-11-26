hideChat(1);

$('#prime').click(function() {
  toggleFab();
});


//Toggle chat and links
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

      let HTMLstr =` 
                        <span class="chat_msg_item chat_msg_item_user">`+ curchatmsg + `</span>
                        <span class="status">20m ago</span>
      
                         <span id = "loading-icon"  class="chat_msg_item chat_msg_item_admin">
                         <img  src= "./loading.gif" height= "40px" widht ="40px"  />
                         </span>
      `;



      $('#chat_converseid').append(HTMLstr);
      setFocusOnDivWithId(document.getElementById("loading-icon"));

      $('#chatSend').val(``);
      

    const body = {
      query: curchatmsg

    };

    $.ajax({
      url: "http://127.0.0.1:5000/query",
      type: "POST",
      data: JSON.stringify(body), // Convert data to JSON string if needed
      contentType: "application/json; charset=utf-8", // Set Content-Type header
      dataType: "json", // Specify the expected response type
      success: function(response) {
          console.log("Success:", response);
 
          $('#loading-icon').remove();

          HTMLstr = ` 
          
          <span class="chat_msg_item chat_msg_item_admin"><div class="chat_avatar"><img src="avatar_ma6vug.png" /></div>`+ response.response + `</span>`;
          $('#chat_converseid').append(HTMLstr);
      },
      error: function(xhr, status, error) {
          console.error("Error:", error);
      }
  });




 //   $.post("https://echo.free.beeceptor.com/sample-request", body, (data, status) => {
//console.log(data);
//var dt = JSON.parse(data);
//console.log(data.parsedBody.response);


   

//     $('#loading-icon').remove();

//     HTMLstr = ` 
    
//     <span class="chat_msg_item chat_msg_item_admin"><div class="chat_avatar"><img src="avatar_ma6vug.png" /></div>`+ data.parsedBody.response + `   server response of msg ` + curchatmsg + `</span>`;
//     $('#chat_converseid').append(HTMLstr);

//});
     // setFocusOnDivWithId('loading-icon');

    //  $('#loading-icon').scrollTop(10000);
  })


//   $('#chat_first_screen').click(function(e) {
//         hideChat(1); 
//   });

//   $('#chat_second_screen').click(function(e) {
//         hideChat(2);
//   });

//   $('#chat_third_screen').click(function(e) {
//         hideChat(3);
//   });

//   $('#chat_fourth_screen').click(function(e) {
//         hideChat(4);
//   });

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
      //$('#chat_converse').css('display', 'none');
     // $('#chat_body').css('display', 'none');
     // $('#chat_form').css('display', 'none');
     // $('.chat_login').css('display', 'none');
     // $('#chat_fullscreen').css('display', 'block');
  });

function hideChat(hide) {
//     switch (hide) {
//       case 0:
//             $('#chat_converse').css('display', 'none');
//             $('#chat_body').css('display', 'none');
//             $('#chat_form').css('display', 'none');
//             $('.chat_login').css('display', 'block');
//             $('.chat_fullscreen_loader').css('display', 'none');
//              $('#chat_fullscreen').css('display', 'none');
//             break;
//       case 1:
            $('#chat_converse').css('display', 'block');
            // $('#chat_body').css('display', 'none');
            // $('#chat_form').css('display', 'none');
            // $('.chat_login').css('display', 'none');
            $('.chat_fullscreen_loader').css('display', 'block');
            // break;
//       case 2:
//             $('#chat_converse').css('display', 'none');
//             $('#chat_body').css('display', 'block');
//             $('#chat_form').css('display', 'none');
//             $('.chat_login').css('display', 'none');
//             $('.chat_fullscreen_loader').css('display', 'block');
//             break;
//       case 3:
//             $('#chat_converse').css('display', 'none');
//             $('#chat_body').css('display', 'none');
//             $('#chat_form').css('display', 'block');
//             $('.chat_login').css('display', 'none');
//             $('.chat_fullscreen_loader').css('display', 'block');
//             break;
//       case 4:
//             $('#chat_converse').css('display', 'none');
//             $('#chat_body').css('display', 'none');
//             $('#chat_form').css('display', 'none');
//             $('.chat_login').css('display', 'none');
//             $('.chat_fullscreen_loader').css('display', 'block');
//             $('#chat_fullscreen').css('display', 'block');
//             break;
//     }
}
