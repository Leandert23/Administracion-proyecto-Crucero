const promoImages = {
    'Lunes': 'assets/two-mugs.svg',
    'Martes': 'assets/taco.svg',
    'Miércoles': 'assets/beer-mug.svg',
    'Jueves': 'assets/cocktail-glass.svg',
    'Domingo': 'assets/tropical-drinks.svg'
};

const promocionesPorDia = [
    {
        dia: 'Lunes',
        promo: '2x1 en Cervezas',
        desc: 'Ideal para empezar la semana con happy hour extendido.',
        happyHour: 'Descuentos en bebidas y aperitivos de 5pm a 8pm.'
    },
    {
        dia: 'Martes',
        promo: 'Martes de Tacos',
        desc: 'Tacos o nachos a mitad de precio con la compra de una margarita.',
        happyHour: 'Descuentos en bebidas y aperitivos de 5pm a 8pm.'
    },
    {
        dia: 'Miércoles',
        promo: 'Jarra de Cerveza a Precio Especial',
        desc: 'Descuento en jarras de cerveza para grupos.',
        happyHour: 'Descuentos en bebidas y aperitivos de 5pm a 8pm.'
    },
    {
        dia: 'Jueves',
        promo: 'Cócteles a Precio de Happy Hour toda la noche',
        desc: 'Atrae a quienes empiezan el fin de semana temprano.',
        happyHour: 'Descuentos en bebidas y aperitivos de 5pm a 8pm.'
    },
    {
        dia: 'Domingo',
        promo: 'Brunch con Mimosa o Bloody Mary incluido',
        desc: 'Ideal para domingos relajados.',
        happyHour: 'Descuentos en bebidas y aperitivos de 5pm a 8pm.'
    }
];

// Obtén el día actual (en español)
function getDiaSemana() {
    const dias = ['Domingo','Lunes','Martes','Miércoles','Jueves','Viernes','Sábado'];
    const hoy = new Date();
    return dias[hoy.getDay()];
}

function renderPromocionDiaActual() {
    const diaActual = getDiaSemana();
    const promoActual = promocionesPorDia.find(p => p.dia === diaActual);
    const cont = document.getElementById('promocion-dia-actual');
    if (!cont) return;
    if (promoActual) {
        const imgSrc = promoImages[promoActual.dia] ? promoImages[promoActual.dia] : '';
        cont.innerHTML = `
            <img src="${imgSrc}" alt="${promoActual.dia}" class="promo-dia-img">
            <div class="promo-dia-info">
                <div class="promo-dia-nombre">${promoActual.dia}: <span class="promo-dia-desc">${promoActual.promo}</span></div>
                <div class="promo-desc">${promoActual.desc}</div>
                <div class="promo-happy-hour">Hora Feliz (Happy Hour): ${promoActual.happyHour}</div>
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
    promocionesPorDia.forEach(promo => {
        const imgSrc = promoImages[promo.dia] ? promoImages[promo.dia] : '';
        lista.innerHTML += `
            <li>
                <img src="${imgSrc}" alt="${promo.dia}" class="promo-list-img">
                <div class="promo-list-info">
                    <div class="promo-nombre">${promo.dia}: <span class="promo-dia-desc">${promo.promo}</span></div>
                    <div class="promo-desc">${promo.desc}</div>
                    <div class="promo-happy-hour">Hora Feliz (Happy Hour): ${promo.happyHour}</div>
                </div>
            </li>
        `;
    });
}

document.addEventListener('DOMContentLoaded', function() {
    renderPromocionDiaActual();
    renderPromocionesLista();
});