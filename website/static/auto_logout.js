const TIME_DURATION = 30000; // 30 SECS (1000 ms = 1 second)
let logoutTimer;

function startLogoutTimer() {
    clearTimeout(logoutTimer);
    logoutTimer = setTimeout(showLogoutAlert, TIME_DURATION);
}

function showLogoutAlert() {
    if (confirm("You have been inactive for " + TIME_DURATION/1000 + " seconds. Would you like to logout of your account?")) {
        logoutUser(); 
    } else {
        startLogoutTimer();;
    }
}

function resetLogoutTimer() {
    startLogoutTimer();
}

function logoutUser() {
    window.location.href = "/logout";
}

document.addEventListener("mousemove", resetLogoutTimer);
document.addEventListener("keypress", resetLogoutTimer);
startLogoutTimer();
