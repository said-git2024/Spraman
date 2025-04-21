document.getElementById("startButton").addEventListener("click", function() {
    fetch("/start_model", { method: "POST" })
    .then(response => response.json())
    .then(data => {
        document.getElementById("timer").textContent = "Time left: 15s";
        let timeLeft = 15;
        let countdown = setInterval(() => {
            timeLeft--;
            document.getElementById("timer").textContent = "Time left: " + timeLeft + "s";
            if (timeLeft <= 0) {
                clearInterval(countdown);
                fetch("/check_liveness")
                .then(response => response.json())
                .then(data => {
                    document.getElementById("result").textContent = data.status;
                    fetch("/stop_model", { method: "POST" });
                });
            }
        }, 1000);
    });
});
