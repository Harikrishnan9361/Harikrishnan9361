document.addEventListener('DOMContentLoaded', function() {
    const modeToggle = document.getElementById('modeToggle');
    const body = document.body;

    // Check for saved theme
    if (localStorage.getItem('theme') === 'light') {
        body.classList.add('light-mode');
        if (modeToggle) {
            modeToggle.checked = true;
        }
    }

    if (modeToggle) {
        modeToggle.addEventListener('change', function() {
            if (this.checked) {
                body.classList.add('light-mode');
                localStorage.setItem('theme', 'light');
            } else {
                body.classList.remove('light-mode');
                localStorage.setItem('theme', 'dark');
            }
        });
    }

    // Smooth scroll animations on load
    if ('IntersectionObserver' in window) {
        const observerOptions = {
            threshold: 0.1
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('fade-in-up');
                }
            });
        }, observerOptions);

        document.querySelectorAll('.glass-card, .category-card, .place-card').forEach(el => {
            el.classList.add('reveal');
            observer.observe(el);
        });
    }
});
