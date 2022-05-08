(async () => {
  const resp = await fetch(
      "/src/data.json",
  );
  const data = await resp.json();
  const dag = d3.dagStratify()(data);
  const nodeRadius = 20;
  const layout = d3
      .sugiyama() // base layout
      //.decross(d3.decrossOpt()) // minimize number of crossings
      .nodeSize((node) => [(node ? 3.6 : 0.25) * nodeRadius, 3 * nodeRadius]); // set node size instead of constraining to fit
  const {width, height} = layout(dag);

  const svgSelection = d3.select("svg");
  svgSelection.attr("width", 600);
  svgSelection.attr("height", 600);
  svgSelection.attr("viewBox", [0, 0, width, height].join(" "));
  const defs = svgSelection.append("defs"); // For gradients

  /*const steps = dag.size();
  const interp = d3.interpolateRainbow;
  const colorMap = new Map();
  for (const [i, node] of dag.idescendants().entries()) {
    colorMap.set(node.data.id, interp(i / steps));
  }*/

  // How to draw edges
  const line = d3
    .line()
    .curve(d3.curveCatmullRom)
    .x((d) => d.x)
    .y((d) => d.y);

  // Plot edges
  svgSelection
    .append("g")
    .selectAll("path")
    .data(dag.links())
    .enter()
    .append("path")
    .attr("d", ({ points }) => line(points))
    .attr("fill", "none")
    .attr("stroke", "white");
    /*.attr("d", ({ points }) => line(points))
    .attr("fill", "none")
    .attr("stroke-width", 3)
    .attr("stroke", ({ source, target }) => {
      // encodeURIComponents for spaces, hope id doesn't have a `--` in it
      const gradId = encodeURIComponent(`${source.data.id}--${target.data.id}`);
      const grad = defs
        .append("linearGradient")
        .attr("id", gradId)
        .attr("gradientUnits", "userSpaceOnUse")
        .attr("x1", source.x)
        .attr("x2", target.x)
        .attr("y1", source.y)
        .attr("y2", target.y);
      grad
        .append("stop")
        .attr("offset", "0%")
        .attr("stop-color", colorMap.get(source.data.id));
      grad
        .append("stop")
        .attr("offset", "100%")
        .attr("stop-color", colorMap.get(target.data.id));
      return `url(#${gradId})`;
    });*/

  // Select nodes
  const nodes = svgSelection
    .append("g")
    .selectAll("g")
    .data(dag.descendants())
    .enter()
    .append("g")
    .attr("transform", ({ x, y }) => `translate(${x}, ${y})`);

  // Plot node circles
  nodes
    .append("circle")
    .attr("r", nodeRadius)
    /*.attr("fill", (n) => colorMap.get(n.data.id));*/
    .attr("fill", "white")
    .attr("stroke", "black")
    .on('mouseover',function(d){
      d3.select(this)
      .attr("opacity", 0.5)
      .attr("stroke","white")
      .attr("stroke-width", 6);
    })
    .on('mouseout', function(d){
      d3.select(this)
      .attr("opacity", 1)
      .attr("stroke","black")
      .attr("stroke-width",1);
    });

  // Add text to nodes
  nodes
    .append("text")
    .text((d) => idMap[d.data.id][0])
    /*.attr("font-weight", "bold")
    .attr("font-family", "sans-serif")
    .attr("text-anchor", "middle")
    .attr("alignment-baseline", "middle")
    .attr("fill", "white");*/
    .attr("text-anchor", "middle")
    .attr("alignment-baseline", "middle");
})();
