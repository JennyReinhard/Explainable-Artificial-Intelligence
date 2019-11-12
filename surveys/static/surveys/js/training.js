$(document).ready(function() {
  var decision;
  var language_code = $('#language-code').val();
  var packageValue = $('#package').data('package');
  var manualLabour = $('#manual').data('manual');
  var result_panel = $('#result').css('display');
  var reliability = $('#reliability').val();
  var dss = $('#dss').val();
  var risk = $('#risk').val();
  var scenario = $('#scenario').val();
  var package_value = $('#package_value').val();
  var attempts = $('#attempts').val();
  var errors = $('#errors').val();
  var success = $('#success').val();
  var suggestion = $('#suggestion').val();
  var best_choice = $('#best_choice').val();
  var result_panel_dispaly = $('#result');
  var url = $('#save-training').val();

  $(function() {
    $('#preload').fadeOut(1000, function() {
      $('.content').fadeIn(500);
    });
  });

  // $('.end-trial').on('click', function() {
  //   decision = $(this).data('decision');
  //   loadResult();
  // });

  $(document).keypress(function(e) {
    //Automate
    if (e.key == 'a') {
      decision = 'automate';
      loadResult();
      setTimeout(save, 300);
    }

    if (e.key == 'm') {
      decision = 'manual';
      loadResult();
      setTimeout(save, 300);

    }

    if (e.keyCode == 32 && result_panel_dispaly.css('display') == 'block') {
      window.location.href = $('#next-training').val();
    }

    // if (e.key == 'i') {
    //   UIkit.offcanvas('#offcanvas-reveal').toggle();
    // }
  });
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

  function save() {
    var profit = $('#result-value').html()
    var injuries = $('#injuries').html()

    var data = {
      'profit': profit,
      'injuries': injuries
    };

    $.post(url, data, function(response) {
      if (response === 'success') {
        console.log('Training successfully completed');
      } else {
        alert('Error! :(');
      }
    });
  };


  function loadResult() {
    $('#decision').fadeOut(200, function() {

      if (language_code == 'en') {
        if (decision == 'manual') {
          $('#result-text').html("You have chosen <strong>manual</strong>! You have made a profit of " + manualLabour + " $ No one has been injured.");
          $('#result-value').html(manualLabour);
          $('#injuries').html("0");
        }
        if (decision == 'automate') {
          if (success == 'True') {
            $('#result-text').html("You have chosen to <strong>automate</strong>! Everything went well and you have made a profit of <span class='uk-text-success'>+" + packageValue + " $</span>. No one has been injured! Yipie!");
            $('#result-value').html(packageValue);
            $('#result-value').addClass('uk-text-success');
            $('#injuries').html("0");
            $('#injuries').addClass('uk-text-success');
          }
          if (success == 'False') {
            if (risk == 'property_and_personal_risk') {
              $('#result-text').html("You have chosen to <strong>automate</strong>! Something went really wrong and you have made a loss of <span class='uk-text-danger'>-" + packageValue + " $</span>. One person got badly <span class='uk-text-danger'>injured</span>. Yayks.");
              $('#result-value').html("0");
              $('#result-value').addClass('uk-text-danger');
              $('#injuries').html("1");
              $('#injuries').addClass('uk-text-danger');
            } else if (risk == 'property_risk') {
              $('#result-text').html("You have chosen to <strong>automate</strong>! Something went really wrong and you have made a loss of <span class='uk-text-danger'>-" + packageValue + " $</span>. Yayks.");
              $('#result-value').html("0");
              $('#result-value').addClass('uk-text-danger');
              $('#injuries').html("0");
            } else if (risk == 'personal_risk') {
              $('#result-text').html("You have chosen to <strong>automate</strong>! Something went really wrong and one person got badly <span class='uk-text-danger'>injured</span>. Yayks.");
              $('#result-value').html("0");
              $('#result-value').addClass('uk-text-danger');
              $('#injuries').html("1");

            } else {
              $('#result-text').html("You have chosen to <strong>automate</strong>! There was however a problem with the vehicle and you made a loss of <span class='uk-text-success'>+" + packageValue + " $</span>. No one has been injured! Yipie!");
              $('#result-value').html("0");
              $('#result-value').addClass('uk-text-dager');
              $('#injuries').html("0");
              $('#injuries').addClass('uk-text-success');
            }
          }
        }
      }
      else if (language_code == 'de') {
        if (decision == 'manual') {
          $('#result-text').html("Sie haben sich für <strong>Manuell</strong> entschieden! Sie haben ein Gewinn von " + manualLabour + " € gemacht.");
          $('#result-value').html(manualLabour);
          $('#injuries').html("0");
        }
        if (decision == 'automate') {
          if (success == 'True') {
            $('#result-text').html("Sie haben sich für <strong>Automatisieren</strong> entschieden! Alles ist gut verlaufen und Sie haben einen Gewinn von <span class='uk-text-success'>+" + packageValue + "</span> € gemacht.");
            $('#result-value').html(packageValue);
            $('#result-value').addClass('uk-text-success');
            $('#injuries').html("0");
            $('#injuries').addClass('uk-text-success');
          }
          if (success == 'False') {
            if (risk == 'property_and_personal_risk') {
              $('#result-text').html("Sie haben sich für <strong>Automatisieren</strong> entschieden! Leider gab es einen Unfall und Sie haben einen Verlust von <span class='uk-text-danger'>-" + packageValue + "</span> € gemacht. Eine Person wurde schwer <span class='uk-text-danger'>verletzt</span>!");
              $('#result-value').html("0");
              $('#result-value').addClass('uk-text-danger');
              $('#injuries').html("1");
              $('#injuries').addClass('uk-text-danger');
            } else if (risk == 'property_risk') {
              $('#result-text').html("Sie haben sich für <strong>Automatisieren</strong> entschieden! Leider gab es einen Unfall und Sie haben einen Verlust von <span class='uk-text-danger'>-" + packageValue + "</span> € gemacht!");
              $('#result-value').html("0");
              $('#result-value').addClass('uk-text-danger');
              $('#injuries').html("0");
            } else if (risk == 'personal_risk') {
              $('#result-text').html("Sie haben sich für <strong>Automatisieren</strong> entschieden! Leider gab es einen Unfall und eine Person wurde schwer <span class='uk-text-danger'>verletzt</span>!");
              $('#result-value').html("0");
              $('#result-value').addClass('uk-text-danger');
              $('#injuries').html("1");
              $('#injuries').addClass('uk-text-danger');
            } else {
              $('#result-text').html("Sie haben sich für <strong>Automatisieren</strong> entschieden! Es gab ein Problem mit dem Fahrzeug. Sie haben <span class='uk-text-danger'>" + packageValue + " $</span> verloren!");
              $('#result-value').html("0");
              $('#result-value').addClass('uk-text-danger');
              $('#injuries').html("0");
            }
          }
        }
      }
      $('#result').fadeIn(200);
    });
  }
});
