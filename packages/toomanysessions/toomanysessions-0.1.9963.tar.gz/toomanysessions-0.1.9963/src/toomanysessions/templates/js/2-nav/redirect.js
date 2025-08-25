function returnHome() {
    // Add success ripple effect
    const button = event.target;
    const ripple = document.createElement('div');
    ripple.className = 'ripple';

    const rect = button.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    ripple.style.width = ripple.style.height = size + 'px';
    ripple.style.left = (event.clientX - rect.left - size / 2) + 'px';
    ripple.style.top = (event.clientY - rect.top - size / 2) + 'px';

    button.appendChild(ripple);

    setTimeout(() => {
        if (ripple.parentNode) {
            ripple.parentNode.removeChild(ripple);
        }
    }, 600);

    // Navigate with delay for ripple effect
    setTimeout(() => {
        if (window.opener && window.opener !== window) {
            window.opener.location.href = '{{ redirect_url }}';
            window.close();
        } else {
            window.location.href = '{{ redirect_url }}';
        }
    }, 150);
}