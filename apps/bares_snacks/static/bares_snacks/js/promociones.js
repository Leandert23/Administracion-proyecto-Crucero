/**const promoImages = {
    '2x1 en Cervezas': 'svg/promos/ber.svg',
    'Martes de Tacos': 'assets/taco.svg',
    'Jarra de Cerveza a Precio Especial': 'assets/beer-mug.svg',
    'Cócteles a Precio de Happy Hour toda la noche': 'assets/cocktail-glass.svg',
    'Brunch con Mimosa o Bloody Mary incluido': 'assets/tropical-drinks.svg',
    'Lunes de Trabajo': 'assets/coffee.svg',
    'Miércoles de Dulce': 'assets/bagel.svg',
    'Viernes de Tarde': 'assets/bubble-tea.svg',
};**/
const promocionesGrupos = [
    {
        grupo: 'Bares',
        promociones: [
            {
                nombre: '2x1 en Cervezas',
                dia: 'Lunes',
                desc: 'Ideal para empezar la semana con happy hour extendido.',
                happyHour: 'Descuentos en bebidas y aperitivos de 5pm a 8pm.'
            },
            {
                nombre: 'Martes de Tacos',
                dia: 'Martes',
                desc: 'Tacos o nachos a mitad de precio con la compra de una margarita.',
                happyHour: 'Descuentos en bebidas y aperitivos de 5pm a 8pm.'
            },
            {
                nombre: 'Jarra de Cerveza a Precio Especial',
                dia: 'Miércoles',
                desc: 'Descuento en jarras de cerveza para grupos.',
                happyHour: 'Descuentos en bebidas y aperitivos de 5pm a 8pm.'
            },
            {
                nombre: 'Cócteles a Precio de Happy Hour toda la noche',
                dia: 'Jueves',
                desc: 'Atrae a quienes empiezan el fin de semana temprano.',
                happyHour: 'Descuentos en bebidas y aperitivos de 5pm a 8pm.'
            },
            {
                nombre: 'Brunch con Mimosa o Bloody Mary incluido',
                dia: 'Domingo',
                desc: 'Ideal para domingos relajados.',
                happyHour: 'Descuentos en bebidas y aperitivos de 5pm a 8pm.'
            }
        ]
    },
    {
        grupo: 'Café',
        promociones: [
            {
                nombre: 'Lunes de Trabajo',
                dia: 'Lunes',
                desc: 'Descuento en café.',
                happyHour: '2x1 en Cafés en horarios específicos (de 8:00 a 10:00 AM)'
            },
            {
                nombre: 'Miércoles de Dulce',
                dia: 'Miércoles',
                desc: 'Al comprar un café.',
                happyHour: '2x1 en Cafés en horarios específicos (de 8:00 a 10:00 AM)'
            },
            {
                nombre: 'Viernes de Tarde',
                dia: 'Viernes',
                desc: 'Descuento en cafés fríos o smoothies después de las 3 PM.',
                happyHour: '2x1 en Cafés en horarios específicos (de 8:00 a 10:00 AM)'
            }
        ]
    }
];

// Keywords por promoción para mapear a un ProductoBar en el backend
const PROMO_KEYWORDS = {
    '2x1 en Cervezas': { keywords: ['cerveza','beer'], multiplier: 2 },
    'Martes de Tacos': { keywords: ['taco','nacho'], multiplier: 1 },
    'Jarra de Cerveza a Precio Especial': { keywords: ['jarra','cerveza'], multiplier: 1 },
    'Cócteles a Precio de Happy Hour toda la noche': { keywords: ['coctel','cóctel','cocktail'], multiplier: 1 },
    'Brunch con Mimosa o Bloody Mary incluido': { keywords: ['mimosa','bloody','mary','brunch'], multiplier: 1 },
    'Lunes de Trabajo': { keywords: ['cafe','café'], multiplier: 1 },
    'Miércoles de Dulce': { keywords: ['dulce','postre'], multiplier: 1 },
    'Viernes de Tarde': { keywords: ['frappe','frío','smoothie'], multiplier: 1 },
};

