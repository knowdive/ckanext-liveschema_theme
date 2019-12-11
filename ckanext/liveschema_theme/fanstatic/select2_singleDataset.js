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

    $('#select2').on('change', function (evt) {
        var id = $('#select2').select2('data')["id"];
        if ( id != null){
            var btn = id.split(",")[2];
            $('.btn').text(btn);

            if ( btn.includes("First") ){
                $('.btn').removeClass("btn-primary");
                $('.btn').addClass("btn-warning");
            }
            else{
                $('.btn').removeClass("btn-warning");
                $('.btn').addClass("btn-primary");
            }
        }
      });

    var id = $('#select2').select2('data')["id"];
    if ( id != null){
        var btn = id.split(",")[2];
        $('.btn').text(btn);

        if ( btn.includes("First") ){
            $('.btn').removeClass("btn-primary");
            $('.btn').addClass("btn-warning");
        }
        else{
            $('.btn').removeClass("btn-warning");
            $('.btn').addClass("btn-primary");
        }
    }
});
