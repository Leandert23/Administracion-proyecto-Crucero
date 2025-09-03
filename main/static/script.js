(() => {
  const maxPersonnelBySize = {
    pequeño: 320,
    mediano: 480,
    grande: 560,
  };

  const puestosByCategoria = {
    culinario: ['Cocinero', 'Mesero', 'Chef', 'Barista', 'Repostero', 'Bartender'],
    mantenimiento: ['Ingeniero', 'Conserje', 'Plomero', 'Mucama'],
    entretenimiento: ['Animadores', "DJ's", 'Musicos', 'Bailarines', 'Guias Turisticos'],
    medico: ['Enfermero', 'Medico Auxiliar', 'Medico en Jefe', 'Doctor Especialista'],
    administrativo: ['Administrador', 'Cajero', 'Gerente'],
  };

  const puestosNoEditables = new Set([
    'Chef', 'Medico en Jefe', 'Doctor Especialista', 'Guias Turisticos', 'Ingeniero', 'Gerente', 'Plomero', 'Musicos',
  ]);

  let cruiseSize = null;
  let maxPersonnel = 0;
  let standbyList = [];
  let hiredList = [];

  // DOM
  const cruiseSizeSection = document.getElementById('cruise-size-section');
  const personnelSection = document.getElementById('personnel-section');
  const cruiseSizeForm = document.getElementById('cruiseSizeForm');

  const standbyTableBody = document.querySelector('#standbyTable tbody');
  const standbyNotice = document.getElementById('standbyNotice');

  const nombreInput = document.getElementById('nombre');
  const apellidoInput = document.getElementById('apellido');
  const edadInput = document.getElementById('edad');
  const experienciaInput = document.getElementById('experiencia');
  const salarioInput = document.getElementById('salario');
  const categoriaSelect = document.getElementById('categoria');
  const puestoSelect = document.getElementById('puesto');
  const personnelForm = document.getElementById('personnelForm');

  const filterCategoria = document.getElementById('filterCategoria');
  const personnelTableBody = document.querySelector('#personnelTable tbody');
  const maxPersonnelNotice = document.getElementById('maxPersonnelNotice');
  const generateRandomBtn = document.getElementById('generateRandomBtn');

  function isValidName(str) {
    return /^[A-Za-zÁÉÍÓÚáéíóúÑñüÜ]+$/.test(str) && str.length <= 10;
  }

  function capitalize(str) {
    if (!str) return '';
    return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
  }

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

  categoriaSelect.addEventListener('change', updatePuestos);

  cruiseSizeForm.addEventListener('submit', e => {
    e.preventDefault();
    const selectedSize = cruiseSizeForm.cruiseSize.value;
    if (!selectedSize) {
      alert('Por favor, selecciona un tamaño de crucero.');
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

  document.getElementById('personnelForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const data = {
        nombre: document.getElementById('nombre').value,
        apellido: document.getElementById('apellido').value,
        edad: document.getElementById('edad').value,
        experiencia: document.getElementById('experiencia').value,
        salario: document.getElementById('salario').value,
        categoria: document.getElementById('categoria').value,
        puesto: document.getElementById('puesto').value,
    };
    fetch('/api/agregar_personal/', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        // Actualiza la tabla o muestra mensaje de éxito
    });
});

  function resetForm() {
    personnelForm.reset();
    puestoSelect.innerHTML = '<option value="">-- Seleccione puesto --</option>';
    puestoSelect.disabled = true;
  }

  function createTdCentered(text) {
    const td = document.createElement('td');
    td.textContent = text;
    td.style.textAlign = 'left';
    td.style.color = '#1e293b';
    return td;
  }

  function applyEditableStyles(td) {
    td.style.cursor = 'text';
    td.style.background = '#f9fafb';
    td.style.border = '1px dashed transparent';
    td.style.borderRadius = '4px';
    td.style.userSelect = 'text';

    td.addEventListener('focus', () => {
      td.style.outline = '2px solid #3b82f6';
      td.style.background = '#e0e7ff';
    });

    td.addEventListener('blur', () => {
      td.style.outline = 'none';
      td.style.background = '#f9fafb';
    });
  }

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

      const accionesTd = document.createElement('td');
      accionesTd.style.textAlign = 'left';

      const contratarBtn = document.createElement('button');
      contratarBtn.textContent = 'Contratar';
      contratarBtn.className = 'hire-btn';
      contratarBtn.title = 'Contratar personal';
      contratarBtn.addEventListener('click', () => {
        if (hiredList.length >= maxPersonnel) {
          alert(`Capacidad máxima alcanzada: ${maxPersonnel}`);
          return;
        }
        hiredList.push(p);
        standbyList = standbyList.filter(x => x.id !== p.id);
        renderStandbyTable();
        renderHiredTable();
        updateStandbyNotice();
        updateMaxPersonnelNotice();
      });

      const eliminarBtn = document.createElement('button');
      eliminarBtn.textContent = 'Eliminar';
      eliminarBtn.className = 'delete-btn';
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

      // Salario y Puesto: NO editables por defecto
      const tdSalario = document.createElement('td');
      tdSalario.textContent = p.salario.toFixed(2);
      tdSalario.contentEditable = false;
      applyEditableStyles(tdSalario);

      const tdPuesto = document.createElement('td');
      tdPuesto.textContent = p.puesto;
      tdPuesto.contentEditable = false;
      if (puestosNoEditables.has(p.puesto)) {
        tdPuesto.style.userSelect = 'none';
        tdPuesto.style.backgroundColor = '#e2e8f0';
        tdPuesto.style.color = '#6b7280';
      } else {
        applyEditableStyles(tdPuesto);
      }

      tr.appendChild(tdSalario);
      tr.appendChild(createTdCentered(capitalize(p.categoria)));
      tr.appendChild(tdPuesto);

      const accionesTd = document.createElement('td');
      accionesTd.style.textAlign = 'left';

      const editarBtn = document.createElement('button');
      editarBtn.textContent = 'Editar';
      editarBtn.className = 'edit-btn';
      editarBtn.title = 'Editar campos';

      let editMode = false;

      editarBtn.addEventListener('click', () => {
        if (!editMode) {
          // Al entrar en modo edición
          if (puestosNoEditables.has(p.puesto)) {
            alert('Este es un personal especialista y no puede ser alterado');
            return;
          }
          tdSalario.contentEditable = true;
          tdPuesto.contentEditable = true;
          tdSalario.focus();
          editarBtn.textContent = 'Guardar';
          editarBtn.title = 'Guardar cambios';
          editMode = true;
        } else {
          // Guardar cambios
          const newSalario = parseFloat(tdSalario.textContent);
          const newPuesto = tdPuesto.textContent.trim();

          // Validaciones
          const rango = salarioPorPuesto[newPuesto] || [100, 99999999];
          if (isNaN(newSalario) || newSalario < rango[0] || newSalario > rango[1]) {
            alert(`Salario inválido para el puesto seleccionado (min ${rango[0]} - max ${rango[1]})`);
            renderHiredTable();
            return;
          }

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

          p.salario = newSalario;
          p.puesto = newPuesto;
          if (p.categoria !== categoriaNueva) {
            p.categoria = categoriaNueva;
          }

          tdSalario.contentEditable = false;
          tdPuesto.contentEditable = false;
          editarBtn.textContent = 'Editar';
          editarBtn.title = 'Editar campos';
          editMode = false;
          alert('Personal actualizado correctamente.');
          renderHiredTable();
        }
      });

      accionesTd.appendChild(editarBtn);
      tr.appendChild(accionesTd);
      personnelTableBody.appendChild(tr);
    });
  }

  // Evento para filtrar la tabla de personal contratado por categoria seleccionada
  filterCategoria.addEventListener('change', () => {
  renderHiredTable();
  });


  function updateStandbyNotice() {
    standbyNotice.textContent = `Personal en Stand By: ${standbyList.length}`;
  }

  function updateMaxPersonnelNotice() {
    maxPersonnelNotice.textContent = `Personal contratado: ${hiredList.length} / Máximo permitido: ${maxPersonnel}`;
  }

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

  const experienciaRandom = () => Math.floor(Math.random() * 31);
  const edadRandom = () => Math.floor(Math.random() * 43) + 18;
  const salarioRandom = () => (Math.random() * 1100 + 100).toFixed(2);

  // Rango de salarios por puesto (AJUSTAR SI ES NECESARIO)
  const salarioPorPuesto = {
    'Cocinero': [800, 1500],
    'Mesero': [600, 1200],
    'Chef': [2000, 3500],
    'Barista': [700, 1200],
    'Repostero': [800, 1400],
    'Bartender': [900, 1500],
    'Ingeniero': [2500, 4000],
    'Conserje': [600, 1000],
    'Plomero': [1200, 2000],
    'Mucama': [600, 900],
    'Animadores': [1000, 2000],
    "DJ's": [1000, 2500],
    'Musicos': [1200, 2500],
    'Bailarines': [1000, 2000],
    'Guias Turisticos': [1500, 3000],
    'Enfermero': [1200, 2000],
    'Medico Auxiliar': [1800, 2500],
    'Medico en Jefe': [3500, 5000],
    'Doctor Especialista': [4000, 6000],
    'Administrador': [1800, 3000],
    'Cajero': [900, 1400],
    'Gerente': [3000, 5000],
  };

  // Genera un salario aleatorio en incrementos de 250 dentro del rango del puesto, para ser realista.
  function salarioRandomPorPuesto(puesto) {
    const rango = salarioPorPuesto[puesto] || [100, 1200];
    const [min, max] = rango;
    const pasos = Math.floor((max - min) / 250) + 1;
    const incremento = Math.floor(Math.random() * pasos);
    return min + incremento * 250;
  }

  function getRandomCategoriaYPuesto() {
    const categorias = Object.keys(puestosByCategoria);
    const cat = categorias[Math.floor(Math.random() * categorias.length)];
    const puestos = puestosByCategoria[cat];
    const puesto = puestos[Math.floor(Math.random() * puestos.length)];
    return { cat, puesto };
  }

  generateRandomBtn.addEventListener('click', () => {
    if (hiredList.length >= maxPersonnel) {
      alert(`Se alcanzó el máximo de personal permitido (${maxPersonnel}).`);
      return;
    }
    const remainingSpace = maxPersonnel - hiredList.length;
    const cantidad = parseInt(prompt(`¿Cuántos empleados aleatorios quieres generar? (máximo ${remainingSpace})`, '5'));
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
        salario: salarioRandomPorPuesto(puesto), // <--- Aquí el cambio
        categoria: cat,
        puesto,
      };
      standbyList.push(nuevo);
    }
    renderStandbyTable();
    updateStandbyNotice();
  });

})();
