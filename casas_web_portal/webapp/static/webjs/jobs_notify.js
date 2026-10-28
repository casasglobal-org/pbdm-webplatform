(function () {
    "use strict";

    var box = document.getElementById("jobNotify");
    if (!box) {
        return;
    }
    var list = document.getElementById("jobNotifyList");
    var closeButton = document.getElementById("jobNotifyClose");
    var userId = parseInt(box.dataset.userId, 10);
    var message = box.dataset.template || "Job {name} has finished, click to see the results";
    var knownKey = "casasKnownJobs";
    var pendingKey = "casasPendingJobs";
    var pollInterval = 15000;

    function load(key) {
        try {
            var value = JSON.parse(window.localStorage.getItem(key));
            return Array.isArray(value) ? value : null;
        } catch (err) {
            return null;
        }
    }

    function save(key, value) {
        try {
            window.localStorage.setItem(key, JSON.stringify(value));
        } catch (err) {
            /* localStorage not available */
        }
    }

    var known = load(knownKey);
    var pending = load(pendingKey) || [];
    var firstRun = known === null;
    if (firstRun) {
        known = [];
    }

    function announce(jobs) {
        jobs.forEach(function (job) {
            var line = document.createElement("div");
            var link = document.createElement("a");
            link.href = "/job/" + encodeURIComponent(job.id);
            link.className = "alert-link";
            link.textContent = message.replace("{name}", job.name);
            line.appendChild(link);
            list.appendChild(line);
        });
        box.classList.remove("d-none");
    }

    closeButton.addEventListener("click", function () {
        box.classList.add("d-none");
        list.innerHTML = "";
    });

    function poll() {
        window
            .fetch("/api/v1/jobs/", { headers: { Accept: "application/json" } })
            .then(function (response) {
                if (response.status === 401 || response.status === 403) {
                    return null;
                }
                if (!response.ok) {
                    throw new Error("HTTP " + response.status);
                }
                return response.json();
            })
            .then(function (jobs) {
                if (!jobs) {
                    return;
                }
                var finished = [];
                var current = [];
                var nextPending = [];
                jobs.forEach(function (job) {
                    if (parseInt(job.user, 10) !== userId) {
                        return;
                    }
                    current.push(job.id);
                    var wasKnown = known.indexOf(job.id) !== -1;
                    var wasPending = pending.indexOf(job.id) !== -1;
                    if (job.ended) {
                        if (!firstRun && (!wasKnown || wasPending)) {
                            finished.push(job);
                        }
                    } else if (job.started) {
                        nextPending.push(job.id);
                    }
                });
                known = current;
                pending = nextPending;
                firstRun = false;
                save(knownKey, known);
                save(pendingKey, pending);
                if (finished.length) {
                    announce(finished);
                }
            })
            .catch(function (err) {
                console.log("Job notification error: " + err);
            })
            .then(function () {
                window.setTimeout(poll, pollInterval);
            });
    }

    poll();
})();
