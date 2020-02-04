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
    alertBox.addClass("alert alert-light")
    alertBox.text("Some tasks are not yet ready. Current status:");
    runningTasks.forEach(task => {
        alertBox.append(
            "<div id='" + task.id + "' class='alert alert-warning'><b>" + task.id + "</b>: Waiting for an" +
            " update...</div>"
        )
        updateTaskStatus(task, alertBox)
    });
}

function updateTaskStatus(task, alertBox) {
    status_url = "/tasks/status/" + task.url + "/" + task.id

    $.getJSON(status_url, function (data) {
        percent = parseInt(data['current'] * 100 / data['total']);
        alertBox.find("#" + task.id).html(
            "<b>" + task.id + "</b>: " + data['progressbar_message'] + " (" + percent + "%)"
        )

        if (data['state'] == 'SUCCESS') {
            alertBox.find("#" + task.id).html(
                "<b>" + task.id + "</b>: Task completed sucessfully. Please refresh this page to see the results..."
            )

            alertBox.find("#" + task.id).switchClass("alert-warning", "alert-success", 500)
        }
        else if  (data['state'] == 'FAILURE') {
            alertBox.find("#" + task.id).html(
                "<b>" + task.id + "</b>: Task failed. Please refresh this page to see the details..."
            )
            alertBox.find("#" + task.id).switchClass("alert-warning", "alert-danger", 500)
        } 
        else if  (data['state'] == 'PENDING') {
            alertBox.find("#" + task.id).html(
                "<b>" + task.id + "</b>: Either there has been an error with the ID of the task, or it has completed in another window. Please refresh the page..."
            )
            alertBox.find("#" + task.id).switchClass("alert-warning", "alert-danger", 500)
        } 
        else {
            // if not success or error rerun task in 2 sec
            setTimeout(function () {
                updateTaskStatus(task, alertBox);
            }, 2000);
        }
    });
};

// search behaviour
$(document).ready(function() {
    let searchParams = new URLSearchParams(window.location.search)
    console.log(searchParams)
})

$('#history-search-form, div').submit(function () {
    $(this)
        .find('input[name]')
        .filter(function () {
            return !this.value;
        })
        .prop('name', '');
    
});