async function findProductoIdForPromo(promoNombre){
    try{
    const resp = await fetch('/bar/productos-bar/');
    const itemsRaw = await resp.json();
    // Quedarnos sólo con ProductoBar (origen === 'producto_bar')
    const items = (Array.isArray(itemsRaw)? itemsRaw: []).filter(x=> x.origen === 'producto_bar');
        if(!Array.isArray(items) || !items.length) return null;
        const config = PROMO_KEYWORDS[promoNombre] || null;
        if(config && Array.isArray(config.keywords)){
            const lcKeywords = config.keywords.map(k=>k.toLowerCase());
            // Buscar por nombre o categoría
            const found = items.find(p=>{
                const nombre = (p.nombre||'').toLowerCase();
                const cat = (p.categoria||'').toLowerCase();
                return lcKeywords.some(k=> nombre.includes(k) || cat.includes(k));
            });
            if(found) return found.id;
        }
        // Fallback: primera coincidencia por plan 'pago' o el primero
        const pago = items.find(p=> (p.tipo||p.plan)==='pago');
        return (pago ? pago.id : items[0].id);
    }catch(_e){
        return null;
    }
}

// Cargar habitaciones para el selector (Promos)
async function cargarHabitacionesEnSelect(selectEl){
    if(!selectEl) return;
    try{
        const resp = await fetch('/bar/habitaciones/');
        const data = await resp.json();
        if(Array.isArray(data)){
            // Ordenar por número si existe
            data.sort((a,b)=>{
                const an = parseInt(a.numero||0,10); const bn = parseInt(b.numero||0,10);
                return (isNaN(an)?0:an) - (isNaN(bn)?0:bn);
            });
            const opts = ['<option value="">Selecciona...</option>']
                .concat(data.map(h=>{
                    const numero = (h.numero!=null? h.numero : '').toString();
                    const codigo = (h.codigo || '').toString();
                    const texto = `Hab. ${numero}${codigo? ' ('+codigo+')':''}`;
                    return `<option value="${h.id}">${texto}</option>`;
                }));
            selectEl.innerHTML = opts.join('');
        }
    }catch(_e){
        selectEl.innerHTML = '<option value="">No disponible</option>';
    }
}

