/*************/
/* Main menu */
/*************/

$(function() {
    var visible = false;
    $("#header_menu").click( function() {
        if (visible) {
            $("#main_menu").hide();
            $("#menu_back").hide();
            visible = false;
        } else {
            $("#main_menu").show();
            $("#menu_back").show();
            visible = true;
        };
    });

    $("#menu_back").click( function() {
        $("#main_menu").hide();
        $("#menu_back").hide();
        visible = false;
    });

    $("#main_menu").mouseleave( function() {
        setTimeout(function(){
            if (!( $("#main_menu:hover").length )) {
                $("#main_menu").hide();
                $("#menu_back").hide();
                visible = false;
            };
        }, 2000);
    });

});
