
$(document).ready(function() {
  var survey_id = $('#survey_id').val();
  var redirect_url = $('#redirect_url').val();
  var url = '/surveys/' + survey_id + '/load/';
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

  $.ajax({
    'type': 'GET',
    'url': url,
    'dataType': 'json',
    'async': true,
    'success': function(json) {
      $('.preload').fadeOut(500, function(){

        $('.content').fadeIn(500);
        if(redirect_url != 'None'){
          $("#start-trial").attr("href", redirect_url+"?sessionkey="+json.session_key);
        }
        else{
          $("#start-trial").attr("href", "/surveys/"+survey_id+"/"+json.session_key+"/ready/");
        }

      });
    }
  });
});