// Modal para pedir promoción
function mostrarModalPedirPromocion(promo) {
    // Si modal no existe aún en el DOM, lo creamos
    let modal = document.getElementById('modal-pedir-promocion');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'modal-pedir-promocion';
        modal.className = 'modal';
        modal.style.display = 'none';
        modal.innerHTML = `
            <div class="modal-content">
                <span class="close-modal" id="close-modal-pedir-promocion">&times;</span>
                <div id="modal-pedir-promocion-content"></div>
            </div>
        `;
        document.body.appendChild(modal);
    }
    const content = modal.querySelector('#modal-pedir-promocion-content');
    // Si no se pasa promo, permitir seleccionar una
    if(!promo){
        // Construir selector de promociones disponibles
        const allPromos = [];
        promocionesGrupos.forEach(g=>g.promociones.forEach(p=>allPromos.push({grupo:g.grupo, ...p})));
        const options = allPromos.map(p=>`<option value="${p.nombre}">${p.nombre} — ${p.grupo} (${p.dia})</option>`).join('');
        content.innerHTML = `
            <h2 style="margin:0 0 10px;">Pedir promoción</h2>
            <div class="form-group">
                <label for="promo-select">Selecciona una promoción:</label>
                <select id="promo-select">${options}</select>
            </div>
            <form id="form-pedir-promocion" style="margin-top:12px;">
                <div class="form-group">
                    <label for="habitacion-select">Habitación:</label>
                    <select id="habitacion-select" required>
                        <option value="">Cargando...</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="cantidad-promo">Cantidad:</label>
                    <input type="number" id="cantidad-promo" name="cantidad-promo" min="1" required value="1" />
                </div>
                <div style="text-align:center; margin-top:12px;">
                    <button type="submit" class="btn completar">Confirmar Pedido</button>
                </div>
            </form>
            <div id="promo-confirmacion-msg" style="margin-top:12px;color:#22c55e;text-align:center;display:none;"></div>
        `;
        // Cargar habitaciones en el select
        const selHab = content.querySelector('#habitacion-select');
        cargarHabitacionesEnSelect(selHab);
    } else {
        const imgSrc = window.promoImages && window.promoImages[promo.nombre] ? window.promoImages[promo.nombre] : '';
        content.innerHTML = `
            <div style="display:flex; align-items:center; gap:22px;">
                ${imgSrc ? `<img src="${imgSrc}" alt="${promo.nombre}" style="width:50px;height:50px;">` : ""}
                <div>
                    <h2 style="margin-bottom:6px;">${promo.nombre}</h2>
                    <div style="color:#64748b; font-size:1.01rem; margin-bottom:8px;">${promo.desc}</div>
                    <div style="color:#16a34a; font-weight:500;">${promo.happyHour}</div>
                    <div style="color:#2563eb; margin-top:6px;">Promoción de <b>${promo.dia}</b></div>
                </div>
            </div>
            <form id="form-pedir-promocion" style="margin-top:24px;">
                <div class="form-group">
                    <label for="habitacion-select">Habitación:</label>
                    <select id="habitacion-select" required>
                        <option value="">Cargando...</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="cantidad-promo">Cantidad:</label>
                    <input type="number" id="cantidad-promo" name="cantidad-promo" min="1" required value="1" />
                </div>
                <div style="text-align:center; margin-top:18px;">
                    <button type="submit" class="btn completar">Confirmar Pedido</button>
                </div>
            </form>
            <div id="promo-confirmacion-msg" style="margin-top:18px;color:#22c55e;text-align:center;display:none;"></div>
        `;
        // Cargar habitaciones en el select
        const selHab = content.querySelector('#habitacion-select');
        cargarHabitacionesEnSelect(selHab);
    }
    modal.style.display = 'flex';

    // Cerrar modal
    modal.querySelector('#close-modal-pedir-promocion').onclick = function() {
        modal.style.display = 'none';
    };
    modal.onclick = function(e) {
        if (e.target === modal) modal.style.display = 'none';
    };

    // Manejar envío
    content.querySelector('#form-pedir-promocion').onsubmit = async function(e) {
        e.preventDefault();
        // Obtener promo seleccionada si no se pasó una fija
        let selPromo = promo;
        if(!selPromo){
            const nombreSel = content.querySelector('#promo-select')?.value;
            if(nombreSel){
                for(const g of promocionesGrupos){
                    const found = g.promociones.find(p=>p.nombre===nombreSel);
                    if(found){ selPromo = found; break; }
                }
            }
        }
        // Validar habitación
        const habSel = content.querySelector('#habitacion-select');
        const habId = habSel ? habSel.value : '';
        const habText = habSel ? (habSel.options[habSel.selectedIndex]?.text || '') : '';
        if(!habId){ return; }
        const cantidad = parseInt(content.querySelector('#cantidad-promo').value||'1',10);
        const promoNombre = selPromo ? selPromo.nombre : 'Promoción seleccionada';
        // Resolver producto
        const prodId = await findProductoIdForPromo(promoNombre);
        if(!prodId){
            content.querySelector('#promo-confirmacion-msg').innerHTML = `No se pudo encontrar un producto para la promoción "${promoNombre}". Configura el mapeo.`;
            content.querySelector('#promo-confirmacion-msg').style.display = 'block';
            return;
        }
        const mult = (PROMO_KEYWORDS[promoNombre]?.multiplier)||1;
        const cantFinal = Math.max(1, cantidad*mult);
        // Crear pedido real (camarote)
        try{
            const payload = {
                tipo_consumo: 'camarote',
                habitacion_id: parseInt(habId,10),
                productos: [{ producto_id: prodId, cantidad: cantFinal }],
                nota: `Promoción: ${promoNombre}`
            };
            const res = await fetch('/bar/crear-pedido/', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload) });
            const data = await res.json();
            if(data && data.success){
                const pid = data.pedido?.id;
                content.querySelector('#promo-confirmacion-msg').innerHTML = `¡Pedido #${pid||''} creado!<br>Habitación: <b>${habText}</b><br>Cantidad: <b>${cantFinal}</b><br>Promoción: <b>${promoNombre}</b>`;
                content.querySelector('#promo-confirmacion-msg').style.display = 'block';
                content.querySelector('#form-pedir-promocion').style.display = 'none';
                // Navegar a Pedidos para verlo
                try{ window.location.hash = '#pedidos'; }catch(_e){}
                // Refrescar listados de pedidos si el módulo está cargado
                try{ window.BaresPedidos && window.BaresPedidos.refresh && window.BaresPedidos.refresh(); }catch(_e){}
                // Cerrar modal tras breve delay
                setTimeout(()=>{ try{ document.getElementById('close-modal-pedir-promocion')?.click(); }catch(_e){} }, 600);
            }else{
                content.querySelector('#promo-confirmacion-msg').innerHTML = `No se pudo crear el pedido: ${data?.error||'Error'}`;
                content.querySelector('#promo-confirmacion-msg').style.display = 'block';
            }
        }catch(err){
            content.querySelector('#promo-confirmacion-msg').innerHTML = `No se pudo crear el pedido.`;
            content.querySelector('#promo-confirmacion-msg').style.display = 'block';
        }
    };
}

