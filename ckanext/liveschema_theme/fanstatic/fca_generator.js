// In your Javascript (external .js resource or <script> tag)
$(document).ready(function() {
    $('#select2').select2({
        placeholder: 'Select the Dataset',
        allowClear: true,
        width: 'resolve' 
    });
});