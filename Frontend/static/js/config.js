const API_BASE_URL = (() => {
    const hostname = window.location.hostname;
    const port = window.location.port;
    const protocol = window.location.protocol;
    
    // Development environments
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
        return `${protocol}//${hostname}:5000`;
    }
    
    // Staging
    if (hostname === 'staging.yourdomain.com') {
        return 'https://api-staging.yourdomain.com';
    }
    
    // Production
    if (hostname === 'yourdomain.com' || hostname === 'www.yourdomain.com') {
        return 'https://api.yourdomain.com';
    }
    
    // Fallback to relative URLs
    return '';
})();

export { API_BASE_URL };