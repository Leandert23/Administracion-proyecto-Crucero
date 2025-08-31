// Mini menú navegación
document.addEventListener('DOMContentLoaded', function() {
    const menuIcons = document.querySelectorAll('.mini-menu-icon');
    const sections = [
        document.getElementById('ordenes'),
        document.getElementById('pedidos'),
        document.getElementById('menu'),
        document.getElementById('promociones'),
        document.getElementById('analisis')
    ];

    menuIcons.forEach((icon, idx) => {
        icon.addEventListener('click', function(e) {
            e.preventDefault();
            menuIcons.forEach(i => i.classList.remove('active'));
            icon.classList.add('active');
            sections.forEach(s => s.style.display = 'none');
            sections[idx].style.display = 'block';
        });
    });

    // Inicialmente mostrar solo Órdenes
    sections.forEach((s, i) => {
        s.style.display = i === 0 ? 'block' : 'none';
    });
});