// AGREGADO: función para pedir la promoción del día
function pedirPromocion(promo) {
    mostrarModalPedirPromocion(promo);
}

function renderPromocionDiaActual() {
    // Buscar la primera promoción del día actual en cualquier grupo
    const dias = ['Domingo','Lunes','Martes','Miércoles','Jueves','Viernes','Sábado'];
    const hoy = new Date();
    const diaActual = dias[hoy.getDay()];

    let promoActual = null;
    let grupoActual = '';
    for (const grupo of promocionesGrupos) {
        promoActual = grupo.promociones.find(p => p.dia === diaActual);
        if (promoActual) {
            grupoActual = grupo.grupo;
            break;
        }
    }

    const cont = document.getElementById('promocion-dia-actual');
    if (!cont) return;
    if (promoActual) {
        // Imagen por nombre de la promoción
        const imgSrc = window.promoImages && window.promoImages[promoActual.nombre] ? window.promoImages[promoActual.nombre] : '';
        cont.innerHTML = `
            <img src="${imgSrc}" alt="${promoActual.nombre}" class="promo-dia-img">
            <div class="promo-dia-info">
                <div class="promo-dia-nombre">${promoActual.nombre}</div>
                <div style="font-size:1rem; color:#64748b; text-align:left; margin-bottom:4px;"><b>${grupoActual}</b></div>
                <div class="promo-desc">${promoActual.desc}</div>
                <div class="promo-happy-hour">Hora Feliz (Happy Hour): ${promoActual.happyHour}</div>
                <div class="promo-dia-subtitulo" style="font-size:0.98em; color:#2563eb; text-align:left; margin-top:8px;">${promoActual.dia}</div>
                <button class="btn completar" id="btn-pedir-promocion-dia" style="margin-top:14px;">
                    Pedir promoción
                </button>
            </div>
        `;
        // AGREGADO: evento al botón "Pedir promoción"
        setTimeout(() => {
            const btn = document.getElementById('btn-pedir-promocion-dia');
            if (btn) {
                btn.onclick = function() {
                    pedirPromocion(promoActual);
                };
            }
        }, 10);

    } else {
        // Sin promo del día: mostrar CTA para pedir cualquiera
        cont.innerHTML = `
            <div style="display:flex; align-items:center; gap:16px;">
                <div style="font-weight:700; color:#1e293b;">Promociones</div>
                <div style="color:#64748b;">No hay promoción especial para hoy.</div>
            </div>
            <button class="btn completar" id="btn-pedir-promocion-dia" style="margin-top:10px;">
                Pedir promoción
            </button>
        `;
    }
}

