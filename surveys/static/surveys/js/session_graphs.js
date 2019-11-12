$(document).ready(function() {

  var endpoint = $('#api-call-trialtimes').val();
  var trialTimes = [];
  var feedbackTimes = [];
  var trialNames = [];

  $.ajax({
    method: "GET",
    url: endpoint,
    success: function(data) {
      trialTimes = data.trialDuration;
      trialNames = data.trials;
      feedbackTimes = data.feedbackDuration;

      var ctx = document.getElementById('trialtimes').getContext('2d');
      var config = {
        type: 'line',
        data: {
          labels: trialNames,
          datasets: [{
            label: 'Feedback time',
            fill: false,
            borderColor: '#995D81',
            backgroundColor: '#995D81',
            data: feedbackTimes

          }, {
            label: 'Trial duration ',
            fill: false,
            borderColor: "#EB8258",
            backgroundColor: '#EB8258',
            data: trialTimes

          }]
        },
        options: {
          title: {
            display: true,
            text: 'Feedback times and trial duration'
          },
        }
      };

      var myChart = new Chart(ctx, config);

    },
    error: function(error) {
      console.log(error)
    }
  });
});
