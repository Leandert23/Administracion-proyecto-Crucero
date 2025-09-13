// Script para repoblar la lista de países al recargar el formulario
window.addEventListener('DOMContentLoaded', function() {
    var paisesJsonInput = document.getElementById('paises-json');
    var paisList = document.getElementById('pais-list');
    if (paisesJsonInput && paisList) {
        var paises = [];
        try {
            paises = JSON.parse(paisesJsonInput.value);
        } catch (e) {
            paises = [];
        }
        paisList.innerHTML = '';
        paises.forEach(function(pais, idx) {
            var li = document.createElement('li');
            li.textContent = pais;
            var btn = document.createElement('button');
            btn.textContent = 'Eliminar';
            btn.type = 'button';
            btn.style.marginLeft = '8px';
            btn.className = 'btn-eliminar-pais';
            btn.onclick = function() {
                paises.splice(idx, 1);
                paisesJsonInput.value = JSON.stringify(paises);
                li.remove();
            };
            li.appendChild(btn);
            paisList.appendChild(li);
        });
    }
    // --- NUEVO: Mantener países al cambiar tipo ---
    var tipoSelect = document.getElementById('id_tipo');
    if (tipoSelect) {
        tipoSelect.addEventListener('change', function(e) {
            // Antes de submit, aseguramos que paises_json tenga el valor actual
            if (paisesJsonInput) {
                // Si hay países en la lista visual, los guardamos en el input
                var paisesActuales = [];
                var lis = paisList.querySelectorAll('li');
                lis.forEach(function(li) {
                    // El texto antes del botón Eliminar es el nombre del país
                    var nombrePais = li.childNodes[0].nodeValue.trim();
                    if (nombrePais) {
                        paisesActuales.push(nombrePais);
                    }
                });
                paisesJsonInput.value = JSON.stringify(paisesActuales);
            }
            // Ahora sí, submit
            tipoSelect.form.submit();
        });
    }
});
