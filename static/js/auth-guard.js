function requireAuth() {
    const token = localStorage.getItem("accessToken");
    const isGuest = sessionStorage.getItem('guestMode') === 'true';

    // If the user is a guest, allow them to proceed.
    if (isGuest) {
        console.log("Guest mode active. Access granted.");
        return; 
    }

    // If not a guest and there's no token, redirect to login.
    if (!token) {
        window.location.href = "/login/";
        return;
    }

    // If there is a token, validate its expiration.
    try {
        const [, payload] = token.split('.');
        const decoded = JSON.parse(atob(payload));
        const now = Date.now() / 1000;
        if (decoded.exp < now) {
            // Token is expired, clear it and redirect.
            localStorage.removeItem("accessToken");
            sessionStorage.removeItem('guestMode'); // Also clear guest mode just in case
            window.location.href = "/login/";
        }
    } catch (e) {
        // Invalid token format, clear it and redirect.
        localStorage.removeItem("accessToken");
        sessionStorage.removeItem('guestMode');
        window.location.href = "/login/";
    }
}