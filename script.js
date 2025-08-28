(() => {
  // Map max personal by size
  const maxPersonnelBySize = {
    pequeño: 320,
    mediano: 480,
    grande: 560,
  };

  // Puestos por categoría
  const puestosByCategoria = {
    culinario: ['Cocinero', 'Mesero', 'Chef', 'Barista', 'Repostero', 'Bartender'],
    mantenimiento: ['Ingeniero', 'Conserje', 'Plomero', 'Mucama'],
    entretenimiento: ['Animadores', "DJ's", 'Musicos', 'Bailarines', 'Guias Turisticos'],
    medico: ['Enfermero', 'Medico Auxiliar', 'Medico en Jefe', 'Doctor Especialista'],
    administrativo: ['Administrador', 'Cajero', 'Gerente'],
  };

  // Set puestos especialistas no editables, incluye Gerentes, Plomeros, Músicos
  const puestosNoEditables = new Set([
    'Chef',
    'Medico en Jefe',
    'Doctor Especialista',
    'Guias Turisticos',
    'Ingeniero',
    'Gerente',
    'Plomero',
    'Musicos',
  ]);

  // Variables de estado
  let cruiseSize = null;
  let maxPersonnel = 0;
  let standbyList = [];
  let hiredList = [];

  // DOM Elements
  const cruiseSizeSection = document.getElementById('cruise-size-section');
  const personnelSection = document.getElementById('personnel-section');
  const cruiseSizeForm = document.getElementById('cruiseSizeForm');

  // Standby
  const standbyTableBody = document.querySelector('#standbyTable tbody');
  const standbyNotice = document.getElementById('standbyNotice');

  // Manual entry form
  const nombreInput = document.getElementById('nombre');
  const apellidoInput = document.getElementById('apellido');
  const edadInput = document.getElementById('edad');
  const experienciaInput = document.getElementById('experiencia');
  const salarioInput = document.getElementById('salario');
  const categoriaSelect = document.getElementById('categoria');
  const puestoSelect = document.getElementById('puesto');
  const personnelForm = document.getElementById('personnelForm');

  // Filters & hired table
  const filterCategoria = document.getElementById('filterCategoria');
  const personnelTableBody = document.querySelector('#personnelTable tbody');
  const maxPersonnelNotice = document.getElementById('maxPersonnelNotice');
  const generateRandomBtn = document.getElementById('generateRandomBtn');

  // Validar inputs para nombre y apellido (Solo letras y max 10)
  function isValidName(str) {
    return /^[A-Za-zÁÉÍÓÚáéíóúÑñüÜ]+$/.test(str) && str.length <= 10;
  }

  // Capitaliza la primera letra
  function capitalize(str) {
    if (!str) return '';
    return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
  }

  // Actualiza puestos según categoría y habilita select
  function updatePuestos() {
    const cat = categoriaSelect.value;
    puestoSelect.innerHTML = '<option value="">-- Seleccione puesto --</option>';
    if (cat && puestosByCategoria[cat]) {
      puestosByCategoria[cat].forEach(p => {
        const option = document.createElement('option');
        option.value = p;
        option.textContent = p;
        puestoSelect.appendChild(option);
      });
      puestoSelect.disabled = false;
    } else {
      puestoSelect.disabled = true;
    }
  }

  // Cuando cambia categoría en formulario
  categoriaSelect.addEventListener('change', () => {
    updatePuestos();
  });

  // Evento envío tamaño crucero
  cruiseSizeForm.addEventListener('submit', e => {
    e.preventDefault();
    const selectedSize = cruiseSizeForm.cruiseSize.value;
    if (!selectedSize) {
      alert('Debes seleccionar un tamaño de crucero.');
      return;
    }
    cruiseSize = selectedSize;
    maxPersonnel = maxPersonnelBySize[cruiseSize];
    cruiseSizeSection.classList.add('hidden');
    personnelSection.classList.remove('hidden');
    updateMaxPersonnelNotice();
    renderStandbyTable();
    renderHiredTable();
  });

  // Agregar personal al StandBy
  personnelForm.addEventListener('submit', e => {
    e.preventDefault();

    // Recolección y validación
    let nombre = nombreInput.value.trim();
    let apellido = apellidoInput.value.trim();
    let edad = edadInput.value.trim();
    let experiencia = experienciaInput.value.trim();
    let salario = salarioInput.value.trim();
    let categoria = categoriaSelect.value;
    let puesto = puestoSelect.value;

    // Validaciones específicas
    if (!nombre || !apellido || !edad || !experiencia || !salario || !categoria || !puesto) {
      alert('Por favor completa todos los campos.');
      return;
    }
    if (!isValidName(nombre)) {
      alert('Nombre inválido: solo letras y máximo 10 caracteres.');
      return;
    }
    if (!isValidName(apellido)) {
      alert('Apellido inválido: solo letras y máximo 10 caracteres.');
      return;
    }

    edad = Number(edad);
    if (isNaN(edad) || edad < 18 || edad > 70) {
      alert('Edad inválida (18-70).');
      return;
    }

    experiencia = Number(experiencia);
    if (isNaN(experiencia) || experiencia < 0 || experiencia > 50) {
      alert('Experiencia inválida (0-50 años).');
      return;
    }

    salario = Number(salario);
    if (
      isNaN(salario) ||
      salario < 100 ||
      salario > 1200 ||
      salario.toString().length > 8
    ) {
      alert('Salario inválido (mínimo 100, máximo 1200, máximo 8 dígitos).');
      return;
    }

    // Capitalizar nombre y apellido
    nombre = capitalize(nombre);
    apellido = capitalize(apellido);

    // Insertar en StandBy
    standbyList.push({
      id: crypto.randomUUID(),
      nombre,
      apellido,
      edad,
      experiencia,
      salario,
      categoria,
      puesto,
    });

    resetForm();
    renderStandbyTable();
    updateStandbyNotice();
  });

  function resetForm() {
    personnelForm.reset();
    puestoSelect.innerHTML = '<option value="">-- Seleccione puesto --</option>';
    puestoSelect.disabled = true;
  }

  // Renderizar tabla de Stand By
  function renderStandbyTable() {
    standbyTableBody.innerHTML = '';
    if (standbyList.length === 0) {
      const tr = document.createElement('tr');
      const td = document.createElement('td');
      td.colSpan = 8;
      td.classList.add('empty-row');
      td.textContent = 'No hay personal en Stand By.';
      tr.appendChild(td);
      standbyTableBody.appendChild(tr);
      return;
    }

    standbyList.forEach(p => {
      const tr = document.createElement('tr');

      tr.appendChild(createTdCentered(p.nombre));
      tr.appendChild(createTdCentered(p.apellido));
      tr.appendChild(createTdCentered(p.edad));
      tr.appendChild(createTdCentered(p.experiencia));
      tr.appendChild(createTdCentered(p.salario.toFixed(2)));
      tr.appendChild(createTdCentered(capitalize(p.categoria)));
      tr.appendChild(createTdCentered(p.puesto));

      // Acciones: botón "Contratar" y botón "Eliminar"
      const accionesTd = document.createElement('td');
      accionesTd.style.textAlign = 'center';

      const contratarBtn = document.createElement('button');
      contratarBtn.textContent = 'Contratar';
      contratarBtn.classList.add('hire-btn');
      contratarBtn.title = 'Contratar personal';

      contratarBtn.addEventListener('click', () => {
        if (hiredList.length >= maxPersonnel) {
          alert(
            `No puedes contratar más personal. Capacidad máxima alcanzada: ${maxPersonnel}`
          );
          return;
        }
        // Mover de standby a contratado
        hiredList.push(p);
        standbyList = standbyList.filter(x => x.id !== p.id);
        renderStandbyTable();
        renderHiredTable();
        updateStandbyNotice();
        updateMaxPersonnelNotice();
      });

      const eliminarBtn = document.createElement('button');
      eliminarBtn.textContent = 'Eliminar';
      eliminarBtn.classList.add('delete-btn');
      eliminarBtn.title = 'Eliminar del Stand By';

      eliminarBtn.addEventListener('click', () => {
        if (confirm(`¿Seguro que quieres eliminar a ${p.nombre} ${p.apellido} del Stand By?`)) {
          standbyList = standbyList.filter(x => x.id !== p.id);
          renderStandbyTable();
          updateStandbyNotice();
        }
      });

      accionesTd.appendChild(contratarBtn);
      accionesTd.appendChild(eliminarBtn);
      tr.appendChild(accionesTd);

      standbyTableBody.appendChild(tr);
    });
  }

  // Renderizar tabla personal contratado
  function renderHiredTable() {
    personnelTableBody.innerHTML = '';
    const filter = filterCategoria.value;

    const filtered = filter === 'all' ? hiredList : hiredList.filter(p => p.categoria === filter);

    if (filtered.length === 0) {
      const tr = document.createElement('tr');
      const td = document.createElement('td');
      td.colSpan = 8;
      td.classList.add('empty-row');
      td.textContent = 'No hay personal contratado para mostrar.';
      tr.appendChild(td);
      personnelTableBody.appendChild(tr);
      return;
    }

    filtered.forEach(p => {
      const tr = document.createElement('tr');

      tr.appendChild(createTdCentered(p.nombre));
      tr.appendChild(createTdCentered(p.apellido));
      tr.appendChild(createTdCentered(p.edad));
      tr.appendChild(createTdCentered(p.experiencia));

      // Salario editable o no según reglas especialistas
      const tdSalario = document.createElement('td');
      tdSalario.textContent = p.salario.toFixed(2);
      tdSalario.classList.add('editable-salario');
      tdSalario.contentEditable = !puestosNoEditables.has(p.puesto);
      applyEditableStyles(tdSalario);

      // Puesto editable o no y categoría sincronizada
      const tdPuesto = document.createElement('td');
      tdPuesto.textContent = p.puesto;
      if (puestosNoEditables.has(p.puesto)) {
        tdPuesto.contentEditable = false;
        tdPuesto.style.userSelect = 'none';
        tdPuesto.style.backgroundColor = '#7fa1d1';
        tdPuesto.style.color = '#000';
      } else {
        tdPuesto.contentEditable = true;
        applyEditableStyles(tdPuesto);
      }

      tr.appendChild(tdSalario);
      tr.appendChild(createTdCentered(capitalize(p.categoria)));
      tr.appendChild(tdPuesto);

      // Acciones: sólo botón editar, no eliminar en contratado
      const accionesTd = document.createElement('td');
      accionesTd.style.textAlign = 'center';

      const editarBtn = document.createElement('button');
      editarBtn.textContent = 'Editar';
      editarBtn.classList.add('edit-btn');
      editarBtn.title = 'Guardar cambios';

      editarBtn.addEventListener('click', () => {
        if (puestosNoEditables.has(p.puesto)) {
          // Detectar si usuario cambia cualquiera celda editable de especialista (salario o puesto)
          const salModificada = tdSalario.textContent.trim() !== p.salario.toFixed(2);
          const puestoModificado = tdPuesto.textContent.trim() !== p.puesto;
          if (salModificada || puestoModificado) {
            alert('Este es un personal especialista y no puede ser alterado');
            renderHiredTable();
            return;
          }
          // No cambios, nada que hacer
          alert('No hay cambios para guardar.');
          return;
        }

        // Para personal normal
        const newSalario = parseFloat(tdSalario.textContent);
        const newPuesto = tdPuesto.textContent.trim();

        if (isNaN(newSalario) || newSalario < 100 || newSalario > 1200) {
          alert('Salario inválido (mínimo 100 - máximo 1200)');
          renderHiredTable();
          return;
        }

        // Validar que puesto existe y actualizar categoría automáticamente
        let categoriaNueva = null;
        for (const [cat, puestos] of Object.entries(puestosByCategoria)) {
          if (puestos.includes(newPuesto)) {
            categoriaNueva = cat;
            break;
          }
        }

        if (!categoriaNueva) {
          alert('El puesto no coincide con ninguna categoría válida.');
          renderHiredTable();
          return;
        }

        // Rechazar cambio de puesto si es especialista para evitar fraude (puesto editable solo en normal)
        if (puestosNoEditables.has(p.puesto) && p.puesto !== newPuesto) {
          alert(
            'Este es un personal especialista y no puede ser alterado'
          );
          renderHiredTable();
          return;
        }

        p.salario = newSalario;
        p.puesto = newPuesto;
        if (p.categoria !== categoriaNueva) {
          p.categoria = categoriaNueva;
        }

        alert('Personal actualizado correctamente.');
        renderHiredTable();
      });

      accionesTd.appendChild(editarBtn);

      tr.appendChild(accionesTd);

      personnelTableBody.appendChild(tr);
    });
  }

  // Actualizar el texto informativo del Standby
  function updateStandbyNotice() {
    standbyNotice.textContent = `Personal en Stand By: ${standbyList.length}`;
  }

  // Actualizar aviso máximo personal contratado
  function updateMaxPersonnelNotice() {
    maxPersonnelNotice.textContent = `Personal contratado: ${hiredList.length} / Máximo permitido: ${maxPersonnel}`;
  }

  // Crear td con texto centrado
  function createTdCentered(text) {
    const td = document.createElement('td');
    td.textContent = text;
    td.style.textAlign = 'center';
    td.style.color = '#000';
    return td;
  }

  // Aplicar estilos para celdas editables
  function applyEditableStyles(td) {
    td.style.cursor = 'text';
    td.style.backgroundColor = '#629ce9';
    td.style.borderRadius = '6px';
    td.style.userSelect = 'text';
    td.style.color = '#000';

    td.addEventListener('focus', () => {
      td.style.outline = '2px solid #003366';
      td.style.backgroundColor = '#4179c3';
      td.style.color = '#fff';
      td.style.userSelect = 'text';
    });

    td.addEventListener('blur', () => {
      td.style.outline = 'none';
      td.style.backgroundColor = '#629ce9';
      td.style.color = '#000';
    });
  }

  // Datos ampliados para generación aleatoria (30 nombres y 30 apellidos)
  const nombresEjemplo = [
    'Ana', 'Luis', 'Carla', 'Jorge', 'María', 'Pedro', 'Laura', 'Diego', 'Sofia', 'Miguel',
    'Eva', 'Raúl', 'Pablo', 'Emma', 'Lucia', 'Alberto', 'Clara', 'Mario', 'Valeria', 'David',
    'Isabel', 'Tomás', 'Marta', 'Renata', 'Sergio', 'Patricia', 'Andres', 'Gabriela', 'Hugo', 'Elena'
  ];

  const apellidosEjemplo = [
    'Gomez', 'Fernandez', 'Lopez', 'Martinez', 'Garcia', 'Rodriguez', 'Sanchez', 'Perez',
    'Ramirez', 'Torres', 'Flores', 'Diaz', 'Castro', 'Rojas', 'Silva', 'Vargas', 'Molina',
    'Cruz', 'Suarez', 'Ortiz', 'Morales', 'Jimenez', 'Campos', 'Reyes', 'Gutierrez', 'Alvarez', 'Benitez', 'Bravo', 'Cuevas'
  ];

  // Generadores random para edad, experiencia y salario
  const experienciaRandom = () => Math.floor(Math.random() * 31);
  const edadRandom = () => Math.floor(Math.random() * 43) + 18;

  // Salario entre 100 y 1200 usd inclusive, con decimales a 2 cifras
  const salarioRandom = () => (Math.random() * 1100 + 100).toFixed(2);

  // Función para elegir aleatoriamente categoría y puesto
  function getRandomCategoriaYPuesto() {
    const categorias = Object.keys(puestosByCategoria);
    const cat = categorias[Math.floor(Math.random() * categorias.length)];
    const puestos = puestosByCategoria[cat];
    const puesto = puestos[Math.floor(Math.random() * puestos.length)];
    return { cat, puesto };
  }

  // Botón generación aleatoria
  generateRandomBtn.addEventListener('click', () => {
    if (hiredList.length >= maxPersonnel) {
      alert(`Se alcanzó el máximo de personal permitido (${maxPersonnel}).`);
      return;
    }
    const remainingSpace = maxPersonnel - hiredList.length;
    const cantidad = parseInt(
      prompt(`¿Cuántos empleados aleatorios quieres generar? (máximo ${remainingSpace})`, '5')
    );
    if (isNaN(cantidad) || cantidad <= 0) {
      alert('Cantidad inválida.');
      return;
    }
    if (cantidad > remainingSpace) {
      alert(`Solo puedes contratar hasta ${remainingSpace} empleados más.`);
      return;
    }

    for (let i = 0; i < cantidad; i++) {
      const { cat, puesto } = getRandomCategoriaYPuesto();
      const nuevo = {
        id: crypto.randomUUID(),
        nombre: nombresEjemplo[Math.floor(Math.random() * nombresEjemplo.length)],
        apellido: apellidosEjemplo[Math.floor(Math.random() * apellidosEjemplo.length)],
        edad: edadRandom(),
        experiencia: experienciaRandom(),
        salario: parseFloat(salarioRandom()),
        categoria: cat,
        puesto,
      };
      // Se agrega al Standby primero
      standbyList.push(nuevo);
    }
    renderStandbyTable();
    updateStandbyNotice();
  });

  // Filtro categoría en personal contratado
  filterCategoria.addEventListener('change', () => {
    renderHiredTable();
  });
})();
