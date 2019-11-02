$(document).ready(function() {
  $('#to-trial').on('click', function() {
    if ($('#checked').is(':checked')){
      window.location.href = $('#trial-redirect').val();
    }
    else {
      $('#alert').fadeIn(200);
    }
  });

});
