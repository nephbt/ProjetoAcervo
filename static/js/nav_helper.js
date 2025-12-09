(function() {
    document.addEventListener('DOMContentLoaded', function() {
        const token = localStorage.getItem('token');

        // Se não tem token, não faz nada (usuário deslogado)
        if (!token) return;

        try {
            const payload = JSON.parse(atob(token.split('.')[1]));

            // Verificar se o token expirou
            const agora = Math.floor(Date.now() / 1000);
            if (payload.exp && payload.exp < agora) {
                localStorage.removeItem('token');
                return;
            }

            const isAdmin = payload.role === 'admin';
            const homePage = isAdmin ? '/home_page_admin' : '/home_page_usuarios';

            // ✅ Ajustar TODOS os links "Início" para a home correta
            document.querySelectorAll('a').forEach(link => {
                const href = link.getAttribute('href');
                const texto = link.textContent.trim().toLowerCase();

                // Links que devem apontar para a home do usuário logado
                if (href === '/' ||
                    href === '/index' ||
                    href === '/home_page_usuarios' ||
                    href === '/home_page_admin' ||
                    texto === 'início') {
                    link.href = homePage;
                }
            });

            // ✅ Se for admin, mostrar badge
            if (isAdmin) {
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
            console.error('Erro ao verificar role:', e);
        }
    });
})();