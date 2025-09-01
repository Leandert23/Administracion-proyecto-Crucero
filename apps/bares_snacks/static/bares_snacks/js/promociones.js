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
// Nueva estructura con grupos y días
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
        const imgSrc = promoImages[promoActual.nombre] ? promoImages[promoActual.nombre] : '';
        cont.innerHTML = `
            <img src="${imgSrc}" alt="${promoActual.nombre}" class="promo-dia-img">
            <div class="promo-dia-info">
                <div class="promo-dia-nombre">${promoActual.nombre}</div>
                <div style="font-size:1rem; color:#64748b; text-align:left; margin-bottom:4px;"><b>${grupoActual}</b></div>
                <div class="promo-desc">${promoActual.desc}</div>
                <div class="promo-happy-hour">Hora Feliz (Happy Hour): ${promoActual.happyHour}</div>
                <div class="promo-dia-subtitulo" style="font-size:0.98em; color:#2563eb; text-align:left; margin-top:8px;">${promoActual.dia}</div>
            </div>
        `;
        
    } else {
        cont.innerHTML = `<div style="color:#64748b;">No hay promoción especial para hoy.</div>`;
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
            const imgSrc = promoImages[promo.nombre] ? promoImages[promo.nombre] : '';
              
            lista.innerHTML += `
                <li>
                    <img src="${imgSrc}" alt="${promo.nombre}" class="promo-list-img">
                    <div class="promo-list-info">
                        <div class="promo-nombre">${promo.nombre}</div>
                        <div class="promo-desc">${promo.desc}</div>
                        <div class="promo-happy-hour">Hora Feliz (Happy Hour): ${promo.happyHour}</div>
                        <div class="promo-grupo" style="font-size:0.96em; color:#2563eb; margin-top:6px;">${promo.dia}</div>
                    </div>
                </li>
            `;
        });
    }
}

document.addEventListener('DOMContentLoaded', function() {
    renderPromocionDiaActual();
    renderPromocionesLista();
});