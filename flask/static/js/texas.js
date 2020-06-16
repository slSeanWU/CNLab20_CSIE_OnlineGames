var oHistory = $('#history');
var oWin = $('#chat_input');
var raise_input = $('#raise_input');
var oStatus = $('#game_status');
var chatroom = $('#chatroom');
var now_bid = 0;
var my_bid = 0;
var chip = 0;
var hand = [];
var board = [];
var action = false;
var player_id=null;
var player_name=null;
var player_num=0;

if (performance.navigation.type == 1) {
    alert( "This page is reloaded, Disconnected" );
    window.location.replace("main_menu");
}

function add_card(who, card){
    var new_card = $("#example-card").clone();
    new_card.addClass("added");
    new_card.attr("src","static/images/cards/"+card+".png");
    if (who=="dealer")
        new_card.appendTo( "#dealer" );
    else if (who=="player")
        new_card.appendTo( "#player" );
    else
        new_card.appendTo(who);
    new_card.show();       
}

function update_user(user_id, change_class, change_value){
    //title,coins,bid,status
    var id = -1;
    if (user_id==player_id)
        id = "#player_me";
    else
        id = "#player_"+user_id.toString();
    if (change_class=="now"){
        for (var i = 0; i < player_num; i++) {
            if (i.toString()==user_id){
                console.log("SET:"+id);
                $(id).css("background-color","rgba(255,255,0,0.6)");
            }
            else{
                $("#player_"+i.toString()).css("background-color","transparent");
                console.log("SET trans: #player_"+user_id.toString());
            }
            if (user_id!=player_id)
                $("#player_me").css("background-color","transparent");
        }
        
    }
    else{
        if (change_class=="big-blind")
            $(id).find(".big-blind").show();
        else if (change_class=="small-blind")
            $(id).find(".small-blind").show();
        else{
            $(id).find(change_class).html(change_value);
            if (change_class==".status" && change_value!="Active")
                $(id).css("opacity","0.5");
        }
    }
    
}

function add_user(user_id, user_name, is_self){
    var new_user = $("#example_user").clone();
    new_user.attr("id","player_"+user_id.toString());
    if (is_self) {
        console.log("first");
        new_user.children('.player-label').remove();
        new_user.css("background-image","url(static/images/my_player.png)");
    }
    else
        new_user.find(".title").html(user_name);
    new_user.show();
    new_user.appendTo("#player-table");
}




