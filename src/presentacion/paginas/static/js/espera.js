// Mensaje de espera mientras el sistema responde (extensión *a de los casos de uso).
document.querySelectorAll("form[data-espera]").forEach(function (formulario) {
  formulario.addEventListener("submit", function () {
    var mensaje = document.getElementById("mensaje");
    if (mensaje) {
      mensaje.className = "mensaje";
      mensaje.setAttribute("role", "status");
      mensaje.innerHTML = "<p>Estamos buscando los mejores precios, por favor espera un momento.</p>";
    }
  });
});
