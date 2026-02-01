document.addEventListener('DOMContentLoaded', () => {
    const flashMessages = document.querySelectorAll('[data-flash-message]');

    flashMessages.forEach(message => {
        // Selector del botón de cerrar
        const closeBtn = message.querySelector('[data-flash-close]');

        const removeMessage = () => {
            // Animación de salida (suave desaparición y reducción de altura)
            message.style.opacity = '0';
            message.style.transform = 'scale(0.98)';
            message.style.maxHeight = '0';
            message.style.marginTop = '0';
            message.style.marginBottom = '0';
            message.style.paddingTop = '0';
            message.style.paddingBottom = '0';
            message.style.borderWidth = '0';
            message.style.overflow = 'hidden';

            setTimeout(() => {
                message.remove();
                // Si el contenedor está vacío, también podrías ocultarlo, 
                // pero remove() ya es suficiente para colapsar el espacio.
            }, 300);
        };

        // Evento clic en el botón cerrar
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                removeMessage();
            });
        }

        // Auto-dismiss tras 20 segundos
        setTimeout(() => {
            if (message && message.parentElement) {
                removeMessage();
            }
        }, 20000);
    });
});
