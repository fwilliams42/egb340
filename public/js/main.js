// Chart
const ctx = document.getElementById('myChart').getContext('2d');
let myChart;

$.getJSON('../json/chart.json', loadChart);

function loadChart(chart) {
    myChart = new Chart(ctx, chart);
}

// Table
$.getJSON('../json/table.json', loadTable);

function loadTable(myTable) {
    
    let str = "<tr>";

    for (let i = 0; i < myTable.headings.length; i++) {
        str += `<th scope="col">${myTable.headings[i]}</th>`;
    }

    str += "</tr>";

    document.querySelector('#my-table-head').innerHTML = str;

    str = "";

    for (let i = 0; i < myTable.data.length; i++) {
        str += "<tr>";

        for (let [key, value] of Object.entries(myTable.data[i])) {
            // console.log(value);
            if (key == "id") {
                str += `<th scope="row">${value}</th>`;
            } else {
                str += `<td>${value}</td>`;
            }
        }

        str += "</tr>"
    }
    
    document.querySelector('#my-table-body').innerHTML = str;
}

// Buttons
const forceSyncBtn = document.querySelector('#force-sync');

forceSyncBtn.addEventListener('click', (e) => {

    console.log('Force Sync was clicked.');

    $.getJSON('/json/chart.json', loadChart);

    $.getJSON('/json/table.json', loadTable);
});

const toggleLedsBtn = document.querySelector('#toggle-leds');

toggleLedsBtn.addEventListener('click', (e) => {
    console.log('Toggled LEDs was clicked.');

    fetch('/api/toggleLEDs', {method: 'POST'})
    .then(function(res) {
      if(res.ok) {
        console.log('Click was recorded');
        return;
      }
      throw new Error('Request failed.');
    })
    .catch(function(error) {
      console.log(error);
    });
});

const shutDownBtn = document.querySelector('#reboot');

shutDownBtn.addEventListener('click', (e) => {
    console.log('Shut Down was clicked.');

    fetch('/api/reboot', {method: 'POST'})
    .then(function(res) {
      if(res.ok) {
        console.log('Click was recorded');
        return;
      }
      throw new Error('Request failed.');
    })
    .catch(function(error) {
      console.log(error);
    });
});

const updateLCD = document.querySelector('#update-lcd');

updateLCD.addEventListener('click', (e) => {
    console.log('Update LCD was clicked.');

    fetch('/api/updateLCD', {method: 'POST'})
    .then(function(res) {
      if(res.ok) {
        console.log('Click was recorded');
        return;
      }
      throw new Error('Request failed.');
    })
    .catch(function(error) {
      console.log(error);
    });
});