function loadReport(fileId) {
    const reportDiv = document.querySelector(`#report-${fileId}`);
    if (reportDiv.dataset.loaded !== 'true') {
        const xhr = new XMLHttpRequest();
        xhr.open('GET', `/get_report/${fileId}`, true);
        xhr.onload = function () {
            if (xhr.status === 200) {
                reportDiv.innerHTML = xhr.responseText;
                reportDiv.dataset.loaded = 'true';

            }
        };
        xhr.send();
    } else {
        reportDiv.classList.toggle('show');
    }

}

const showReportButtons = document.querySelectorAll('[data-toggle="collapse"]');
showReportButtons.forEach(button => {
    button.addEventListener('click', () => {
        const fileId = button.parentElement.querySelector('[data-target]').dataset.target.split('-')[1];
        loadReport(fileId);
    });
});

