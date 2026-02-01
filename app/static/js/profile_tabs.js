/**
 * Profile Tabs Navigation
 * Handles switching between 'Actividad', 'Información', and 'Seguridad' panels.
 */
document.addEventListener('DOMContentLoaded', function () {
    const tabs = document.querySelectorAll('.tab-btn');
    const panels = document.querySelectorAll('.tab-panel');

    if (tabs.length === 0) return;

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const target = tab.getAttribute('data-tab-target');

            // 1. Reset all tabs
            tabs.forEach(t => {
                t.classList.remove('active', 'border-foreground/30', 'text-foreground');
                t.classList.add('border-transparent', 'text-muted-foreground');
                t.removeAttribute('aria-current');
            });

            // 2. Activate selected tab
            tab.classList.add('active', 'border-foreground/30', 'text-foreground');
            tab.classList.remove('border-transparent', 'text-muted-foreground');
            tab.setAttribute('aria-current', 'page');

            // 3. Switch panels
            panels.forEach(p => p.classList.add('hidden'));
            const activePanel = document.getElementById(`tab-${target}`);
            if (activePanel) {
                activePanel.classList.remove('hidden');
            }
        });
    });
});
