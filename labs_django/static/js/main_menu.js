/*************/
/* Main menu */
/*************/

$(function() {
    var visible = false;
    $("#header_menu").click( function() {
        if (visible) {
            $("#main_menu").hide();
            visible = false;
        } else {
            $("#main_menu").show();
            visible = true;
        };
    });

    $("#main_menu").mouseleave( function() {
         setTimeout(function(){ 
             if (!( $("#main_menu:hover").length )) {
                $("#main_menu").hide();
                visible = false;
             };
         }, 2000);
    });
});

