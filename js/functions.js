function draw_stats(players) {
  mysteries = 0;
  solved = 0;
  letters = 0;
  results_html = '<table style="border-collapse: collapse;" border=1>';
  results_html += '<tr><th>Player</th><th>Scrambles Solved</th><th>Key Letters</th><th>Scramble Sets Solved</th></tr>'
  for (var player in players) {
    results_html += '<tr><td>';
    results_html += players[player].name;
    results_html += '</td><td>';
    results_html += players[player].solved;
    results_html += '</td><td>';
    results_html += players[player].letters;
    results_html += '</td><td>';
    results_html += players[player].mystery;
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
