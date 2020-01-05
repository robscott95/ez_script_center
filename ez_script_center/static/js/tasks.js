// Model and form validation handling

var modal = $("#progressModal")

function toggleModal() {
    if (validateForm() === true) {
        modal.modal("show");
        start_long_task();
    }
}

function validateForm() {
    var form_valid = true;
    var forms = document.getElementsByClassName('needs-validation');
    Array.prototype.filter.call(forms, function(form) {
        if (form.checkValidity() === false) {
            event.preventDefault();
            event.stopPropagation();
            form.classList.add('was-validated');
            form_valid = false;
        }
    });
    return form_valid;
};

// AJAX task starter

function start_long_task() {
    // add task status elements
    progress_bar_outside = $('<div class="progress" style="background-color: darkgrey;"></div>');
    $('#progress').append(progress_bar_outside);
    progress_bar_inside = $('<div class="progress-bar progress-bar-striped progress-bar-animated" role="progressbar" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100" style="width: 0%"></div>')
    $(progress_bar_outside).append(progress_bar_inside)
    $(progress_bar_outside).after("<hr>")

    // send ajax POST request to start background job
    $.ajax({
        type: 'POST',
        url: window.location.pathname,
        data: new FormData($('form')[0]),
        cache: false,
        processData: false,
        contentType: false,
        success: function(data, status, request) {
            status_url = request.getResponseHeader('task_status_url');
            update_progress(status_url, progress_bar_inside);
        },
        error: function() {
            alert('Unexpected error');
        }
    });
}

function update_progress(status_url, progress_bar) {
    // send GET request to status URL
    $.getJSON(status_url, function(data) {
        // update UI
        percent = parseInt(data['current'] * 100 / data['total']);
        progress_bar_inside.attr('aria-valuenow', percent).css('width', percent + "%");
        progress_bar_inside.text(percent + '% ' + data['progressbar_message']);
        if (data['state'] == 'SUCCESS' || data['state'] != 'FAILURE') {
            progress_bar_inside.removeClass("progress-bar-striped progress-bar-animated")
            
            if (data['state'] == "SUCCESS") {
                progress_bar_inside.addClass("bg-success")
            }
            
            if (data['state'] == "FAILURE") {
                progress_bar_inside.addClass("bg-danger")
                console.error("ERROR: " + data['progressbar_message'])
            }

            progress_bar_inside.attr('aria-valuenow', 100).css('width', "100%");
            progress_bar_inside.text(data['state'] + ': ' + data['progressbar_message']);

        }
        else {
            // rerun in 2 seconds
            setTimeout(function() {
                update_progress(status_url, progress_bar);
            }, 2000);
        }
    });
}