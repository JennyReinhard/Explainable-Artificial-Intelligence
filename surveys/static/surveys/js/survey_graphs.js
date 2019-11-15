$(document).ready(function() {

  var endpoint = $('#api-call-survey').val();
  //Ajax call to api to get graph data
  $.ajax({
    method: "GET",
    url: endpoint,
    success: function(data) {
      var scenario_comparison = data.scenario_comparison;
      new Chart(document.getElementById("scenario_comparison"), {
        type: 'bar',
        data: {
          labels: ['Medical', 'Urban', 'Warehouse'],
          datasets: [{
            label: "Time in ms",
            backgroundColor: ["#995D81", '#EB8258', '#83B692'],
            data: scenario_comparison

          }]
        },
        options: {
          legend: {
            display: false
          },
          title: {
            display: true,
            text: 'Comparison of Scenarios'
          },
        }
      });
    },
    error: function(error) {
      console.log(error)
    }
  });
});
