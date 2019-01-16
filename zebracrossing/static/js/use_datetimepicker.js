$(document).ready(function () {
    $('.date-input').each(function() {
        $(this).datepicker({
            uiLibrary: 'bootstrap4',
            format: 'yyyy-mm-dd'
        });
    });
});
