// Solicitud de la posición al servicio de ubicación del dispositivo (CU-S04).
// La posición viaja como parámetro de la consulta y no se almacena.
(function () {
  function informar(id, texto, esError) {
    var caja = document.getElementById(id);
    if (!caja) return;
    caja.className = "mensaje" + (esError ? " error" : "");
    caja.innerHTML = "<p>" + texto + "</p>";
  }
  var SIN_POSICION = "Habilite la ubicación para ver las sucursales cercanas.";

  // Pantalla de tiendas cercanas.
  var boton = document.getElementById("usar-ubicacion");
  if (boton) {
    boton.addEventListener("click", function () {
      if (!navigator.geolocation) { informar("mensaje", SIN_POSICION, true); return; }
      informar("mensaje", "Solicitando su ubicación…", false);
      navigator.geolocation.getCurrentPosition(function (posicion) {
        document.getElementById("latitud").value = posicion.coords.latitude;
        document.getElementById("longitud").value = posicion.coords.longitude;
        document.getElementById("form-ubicacion").submit();
      }, function () {
        informar("mensaje", SIN_POSICION, true);
      }, { timeout: 15000 });
    });
  }

  // Lista de compras: sucursal más cercana de cada supermercado (CU-S02, extensión 5b).
  var verSucursales = document.getElementById("ver-sucursales");
  if (verSucursales) {
    verSucursales.addEventListener("click", function () {
      if (!navigator.geolocation) { informar("mensaje-ubicacion", SIN_POSICION, true); return; }
      navigator.geolocation.getCurrentPosition(function (posicion) {
        var datos = new URLSearchParams();
        datos.append("latitud", posicion.coords.latitude);
        datos.append("longitud", posicion.coords.longitude);
        fetch(verSucursales.dataset.url, { method: "POST", body: datos })
          .then(function (r) { return r.json(); })
          .then(function (tiendas) {
            var masCercana = {};
            (tiendas || []).forEach(function (t) { if (!masCercana[t.cadena]) masCercana[t.cadena] = t; });
            document.querySelectorAll("[data-sucursal]").forEach(function (celda) {
              var t = masCercana[celda.dataset.sucursal];
              celda.textContent = t ? (t.nombre + ", a " + t.distancia_km.toFixed(1).replace(".", ",") + " km")
                                    : "Sin sucursal registrada en el radio de cobertura";
            });
            informar("mensaje-ubicacion", "Se agregó la sucursal más cercana de cada supermercado. Su ubicación no se guarda.", false);
          })
          .catch(function () { informar("mensaje-ubicacion", "No fue posible consultar las sucursales.", true); });
      }, function () {
        informar("mensaje-ubicacion", SIN_POSICION, true);
      }, { timeout: 15000 });
    });
  }
})();