function renderPromocionesLista() {
    const lista = document.getElementById('lista-promociones');
    if (!lista) return;
    lista.innerHTML = '';

    for (const grupo of promocionesGrupos) {
        // Subtítulo del grupo
        lista.innerHTML += `
            <li style="background:none; box-shadow:none; margin-bottom:0; padding:0;">
                <h3 style="text-align:center; font-weight:700; color:#1e293b; margin-bottom:10px; margin-top:24px;">${grupo.grupo}</h3>
            </li>
        `;

        // Subtítulos de días para cada grupo
        lista.innerHTML += `
            <li style="background:none; box-shadow:none; margin-bottom:0; padding:0;">
                <div style="text-align:center; font-weight:600; font-size:0.97em; color:#2563eb; margin-bottom:12px;">
                    ${grupo.promociones.map(p => p.dia).join(' &ndash; ')}
                </div>
            </li>
        `;

        // Promociones del grupo
        grupo.promociones.forEach(promo => {
            const imgSrc = window.promoImages && window.promoImages[promo.nombre] ? window.promoImages[promo.nombre] : '';
            const dias = ['Domingo','Lunes','Martes','Miércoles','Jueves','Viernes','Sábado'];
            const hoy = new Date();
            const diaActual = dias[hoy.getDay()];
            // Siempre mostrar botón para permitir pedir cualquier promoción
            let pedirBtn = `<button class="btn completar btn-pedir-promocion-lista" data-nombre="${promo.nombre}" style="margin-top:10px;">Pedir promoción</button>`;
            lista.innerHTML += `
                <li>
                    <img src="${imgSrc}" alt="${promo.nombre}" class="promo-list-img">
                    <div class="promo-list-info">
                        <div class="promo-nombre">${promo.nombre}</div>
                        <div class="promo-desc">${promo.desc}</div>
                        <div class="promo-happy-hour">Hora Feliz (Happy Hour): ${promo.happyHour}</div>
                        <div class="promo-grupo" style="font-size:0.96em; color:#2563eb; margin-top:6px;">${promo.dia}</div>
                        ${pedirBtn}
                    </div>
                </li>
            `;
        });
    }
}

document.addEventListener('DOMContentLoaded', function() {
    // Permite que promoImages esté en window para uso en modales
    if (typeof promoImages !== "undefined") window.promoImages = promoImages;
    renderPromocionDiaActual();
    renderPromocionesLista();

    document.getElementById('lista-promociones')?.addEventListener('click', function(e) {
        if (e.target.classList.contains('btn-pedir-promocion-lista')) {
            const nombre = e.target.getAttribute('data-nombre');
            // Buscar promo por nombre
            let promo = null;
            for (const grupo of promocionesGrupos) {
                promo = grupo.promociones.find(p => p.nombre === nombre);
                if (promo) break;
            }
            if (promo) pedirPromocion(promo);
        }
    });

    // AGREGADO: evento para el botón del día actual (en el mismo menú)
    document.getElementById('promocion-dia-actual')?.addEventListener('click', function(e) {
        if (e.target.id === 'btn-pedir-promocion-dia') {
            // Busca la promo del día actual
            const dias = ['Domingo','Lunes','Martes','Miércoles','Jueves','Viernes','Sábado'];
            const hoy = new Date();
            const diaActual = dias[hoy.getDay()];
            let promoActual = null;
            for (const grupo of promocionesGrupos) {
                promoActual = grupo.promociones.find(p => p.dia === diaActual);
                if (promoActual) break;
            }
            if (promoActual) pedirPromocion(promoActual);
        }
    });
});