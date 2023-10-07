setInterval(function() {
    var timeLeft = document.getElementById("time_left");
    timeLeft.textContent = parseInt(timeLeft.textContent) - 1;
    if (parseInt(timeLeft.textContent) <= 0) {
        location.reload()
    };
}, 1000);