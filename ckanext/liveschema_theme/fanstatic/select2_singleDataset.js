// In your Javascript (external .js resource or <script> tag)
$(document).ready(function() {
    $('#select2').select2({
        placeholder: 'Select the Dataset',
        width: 'resolve',
        templateResult: function (data, container) {
            if (data.element) {
                $(container).addClass($(data.element).attr("class"));
            }
            return data.text;
        }
    });

});
