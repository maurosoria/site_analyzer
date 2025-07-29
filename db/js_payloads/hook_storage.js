(() => {
    return {
        localStorage: Object.entries(localStorage),
        sessionStorage: Object.entries(sessionStorage)
    };
})();