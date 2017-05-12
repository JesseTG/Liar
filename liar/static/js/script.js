(function ready(fn) {
  window.addEventListener('load', fn);
})(function() {
  let nodes = d3.selectAll('.subject');
  let edges = d3.selectAll('.edge');

  let tip = d3
    .tip()
    .attr('class', 'tooltip')
    .html(function(d, i) {
      return d.dataset.subject;
    });

  let tx = d3.transition()
      .duration(750)
      .ease(d3.easeCircleOut);

  let pie = d3.pie();


  edges
    .on('node-selected', function(d, i) {
      this.style['stroke-width'] = 1;
    })
    .on('node-deselected', function(d, i) {
      this.style['stroke-width'] = 0.05;
    });

  nodes
    .data(nodes.nodes())
    .call(tip)
    .on('node-selected', function(d, i) {
      tip.show(d, i);
      this.style.fill = `url(#${this.dataset.subjectslug})`;
    })
    .on('node-deselected', function(d, i) {
      tip.hide(d, i);
      this.style.fill = this.dataset.defaultfill;
    })
    .on('mouseover', function(d, i) {

      let e = d3.selectAll(`.${d.dataset.subjectslug}`);
      e.each(function(d, i) {
          let func = d3.select(this).on("node-selected");
          func.apply(this, [d, i]);
      });
    })
    .on('mouseout', function(d, i) {

      let e = d3.selectAll(`.${d.dataset.subjectslug}`);
      e.each(function(d, i) {
          let func = d3.select(this).on("node-deselected");
          func.apply(this, [d, i]);
      });
    });
});