(function ready(fn) {
  window.addEventListener('load', fn);
})(function() {
  let nodes = d3.selectAll('.subject');
  let tip = d3
    .tip()
    .attr('class', 'tooltip')
    .html(function(d, i) {
      let node = nodes.nodes()[i];
      return `<b>${node.dataset.subject}</b>`;
    });

  let tx = d3.transition()
      .duration(750)
      .ease(d3.easeCircleOut);

  let pie = d3.pie();

  nodes
    .call(tip)
    .on('mouseover', function(d, i) {
      let node = nodes.nodes()[i];
      tip.show(d, i);
      node.style.fill = `url(#${node.dataset.subjectslug})`;
    })
    .on('mouseout', function(d, i) {
      let node = nodes.nodes()[i];
      tip.hide(d, i);
      node.style.fill = node.dataset.defaultfill;
    })
    .transition(tx)
      .attr("cx", function() { return this.dataset.targetx; })
      .attr("cy", function() { return this.dataset.targety; })
      .attr("opacity", 1);


});