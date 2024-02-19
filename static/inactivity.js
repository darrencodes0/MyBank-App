const TIMEOUT_DURATION = 10000; // 10 SECS (1000 ms = 1 second)
let logoutTimer;

function enableLogoutTimer() {
    clearTimeout(logoutTimer);
    logoutTimer = setTimeout(showLogoutAlert, TIMEOUT_DURATION);
}

function logoutUser() {
    window.location.href = "/logout";
}

function showLogoutAlert() {
    if (confirm("You have been inactive for " + TIMEOUT_DURATION/1000 + " seconds. Would you like to logout?")) {
        logoutUser(); 
    } else {
        startLogoutTimer();
    }
}

function resetLogoutTimer() {
    startLogoutTimer();
}

enableLogoutTimer();

// checks for any user mouse or keyboard input 
document.addEventListener("mousemove", resetLogoutTimer);
document.addEventListener("keypress", resetLogoutTimer);
