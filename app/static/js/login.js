(() => {
    'use strict';

    const password = document.getElementById('password');
    const togglePassword = document.getElementById('togglePassword');

    if (togglePassword && password) {
        const icon = togglePassword.querySelector('i');
        togglePassword.addEventListener('click', () => {
            const showPassword = password.type === 'password';
            password.type = showPassword ? 'text' : 'password';
            togglePassword.setAttribute('aria-label', showPassword ? 'Hide password' : 'Show password');
            icon?.classList.toggle('bi-eye-fill', showPassword);
            icon?.classList.toggle('bi-eye-slash-fill', !showPassword);
        });
    }

    const page = document.getElementById('mgmsLogin');
    const intro = document.getElementById('loginIntro');
    const skipButton = document.getElementById('skipIntro');
    const panel = document.getElementById('loginPanel');

    if (!page || !intro || !panel) return;

    let finished = false;
    let introTimer;

    function finishIntro() {
        if (finished) return;
        finished = true;
        window.clearTimeout(introTimer);
        page.classList.remove('login-intro-active');
        page.classList.add('login-intro-complete');
        panel.inert = false;
        intro.inert = true;
        intro.setAttribute('aria-hidden', 'true');
        if (document.activeElement === skipButton) {
            document.getElementById('username')?.focus({ preventScroll: true });
        }
    }

    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (reducedMotion) {
        finishIntro();
    } else {
        panel.inert = true;
        intro.setAttribute('aria-hidden', 'false');
        page.classList.add('login-intro-active');
        const duration = Math.max(2500, Number(page.dataset.introDuration) || 3400);
        introTimer = window.setTimeout(finishIntro, duration);
        skipButton?.addEventListener('click', finishIntro);
    }
})();