if ("WebSocket" in window){
    console.log("您的瀏覽器支援 WebSocket!");
    var ws = new WebSocket("ws://10.5.0.66:9001");
    ws.onopen = function(){
        console.log("websocket 已連線上");
        //var username = flask['username'];
        player_name = $('#username-store').val();
        ws.send('#NAME ' + player_name);
    }

    ws.onmessage = function (evt) {
        var dataReceive = evt.data;
        console.log(dataReceive);
        if (dataReceive.match("#IO") != null)
            $('#history').val($('#history').val()+dataReceive.substring(4,dataReceive.length)+"\n");
        else if (dataReceive.match("#BID") != null)
        {
            now_bid = parseInt(dataReceive.split(" ")[1]);
            oStatus.val("Board: "+board.toString()+"\n" + "Hand: "+hand.toString()+"\n" + "now bid: "+now_bid+"\n" + "my bid: "+my_bid+"\n" + "chip: "+chip+"\n");
        }
        else if (dataReceive.match("#BLIND") != null)
        {
            chip -= parseInt(dataReceive.split(" ")[1])
            my_bid += parseInt(dataReceive.split(" ")[1])
            oStatus.val("Board: "+board.toString()+"\n" + "Hand: "+hand.toString()+"\n" + "now bid: "+now_bid+"\n" + "my bid: "+my_bid+"\n" + "chip: "+chip+"\n");
        }
        else if (dataReceive.match("#HAND") != null)
        {
            // new game
            hand = []
            board = []
            my_bid = 0
            hand.push(dataReceive.split(" ")[1]);
            hand.push(dataReceive.split(" ")[2]);
            add_card("player",hand[0]);
            add_card("player",hand[1]);
        }
        else if (dataReceive.match("#TURN") != null)
        {
            $('#history').val($('#history').val() + "It's your turn!" + "\n");
            action = true;
            console.log(action);
            oStatus.val("Board: "+board.toString()+"\n" + "Hand: "+hand.toString()+"\n" + "now bid: "+now_bid+"\n" + "my bid: "+my_bid+"\n" + "chip: "+chip+"\n");
            if (chip == 0)
            {
                ws.send("#CHECK");
                action = false;
            }
            console.log(action);
        }
        else if (dataReceive.match("#BOARD") != null)
        {
            if ((dataReceive.split(" ").length - 1) > board.length)
            {
                var b_len = board.length;
                for (i=0; i<(dataReceive.split(" ").length-b_len-1); i++){
                    board.push(dataReceive.split(" ")[dataReceive.split(" ").length-i-1]);
                    console.log(dataReceive.split(" ")[dataReceive.split(" ").length-i-1]);
                    add_card("dealer",dataReceive.split(" ")[dataReceive.split(" ").length-i-1]);
                }
                
            }
        }
        else if (dataReceive.match("#CHIP") != null)
        {
            chip = parseInt(dataReceive.split(" ")[1]);
            oStatus.val("Board: "+board.toString()+"\n" + "Hand: "+hand.toString()+"\n" + "now bid: "+now_bid+"\n" + "my bid: "+my_bid+"\n" + "chip: "+chip+"\n");
            console.log(dataReceive);
            console.log(chip);
        }
        else if (dataReceive.match("#CHAT") != null)
            chatroom.val(dataReceive.substring(5,dataReceive.length)+"\n"+chatroom.val());
        // already-enter-user-names
        else if (dataReceive.match("#ALL_NAME") != null){
            var player_names = dataReceive.split(" ").slice(1);
            // console.log("###");
            console.log(player_names);
            if (player_id==null)
                player_id = player_names.length-1
            console.log(player_id);
            for (var i = player_num; i < player_names.length; i++) {
                if (i==player_id){
                    add_user(i,player_names[i], true);
                    update_user(i, ".title", player_names[i]);
                }
                else
                    add_user(i,player_names[i], false);
            }
            // player_names.length-player_num
            player_num = player_names.length;
        }
        else if (dataReceive.match("#START") != null){
            $("#special-msg").hide();
            alert("Ready to start!");
            
            
            for (var i = 0; i < player_num; i++) {
                if(i.toString()!=player_id){
                    $("#player_"+i.toString()).css("background-color","transparent");
                    $("#player_"+i.toString()).find(".small-blind").hide();
                    $("#player_"+i.toString()).find(".big-blind").hide();
                    $("#player_"+i.toString()).css("opacity","1");
                }
            }
            $("#player_me").css("background-color","transparent");
            $("#player_me").find(".small-blind").hide();
            $("#player_me").find(".big-blind").hide();
            $("#player_me").css("opacity","1");
            $( ".added" ).remove();
            $( ".show_cards" ).hide();
        }
        else if (dataReceive.match("#ALL_STATUS") != null){
            var all_status = dataReceive.split(" ").slice(1);
            console.log(all_status);
            for (var i = 0; i < player_num; i++) 
                if(all_status[i]=="1")
                    update_user(i, ".status", "Active");
                else if (all_status[i] == "0")
                    update_user(i, ".status", "Fold");
                else
                    update_user(i, ".status", "Disconnect");
        }
        else if (dataReceive.match("#ALL_BID") != null){
            var all_bid = dataReceive.split(" ").slice(1);
            for (var i = 0; i < player_num; i++) 
                update_user(i, ".bid", all_bid[i]);
        }
        else if (dataReceive.match("#ALL_MONEY") != null){
            var all_money = dataReceive.split(" ").slice(1);
            for (var i = 0; i < player_num; i++) 
                update_user(i, ".coins", all_money[i]);
        }
        else if (dataReceive.match("#NOW_PLAY") != null){
            var now_play = dataReceive.split(" ")[1];
            update_user(now_play, "now", null);
            console.log("Update now play: "+now_play.toString());
        }
        else if (dataReceive.match("#ALL_BLIND") != null){
            var blind_big_small = dataReceive.split(" ").slice(1);
            update_user(blind_big_small[0], "big-blind", null);
            update_user(blind_big_small[1], "small-blind", null);
        }
        else if (dataReceive.match("#FIN_HAND") != null){
            var fin = dataReceive.split(" ").slice(1);//0 id, 1 name, 2 card, 3 card
            console.log(fin);
            if (fin[0]!=player_id) {
                add_card("#player_"+fin[0]+" > .show_cards", fin[2]);
                add_card("#player_"+fin[0]+" > .show_cards", fin[3]);
                $("#player_"+fin[0]+" > .show_cards").show();    
            }
            
        }
        else if (dataReceive.match("#END") != null){
            alert("Someone left the room");
            window.location.replace("main_menu");
        }
        else if (dataReceive.match("#WIN") != null){
            $("#special-msg").show();
            if(confirm(dataReceive.substring(5,dataReceive.length)+"\n If you're ready to start new game, press OK\nElse press Cancel and leave")==false){
                //leave
                ws.send("#LEAVE");
                window.location.replace("main_menu");
            }
            else{
                //continue
                ws.send("#CONTINUE " + player_name);
                console.log("continue");
            }

        }
    };

    ws.onclose = function() {
        //ws.send("#FOLD");
        console.log("連線已關閉...");
    };

}else{
    // 瀏覽器不支援 WebSocket
    console.log("您的瀏覽器不支援 WebSocket!");
}

