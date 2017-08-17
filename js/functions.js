function draw_stats(players) {
  console.log(players);
  mysteries = 0;
  solved = 0;
  letters = 0;
  results_html = '<table style="border-collapse: collapse;" border=1>';
  //results_html += '<tr><th>Player</th><th>Workstation Number</th><th>Scrambles Solved</th><th>Key Letters</th><th>Scramble Sets Solved</th></tr>'
  results_html += '<tr><th>Player</th><th>Scrambles Solved</th><th>Key Letters</th><th>Scramble Sets Solved</th><th>Closed Puzzle Solver</th><th>Pay Type</th></tr>'
  for (var player in players) {
    results_html += '<tr><td>';
    results_html += players[player].name;
    results_html += '</td><td>';
    results_html += players[player].solved + players[player].mystery;
    results_html += '</td><td>';
    results_html += players[player].letters;
    results_html += '</td><td>';
    results_html += players[player].sets;
    results_html += '</td><td>';
    results_html += players[player].is_mystery ? 'yes' : 'no';
    results_html += '</td><td>';
    results_html += players[player].pay_type;
    results_html += '</td></tr>';

    mysteries += players[player].mystery;
    solved += players[player].solved;
    letters += players[player].letters;
  }
  /*
  results_html += '<tr style="border-top-style:solid;"><td>Total</td><td>';
  results_html += mysteries;
  results_html += '</td><td>';
  results_html += solved;
  results_html += '</td><td>';
  results_html += letters;
  results_html += '</td></tr>';
  */
  results_html += '</table>';
  return results_html;
}
