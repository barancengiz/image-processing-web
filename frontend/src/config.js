const getApiUrl = () => {
    // Get the current hostname (IP or domain)
    const hostname = window.location.hostname;
    return `http://${hostname}:8000`;
};

export const config = {
    apiUrl: getApiUrl()
};