function sendMessage(){
    console.log(oWin);
    var dataSend = oWin.val().trim();
    ws.send(dataSend);
    oWin.val('');
}

function call(){
    console.log(action);
    if (action)
    {
        if ((now_bid - my_bid) > chip)
            oHistory.val(oHistory.val() + "You don't have that much money you poor little piece of sh*t 凸-_-凸\n");
        else
        {
            ws.send("#CALL");
            my_bid = now_bid;
            action = false;
        }
    }
    else
        oHistory.val(oHistory.val() + "It's not your turn you little sh*t 凸-_-凸\n");
}

function raise(){
    if (action)
    {
        var raise = raise_input.val().trim();
        if (raise.match("[0-9]") != null)
        {
            if ((parseInt(raise) + now_bid - my_bid) > chip)
                oHistory.val(oHistory.val() + "You don't have that much money you poor little piece of sh*t 凸-_-凸\n");
            else
            {
                ws.send("#RAISE " + raise);
                my_bid = now_bid + parseInt(raise);
                action = false;
            }
        }
        else
            oHistory.val(oHistory.val() + "Enter a number you little sh*t 凸-_-凸\n");
    }
    else
        oHistory.val(oHistory.val() + "It's not your turn you little sh*t 凸-_-凸\n");
    oWin.val('');
}

function fold(){
    if (action)
        ws.send('#FOLD');
    else
        oHistory.val(oHistory.val() + "It's not your turn you little sh*t 凸-_-凸\n");
    action = false;
}

function check(){
    if (action)
    {
        if (my_bid == now_bid)
        {
            ws.send("#CHECK");
            action = false;
        }
        else
            oHistory.val(oHistory.val() + "You can only call, raise, or allin now you little sh*t 凸-_-凸\n");
    }
    else
        oHistory.val(oHistory.val() + "It's not your turn you little sh*t 凸-_-凸\n");
}

function allin(){
    if (action)
    {
        ws.send("#ALLIN");
        my_bid += chip;
        action = false;
    }
    else
        oHistory.val(oHistory.val() + "It's not your turn you little sh*t 凸-_-凸\n");
}

function chat(){
    console.log(oWin);
    ws.send("#CHAT " + oWin.val().trim());
    oWin.val('');
}


$("#chat_send").click(function(){chat()});
