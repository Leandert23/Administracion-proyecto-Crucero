// Funcionalidad para Recursos Humanos

document.addEventListener('DOMContentLoaded', function() {
    // Mapeo de categorías a puestos
    const puestosPorCategoria = {
        'Culinario': ['Chef Ejecutivo', 'Sous Chef', 'Cocinero', 'Ayudante de Cocina', 'Pastelero'],
        'Medico': ['Médico General', 'Enfermero', 'Paramédico', 'Técnico Médico', 'Farmacéutico'],
        'Administrativo': ['Gerente Administrativo', 'Secretario', 'Contador', 'Recepcionista', 'Asistente Administrativo'],
        'Mantenimiento': ['Jefe de Mantenimiento', 'Técnico Eléctrico', 'Plomero', 'Carpintero', 'Pintor'],
        'Entretenimiento': ['Director de Entretenimiento', 'Animador', 'Músico', 'Instructor', 'Guía Turístico'],
        'Personal Extra': ['Mesero', 'Camarero', 'Limpiador', 'Botones', 'Ayudante General']
    };

    // Elementos del formulario
    const categoriaSelect = document.getElementById('categoria');
    const puestoSelect = document.getElementById('puesto');
    const edadInput = document.getElementById('edad');
    const experienciaInput = document.getElementById('anios_experiencia');

    // Función para actualizar puestos según categoría
    function actualizarPuestos() {
        const categoriaSeleccionada = categoriaSelect.value;
        const puestos = puestosPorCategoria[categoriaSeleccionada] || [];

        // Limpiar opciones actuales
        puestoSelect.innerHTML = '<option value="" disabled selected>Seleccione</option>';

        // Agregar nuevas opciones
        puestos.forEach(puesto => {
            const option = document.createElement('option');
            option.value = puesto;
            option.textContent = puesto;
            puestoSelect.appendChild(option);
        });
    }

    // Event listener para cambio de categoría
    if (categoriaSelect && puestoSelect) {
        categoriaSelect.addEventListener('change', actualizarPuestos);
    }

    // Función para validar edad
    function validarEdad() {
        const edad = parseInt(edadInput.value);
        if (edad < 21) {
            edadInput.setCustomValidity('La edad debe ser mayor o igual a 21 años');
        } else {
            edadInput.setCustomValidity('');
        }
    }

    // Event listeners para validación
    if (edadInput) {
        edadInput.addEventListener('input', validarEdad);
        edadInput.addEventListener('change', validarEdad);
    }

    // Función para validar experiencia
    function validarExperiencia() {
        const experiencia = parseInt(experienciaInput.value || 0);
        if (experiencia < 0) {
            experienciaInput.setCustomValidity('Los años de experiencia no pueden ser negativos');
        } else {
            experienciaInput.setCustomValidity('');
        }
    }

    if (experienciaInput) {
        experienciaInput.addEventListener('input', validarExperiencia);
        experienciaInput.addEventListener('change', validarExperiencia);
    }

    // Funcionalidad para la tabla de personal
    const editarBotones = document.querySelectorAll('.btn-editar');
    const eliminarBotones = document.querySelectorAll('.btn-eliminar');

    // Función para editar personal
    editarBotones.forEach(boton => {
        boton.addEventListener('click', function() {
            const fila = this.closest('tr');
            const id = fila.dataset.id;

            // Aquí puedes agregar la lógica para editar
            alert(`Editar personal con ID: ${id}`);
        });
    });

    // Función para eliminar personal
    eliminarBotones.forEach(boton => {
        boton.addEventListener('click', function() {
            const fila = this.closest('tr');
            const id = fila.dataset.id;

            if (confirm('¿Estás seguro de que quieres eliminar este registro?')) {
                // Aquí puedes agregar la lógica para eliminar
                alert(`Eliminar personal con ID: ${id}`);
            }
        });
    });

    console.log('JavaScript de Recursos Humanos cargado correctamente');
});
