$(document).ready(function () {
    $('.reply-jump').click(function () {
        $("html,body").animate({scrollTop: $("#reply-box,.cont-box").offset().top}, 500)
    });
    //  approval

    $('.form-checkbox').prev('label').css('block', 'inline-block').css('margin-right', '10px').addClass('pull-left').parent().addClass('clearfix')

    function toBottom() {
        $('html,body').animate({ scrollTop: $(document).height() }, 1000)
    }

    // function HideShow() {
    //     $(function(){
    //         $(window).scroll(function(){
    //             if($(window).scrollTop > 100){
    //                 $(".to-top").css('display', '');
    //                 }else{
    //                 $(".to-top").css('display', 'none');
    //                 }
    //         });
    //         $("#gotop").click(function(){
    //             $('body,html').animate({scrollTop:0},1000);
    //         });
    //     });
    // }

    function gotoTop() {
        var x = document.body.scrollTop || document.documentElement.scrollTop;
        var timer = setInterval(function () {
            x = x - 220;
            if (x < 220) {
                x = 0;
                window.scrollTo(x, x);
                clearInterval(timer);
            }
            window.scrollTo(x, x);
        }, 10);
    }

    $('.to-top').click(function () {
        gotoTop()
    });
    $('.to-bottom').click(function () {
        toBottom()
    });
    //if (window.location.pathname === '/forum/'){
    //    $('body').css('overflow', 'hidden');
    //}


    $('#live_close').click(function () {
        $('.modal-box,.modal-live').remove();
        $('body').css('overflow', '')
    })

});




