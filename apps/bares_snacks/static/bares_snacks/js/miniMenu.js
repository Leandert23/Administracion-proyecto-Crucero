// Mini menú navegación robusto (maneja secciones faltantes y hash directo)
document.addEventListener('DOMContentLoaded', () => {
    const links = Array.from(document.querySelectorAll('.mini-menu-icon'));
        const entries = links.map(link => {
        const hash = link.getAttribute('href') || '';
        const id = hash.startsWith('#') ? hash.slice(1) : null;
        if(!id) return null;
        const section = document.getElementById(id);
        return section ? { link, id, section } : null;
    }).filter(Boolean);

    function hideAll(){ entries.forEach(e => { e.section.style.display='none'; e.link.classList.remove('active'); }); }
        function activate(id){
        const target = entries.find(e=>e.id===id) || entries[0];
        if(!target) return;
        hideAll();
        target.section.style.display='block';
        target.link.classList.add('active');
        try { localStorage.setItem('menuSectionId', target.id); } catch(_){}
        if(window.location.hash !== '#'+target.id) history.replaceState(null,'','#'+target.id);
    }

    // Estado inicial
    let startId = null;
    if(window.location.hash){ startId = window.location.hash.slice(1); }
    if(!startId){
        try { const saved = localStorage.getItem('menuSectionId'); if(saved) startId = saved; } catch(_){}
    }
    if(!startId && entries[0]) startId = entries[0].id;
    hideAll();
    if(startId) activate(startId);

    // Clicks
    entries.forEach(e => {
        e.link.addEventListener('click', ev => {
            ev.preventDefault();
            activate(e.id);
        });
    });

    // Navegación por cambio manual del hash
    window.addEventListener('hashchange', () => {
        const id = window.location.hash.slice(1);
        if(id) activate(id);
    });
});