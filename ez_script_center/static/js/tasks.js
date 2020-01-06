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
    Array.prototype.filter.call(forms, function (form) {
        if (form.checkValidity() === false) {
            event.preventDefault();
            event.stopPropagation();
            form.classList.add('was-validated');
            form_valid = false;
        }
    });
    return form_valid;
};

function jsonDisplay(json_obj, target_div, is_link = false) {
    if (json_obj == null) {
        return;
    }

    list = $('<ul></ul>')
    target_div.append(list);

    if (is_link) {
        for (var filename in json_obj) {
            var link = json_obj[filename];
            var text = $("<li><a href='" + link + "'>" + filename + "</a></li>");

            $(list).append(text);
        }

    } else {
        for (var field_name in json_obj) {
            var content = json_obj[field_name]
            var text = $("<li>" + content + "</li>")

            $(list).append(text)
        }
    }
}

function listResults(data, target_div, show_input = false, show_error = false) {
    // abstract this to a helper function to reduce copy code.
    if (show_input) {
        input_files_div = $('<div id="input_files"><b>Input files:</b></div>')
        input_info_div = $('<div id="input_info"><b>Input info:</b></div>')

        $(target_div).after(result_files_div)
        $(target_div).after(result_info_div)

        input_files = data["input_files"]
        jsonDisplay(input_files, input_files_div, true)

        input_info = data["input_info"]
        jsonDisplay(input_info, input_info_div, false)
    }

    result_files_div = $('<div id="result_files"><b>Result files:</b></div>')
    result_info_div = $('<div id="result_info"><b>Result info:</b></div>')

    $(target_div).after(result_files_div)
    $(target_div).after(result_info_div)

    result_files = data["result_files"]
    jsonDisplay(result_files, result_files_div, true)

    result_info = data["result_info"]
    jsonDisplay(result_info, result_info_div, false)

    // Add showing errors
}

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
        success: function (data, status, request) {
            status_url = request.getResponseHeader('task_status_url');
            update_progress(status_url, progress_bar_inside, progress_bar_outside);
        },
        error: function () {
            alert('Unexpected error');
        }
    });
}

function update_progress(status_url, progress_bar_inside, progress_bar_outside) {
    // send GET request to status URL
    $.getJSON(status_url, function (data) {
        // update UI
        percent = parseInt(data['current'] * 100 / data['total']);
        progress_bar_inside.attr('aria-valuenow', percent).css('width', percent + "%");
        progress_bar_inside.text(percent + '% ' + data['progressbar_message']);

        if (data['state'] == 'SUCCESS' || data['state'] == 'FAILURE') {
            progress_bar_inside.removeClass("progress-bar-striped progress-bar-animated")

            if (data['state'] == "SUCCESS") {
                progress_bar_inside.addClass("bg-success")

                task_id = status_url.split('/')[status_url.split('/').length - 1]
                $.getJSON(data['result_url'], function (result_data) {
                    listResults(result_data, progress_bar_outside, show_input = false, show_error = false)
                })
            }

            if (data['state'] == "FAILURE") {
                progress_bar_inside.addClass("bg-danger")

                if ('result' in data) {
                    console.error("ERROR: " + data['result'])
                } else {
                    console.error("ERROR: " + data['progressbar_message'])
                }

            }

            progress_bar_inside.text(data['state'] + ': ' + data['progressbar_message']);
        }
        else {
            // rerun in 2 seconds
            setTimeout(function () {
                update_progress(status_url, progress_bar_inside, progress_bar_outside);
            }, 2000);
        }
    });
}