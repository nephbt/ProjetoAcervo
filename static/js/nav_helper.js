// Apenas mostra badge de admin se logado como admin
(function() {
    document.addEventListener('DOMContentLoaded', function() {
        const token = localStorage.getItem('token');

        if (!token) return;

        try {
            const payload = JSON.parse(atob(token.split('.')[1]));

            // Verificar se o token expirou
            const agora = Math.floor(Date.now() / 1000);
            if (payload.exp && payload.exp < agora) {
                localStorage.removeItem('token');
                return;
            }

            // Se for admin, mostrar badge
            if (payload.role === 'admin') {
                const nav = document.querySelector('nav');
                if (nav && !document.querySelector('.admin-badge')) {
                    const badge = document.createElement('span');
                    badge.className = 'admin-badge';
                    badge.textContent = '🛡️ Admin';
                    badge.style.cssText = 'background: #e74c3c; color: white; padding: 5px 10px; border-radius: 5px; font-size: 0.8em; margin-left: 10px;';
                    nav.appendChild(badge);
                }
            }

        } catch (e) {
            localStorage.removeItem('token');
        }
    });
})();