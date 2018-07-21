// function to update standings table
function update_standings(comp) {
    $.ajax({
        url: "/update_standings",
        data: {'comp' : comp},
        dataType: "json",
        type: 'POST',
        success: function(data) {
            var standings = data['data'];
            d3.select('#pointsTable').remove();
            // do the thing to make the table
            var columns = ['team', 'pts', 'gp', 'gs', 'ga', 'gd', 'lead_time_p90', 'trail_time_p90'];
            var table = d3.select('.standings')
                .append('table')
                .attr('id', 'pointsTable');
            var thead = table.append('thead');
            var	tbody = table.append('tbody');

            // append the header row
            thead.append('tr')
                .selectAll('th')
                .data(columns).enter()
                .append('th')
                .text(function (column) { return column; });

            // create a row for each object in the data
            var rows = tbody.selectAll('tr')
                .data(standings)
                .enter()
                .append('tr');

            // create a cell in each row for each column
            var cells = rows.selectAll('td')
                .data(function (row) {
                    return columns.map(function (column) {
                        return {column: column, value: row[column]};
                    });
                })
                .enter()
                .append('td')
                .text(function (d) { return d.value; });
        }
    });
};

// check if table needs to be initialized
var points_table = document.getElementById('pointsTable').getElementsByClassName('tr');
if (points_table.length == 0) {
    var latest = document.getElementsByClassName('season')[0].id;
    update_standings(latest);
}

// listen for clicks on seasons
$(document).on("click", ".season", function() {
    var comp = $(this).attr('id');
    update_standings(comp);
});
