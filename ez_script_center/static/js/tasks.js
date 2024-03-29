// Model and form validation handling

$("#script-request").keyup(function (event) {
    if (event.keyCode === 13) {
        $("#submit-btn").click();
    }
});

function toggleModal() {
    let submitBtn = $("#submit-btn");
    submitBtn.attr("disabled");
    submitBtn.text('Loading...').prepend(
        '<span class="spinner-grow spinner-grow-sm" role="status" aria-hidden="true" ' +
        'style="vertical-align: baseline; margin-right: 5px;"></span>'
    );

    validateForm();
}

function jsonDisplay(json_obj, target_div, is_link = false, is_error = false) {
    if (json_obj == null) {
        return;
    }

    list = $('<ul></ul>');
    target_div.append(list);

    if (is_link) {
        for (var key in json_obj) {
            let link = json_obj[key][0];
            let filename = json_obj[key][1];
            let name = json_obj[key][2];
            let text = $("<li><b>" + name + ": </b><a href='" + link + "'>" + filename + "</a></li>");

            $(list).append(text);
        }
    } else if (is_error) {
        let content = json_obj;
        let text = $("<li>" + content + "</li>");

        $(list).append(text)
    } else {
        for (var field_name in json_obj) {
            let content = json_obj[field_name];
            let text = $("<li><b>" + field_name + ": </b>" + content + "</li>");

            $(list).append(text)
        }
    }
}

function listResults(data, target_div, show_input = false, show_result = false, show_error = false) {
    function setUpResultSpace(key, title, target_div, data, data_is_files, is_error = false) {
        div = $('<div id=" ' + key + ' "><b>' + title + ':</b></div>');
        $(target_div).after(div);
        data_val = data[key];
        jsonDisplay(data_val, div, data_is_files, is_error)
    }

    if (show_input) {
        setUpResultSpace('input_files', 'Input files', target_div, data, true);
        setUpResultSpace('input_info', 'Input info', target_div, data, false)
    }

    if (show_result) {
        setUpResultSpace('result_files', 'Result files', target_div, data, true);
        setUpResultSpace('result_info', 'Result info', target_div, data, false)
    }

    if (show_error) {
        setUpResultSpace('error', 'Error', target_div, data, false, true)
    }
}

// AJAX task starter
function validateForm() {
    function clearErrors() {
        $('.invalid-feedback').remove();
        $('.form-control, .form-control-file').addClass("is-valid").removeClass("is-invalid")
    }

    function showErrors(data) {
        clearErrors();

        for (let id in data) {
            let invalidFormField = $("#" + id);
            let errorMessage = '<div class=\"invalid-feedback\"> ' + data[id] + '</div>';
            invalidFormField.addClass("is-invalid");
            invalidFormField.parent().append(errorMessage)
        }
}

    let modal = $("#progressModal");
    let submitBtn = $("#submit-btn");

    $.ajax({
        type: 'POST',
        url: window.location.pathname,
        data: new FormData($('form')[0]),
        cache: false,
        processData: false,
        contentType: false,
        success: function (data, status, request) {
            submitBtn.removeAttr("disabled");
            submitBtn.text('Execute script').remove('.spinner-grow')
            // Check if form validation is true.
            let formValidationError = request.getResponseHeader('form_validation_error');
            if (formValidationError === "True") {
                showErrors(data)
            } else {
                clearErrors()
                start_long_task(modal, request)
            }
        },
        error: function () {
            alert('Unexpected error');
        }
    });
}

function start_long_task(modal, request) {
    // add task status elements
    progress_bar_outside = $('<div class="progress" style="background-color: darkgrey;"></div>');
    $('#progress').append(progress_bar_outside);
    progress_bar_inside = $('<div class="progress-bar progress-bar-striped progress-bar-animated" role="progressbar"' +
        ' aria-valuenow="0" aria-valuemin="0" aria-valuemax="100" style="width: 0"></div>');
    $(progress_bar_outside).append(progress_bar_inside);
    $(progress_bar_outside).after("<hr>");

    modal.modal("show");
    let status_url = request.getResponseHeader('task_status_url');
    updateProgress(status_url, progress_bar_inside, progress_bar_outside);
}

function updateProgress(status_url, progress_bar_inside, progress_bar_outside) {
    // send GET request to status URL
    $.getJSON(status_url, function (data) {
        // update UI
        percent = parseInt(data['current'] * 100 / data['total']);
        progress_bar_inside.attr('aria-valuenow', percent).css('width', percent + "%");
        progress_bar_inside.text(percent + '% ' + data['progressbar_message']);

        if (data['state'] == 'SUCCESS' || data['state'] == 'FAILURE') {
            // Let the user know that the update will be shown in a minute.
            progress_bar_inside.removeClass("progress-bar-striped progress-bar-animated");
            progress_bar_inside.text(data['state'] + ': ' + data['progressbar_message']);

            please_wait_message = document.createTextNode('Please wait until the results are shown here below...');
            $(progress_bar_outside).after(please_wait_message);

            if (data['state'] == "SUCCESS") {
                progress_bar_inside.addClass("bg-success");

                $.getJSON(data['result_url'], function (result_data) {
                    please_wait_message.remove();
                    listResults(result_data, progress_bar_outside, false, true, false)
                })
            }

            if (data['state'] == "FAILURE") {
                progress_bar_inside.addClass("bg-danger");

                $.getJSON(data['result_url'], function (result_data) {
                    please_wait_message.remove();
                    listResults(result_data, progress_bar_outside, false, false, true)
                });

                progress_bar_inside.text("ERROR! Check console logs.");

                console.error("ERROR: " + data['result'] + " (task_id: " + status_url.split("/")[4] + ")")

            }
        } else {
            // rerun in 2 seconds
            setTimeout(function () {
                updateProgress(status_url, progress_bar_inside, progress_bar_outside);
            }, 2000);
        }
    });
}