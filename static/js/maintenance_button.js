// Botón universal para reportar mantenimiento en páginas del módulo Restaurante
(function(){
  if (!document.addEventListener) return;

  // Utilidades mínimas por si main.js aún no cargó
  function ensureRestaurantApp(){
    if (window.restaurantApp && window.restaurantApp.submitData) return window.restaurantApp;
    const csrftoken = (function getCookie(name){
      let cookieValue = null;
      if (document.cookie && document.cookie !== ''){
        const cookies = document.cookie.split(';');
        for (let c of cookies){
          const cookie = c.trim();
          if (cookie.substring(0, name.length + 1) === (name + '=')){
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            break;
          }
        }
      }
      return cookieValue;
    })('csrftoken');

    function showAlert(message, type='info'){
      const alertDiv = document.createElement('div');
      alertDiv.className = `alert alert-${type}`;
      alertDiv.textContent = message;
      const container = document.querySelector('.messages') || (function(){
        const el = document.createElement('div');
        el.className = 'messages';
        const main = document.querySelector('.main-content') || document.body;
        main.insertBefore(el, main.firstChild);
        return el;
      })();
      container.appendChild(alertDiv);
      setTimeout(()=>alertDiv.remove(), 5000);
    }

    function submitData(url, data, successMessage){
      return fetch(url, {
        method: 'POST',
        headers: {
          'X-CSRFToken': csrftoken,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
      })
      .then(r=>r.json())
      .then(json=>{
        if(json.success){
          showAlert(successMessage || json.message, 'success');
          return json;
        }
        throw new Error(json.message || 'Error desconocido');
      })
      .catch(err=>{ showAlert(err.message, 'error'); throw err; });
    }

    window.restaurantApp = window.restaurantApp || {};
    return Object.assign(window.restaurantApp, { showAlert, submitData });
  }

  const App = ensureRestaurantApp();

  // Cache de restaurantes para el modal
  let restaurantsCache = null;

  async function fetchRestaurants(){
    if (restaurantsCache) return restaurantsCache;
    try{
      const res = await fetch('/ajax/get-restaurants/');
      const data = await res.json();
      restaurantsCache = (data && data.restaurants) ? data.restaurants : [];
      return restaurantsCache;
    }catch(e){
      App.showAlert('No se pudieron cargar los restaurantes', 'error');
      return [];
    }
  }

  function createButton(){
    if (document.getElementById('maintenance-fab')) return;
    const btn = document.createElement('button');
    btn.id = 'maintenance-fab';
    btn.type = 'button';
    btn.innerHTML = '<i class="fas fa-tools"></i> Reportar Mantenimiento';
    btn.style.cssText = `
      position: fixed; right: 20px; bottom: 20px; z-index: 9999;
      background: #3b82f6; color: #fff; border: none; border-radius: 999px;
      padding: 12px 16px; box-shadow: 0 6px 18px rgba(0,0,0,.2);
      cursor: pointer; display: flex; align-items: center; gap: 8px; font-weight: 600;
    `;
    btn.addEventListener('mouseenter', ()=>{ btn.style.transform='translateY(-2px)'; });
    btn.addEventListener('mouseleave', ()=>{ btn.style.transform='none'; });
    btn.addEventListener('click', openModal);
    document.body.appendChild(btn);
  }

  function closeModal(){
    const modal = document.getElementById('maintenance-modal');
    if (modal) modal.remove();
  }

  async function openModal(){
    const restaurants = await fetchRestaurants();

    const overlay = document.createElement('div');
    overlay.id = 'maintenance-modal';
    overlay.style.cssText = `
      position: fixed; inset: 0; background: rgba(0,0,0,.45); z-index: 10000;
      display:flex; align-items:center; justify-content:center; padding: 16px;
    `;
    const box = document.createElement('div');
    box.style.cssText = `background:#fff; border-radius:12px; width:100%; max-width:560px; padding:20px;`;
    box.innerHTML = `
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
        <h3 style="margin:0;display:flex;align-items:center;gap:8px;color:#1f2937;"><i class="fas fa-tools" style="color:#3b82f6"></i> Reportar Mantenimiento</h3>
        <button type="button" id="mm-close" style="font-size:22px;background:none;border:none;cursor:pointer">&times;</button>
      </div>
      <form id="maintenance-quick-form" class="add-form">
        <div class="form-grid">
          <div class="form-group">
            <label>Área</label>
            <select name="area" required>
              <option value="">Seleccionar Área</option>
              <option value="cocina">Cocina</option>
              <option value="comedor">Comedor</option>
              <option value="bar">Bar</option>
              <option value="almacen">Almacén</option>
              <option value="equipos">Equipos</option>
              <option value="refrigeracion">Refrigeración</option>
              <option value="limpieza">Limpieza</option>
            </select>
          </div>
          <div class="form-group">
            <label>Restaurante</label>
            <select name="restaurant_id" required>
              <option value="">Seleccionar Restaurante</option>
              ${restaurants.map(r=>`<option value="${r.id}">${r.name} (${r.type_display})</option>`).join('')}
            </select>
          </div>
          <div class="form-group">
            <label>Prioridad</label>
            <select name="priority" required>
              <option value="">Seleccionar Prioridad</option>
              <option value="baja">Baja</option>
              <option value="media">Media</option>
              <option value="alta">Alta</option>
              <option value="critica">Crítica</option>
            </select>
          </div>
          <div class="form-group">
            <label>Reportado por</label>
            <input type="text" name="reported_by" placeholder="Nombre del reportante" />
          </div>
          <div class="form-group" style="grid-column:1/-1;">
            <label>Descripción</label>
            <textarea name="description" rows="3" required placeholder="Describa detalladamente el problema"></textarea>
          </div>
        </div>
        <button type="submit" class="btn btn-primary" style="margin-top:12px"><i class="fas fa-paper-plane"></i> Enviar</button>
      </form>
    `;
    overlay.appendChild(box);
    document.body.appendChild(overlay);
    overlay.addEventListener('click', (e)=>{ if(e.target===overlay) closeModal(); });
    box.querySelector('#mm-close').addEventListener('click', closeModal);

    // Submit
    box.querySelector('#maintenance-quick-form').addEventListener('submit', function(e){
      e.preventDefault();
      const formData = new FormData(this);
      const data = {
        area: formData.get('area'),
        restaurant_id: formData.get('restaurant_id'),
        priority: formData.get('priority'),
        reported_by: formData.get('reported_by') || 'Sistema',
        description: formData.get('description')
      };
      App.submitData('/ajax/add-maintenance/', data, 'Problema de mantenimiento reportado exitosamente')
        .then(()=>{
          closeModal();
          if (location.pathname.includes('/restaurant/maintenance')) {
            setTimeout(()=>location.reload(), 800);
          }
        })
        .catch(()=>{});
    });
  }

  document.addEventListener('DOMContentLoaded', createButton);
})();
