// function to update standings table
function update_standings(comp) {
    $.ajax({
        url: "/update_standings",
        data: {'comp' : comp},
        dataType: "json",
        type: 'POST',
        success: function(data) {
            var standings = data['data'];
            // remove and reset table
            d3.select('#pointsTable').remove();
            // do the thing to make the table
            var columns = ['team', 'pts', 'gp', 'gs', 'ga', 'gd', 'lead_time_p90', 'trail_time_p90'];
			var headings = {'team': 'Team', 'pts': 'Points', 'gp': 'GP', 'gs': 'GS', 'ga': 'GA', 'gd': 'GD', 'lead_time_p90': 'LTp90', 'trail_time_p90': 'TTp90'}
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
                .text(function (column) { return headings[column]; });

            // create a row for each object in the data
            var rows = tbody.selectAll('tr')
                .data(standings)
                .enter()
                .append('tr')
				.attr('id', function(d) { return d['team']; })
				.attr('class', 'team');

            // create a cell in each row for each column
            // except for team names
            var cells = rows.selectAll('td')
                .data(function (row) {
                    return columns.map(function (column) {
                        return {column: column, value: row[column]};
                    });
                })
                .enter()
                .append('td')
                .text(function (d) { return d.column == 'team' ? "" : d.value; });

            // add team names and link to these team names
            cells.filter(function(d, i) { return d.column == 'team' })
                .append('a')
                .attr('href', function(d) { return '/' + d.value.split(' ').join('_') + '/' + comp; })
                .html(function(d) { return d.value });

			d3.select("#heading").select("th")
				.text("English Premier League " + comp)
				.attr("style", "font-weight: 300; padding-bottom: 3vh;")

			d3.selectAll(".team")
				.style("background-color", function(d, i) { return i % 2 == 0? "#f0f0f0" : "#fff";});

            // format_standings();
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
