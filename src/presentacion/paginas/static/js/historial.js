// Diagrama de líneas del historial (CU-S03). Cada supermercado se distingue por
// el trazo de su línea y por su rótulo, sin depender del color.
(function () {
  var datos = JSON.parse(document.getElementById("datos-historial").textContent);
  var trazos = { "Ara": [10, 6], "D1": [2, 4], "Olímpica": [] };
  var grosor = { "Ara": 3, "D1": 3, "Olímpica": 3 };
  var fechas = [];
  Object.keys(datos).forEach(function (cadena) {
    datos[cadena].forEach(function (p) { if (fechas.indexOf(p.fecha) < 0) fechas.push(p.fecha); });
  });
  fechas.sort();
  var series = Object.keys(datos).map(function (cadena) {
    var porFecha = {};
    datos[cadena].forEach(function (p) { porFecha[p.fecha] = p.precio; });
    return {
      label: cadena,
      data: fechas.map(function (f) { return porFecha[f] === undefined ? null : porFecha[f]; }),
      borderColor: "#1a1a1a", backgroundColor: "#1a1a1a",
      borderDash: trazos[cadena] || [6, 3], borderWidth: grosor[cadena] || 2,
      pointRadius: 3, spanGaps: true, tension: 0
    };
  });
  var etiquetasFecha = fechas.map(function (f) { var p = f.split("-"); return p[2] + "/" + p[1] + "/" + p[0]; });
  var pesos = function (v) { return "$ " + Math.round(v).toLocaleString("es-CO"); };
  new Chart(document.getElementById("grafica-historial"), {
    type: "line",
    data: { labels: etiquetasFecha, datasets: series },
    options: {
      responsive: true,
      plugins: {
        legend: { labels: { color: "#1a1a1a", font: { size: 16 }, usePointStyle: false } },
        tooltip: { callbacks: { label: function (c) { return c.dataset.label + ": " + pesos(c.parsed.y); } } }
      },
      scales: {
        y: { ticks: { color: "#1a1a1a", callback: pesos } },
        x: { ticks: { color: "#1a1a1a" } }
      }
    }
  });
})();
