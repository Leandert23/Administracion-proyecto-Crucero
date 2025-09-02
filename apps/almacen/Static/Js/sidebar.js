(function(){
    const GestorBarraLateral = {
        barra: null,
        overlay: null,
        botonMovil: null,
        init(){
            this.barra = document.querySelector('.sidebar');
            this.overlay = document.querySelector('.sidebar-overlay');
            this.botonMovil = document.querySelector('.mobile-menu-toggle');
        },
        toggleSidebar(){ if(this.barra){ this.barra.classList.toggle('collapsed'); } },
        toggleMobileSidebar(){
            if(!this.barra||!this.overlay||!this.botonMovil) return;
            this.barra.classList.toggle('open');
            this.overlay.classList.toggle('active');
            this.botonMovil.classList.toggle('active');
        },
        closeMobileSidebar(){
            if(!this.barra||!this.overlay||!this.botonMovil) return;
            this.barra.classList.remove('open');
            this.overlay.classList.remove('active');
            this.botonMovil.classList.remove('active');
        }
    };

    // Inicializar cuando el DOM esté listo
    document.addEventListener('DOMContentLoaded', ()=> GestorBarraLateral.init());

    // Funciones globales que el HTML ya usa
    window.toggleSidebar = () => GestorBarraLateral.toggleSidebar();
    window.toggleMobileSidebar = () => GestorBarraLateral.toggleMobileSidebar();
    window.closeMobileSidebar = () => GestorBarraLateral.closeMobileSidebar();

    // Exponer objeto por si se necesita directamente
    window.GestorBarraLateral = GestorBarraLateral;
})();
