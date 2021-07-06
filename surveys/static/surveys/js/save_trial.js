$(document).ready(function () {

  var language_code = $('#language-code').val();
  var trial_id = $('#trial-id').val();
  var url = '/' + language_code + '/surveys/trial/save/' + trial_id + '/';
  var result_panel = $('#result').css('display');
  var sessionkey = $('#sessionkey').val();
  var blockcounter = $('#blockcounter').val();
  var context = $('#context').val();
  var ai_method = $('#ai_method').val();
  var explanation_approach = $('#explanation_approach').val();

  //Preloader
  $(function() {
    $('#preload').fadeOut(1000, function() {
      $('.content').fadeIn(500);
    });
  });

  $(document).keypress(function (e) {
  });


  //Ajax setup
  function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      var cookies = document.cookie.split(';');
      for (var i = 0; i < cookies.length; i++) {
        var cookie = jQuery.trim(cookies[i]);
        // Does this cookie string begin with the name we want?
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  var csrftoken = getCookie('csrftoken');

  function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
  }

  $.ajaxSetup({
    beforeSend: function(xhr, settings) {
      if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
        xhr.setRequestHeader("X-CSRFToken", csrftoken);
      }
    }
  });



  //Saves trial to database
  function save() {
    var data = {
        'blockcounter': blockcounter,
        'sessionkey': sessionkey,
        'ai_method': ai_method,
        'context': context,
        'explanation_approach': explanation_approach,
    };

      $.post(url, data, function(response) {
      if (response === 'success') {
        console.log('Trial data sucessfully posted.');
      } else {
        alert('Error! :(');
      }
    });
  };

  //loads trial result
  function loadResult() {
    $('#decision').fadeOut(200, function() {
      //insert your code here for the results panel
      $('#result').fadeIn(10);
    });
  }

});