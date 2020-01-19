// Task update notifier

$(document).ready(function() {
    var runningTasks = [] // array of (id, url) tuples
    $("#user-history > tbody > tr").each(function() {
        if ($(this).hasClass("task-not-ready")) {
            runningTasks.push({
                "id": $(this).find("th").text(),
                // the first column is the tool name. Anchor contains the link
                // to it.
                "url": $(this).find("td").children().first().attr("href")
            })
        }
    });
    if (runningTasks.length > 0) {
        waitForUpdateAlert(runningTasks)
    }
})

function waitForUpdateAlert(runningTasks) {
    alertBox = $("#alert-box")
    alertBox.addClass("alert alert-warning")
    alertBox.text("Some tasks are not yet ready. Current status:");
    runningTasks.forEach(task => {
        alertBox.append(
            "<div id='" + task.id + "'><b>" + task.id + "</b>: Waiting for an update...</div>"
        )
        updateTaskStatus(task, alertBox)
    });
}

function updateTaskStatus(task, alertBox) {
    status_url = "/tasks/status/" + task.url + "/" + task.id

    $.getJSON(status_url, function (data) {
        percent = parseInt(data['current'] * 100 / data['total']);
        console.log(data)
        alertBox.find("#" + task.id).html(
            "<b>" + task.id + "</b>: " + data['progressbar_message'] + " (" + percent + "%)"
        )

        if (data['state'] == 'SUCCESS') {
            alertBox.find("#" + task.id).html(
                "<b>" + task.id + "</b>: Task completed sucessfully. Please refresh this page to see the results..."
            )
        }
        else if  (data['state'] == 'FAILURE') {
            alertBox.find("#" + task.id).html(
                "<b>" + task.id + "</b>: Task failed. Please refresh this page to see the details..."
            )
        } 
        else if  (data['state'] == 'PENDING') {
            alertBox.find("#" + task.id).html(
                "<b>" + task.id + "</b>: Either there has been an error with the ID of the task, or it has completed in another window. Please refresh the page..."
            )
        } 
        else {
            // if not success or error rerun task in 2 sec
            setTimeout(function () {
                updateTaskStatus(task, alertBox);
            }, 2000);
        }
    });
};