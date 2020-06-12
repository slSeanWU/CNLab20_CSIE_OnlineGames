function add_card(who, card){
    var new_card = $("#example-card").clone();
    var color = ["C","D","H","S"];
    new_card.addClass("added");
    if (card!="X")
        new_card.attr("src","static/images/cards/"+card+color[Math.floor(Math.random() * 4)]+".png");
    else
        new_card.addClass("hidden");
    if (who=="dealer")
        new_card.appendTo( "#dealer" );
    if (who=="player")
        new_card.appendTo( "#player" );
    new_card.show();       
}
$(document).ready(function(){
    namespace = '/blackjack';
    var socket = io(namespace);
    var coins_now = Number($("#coins_store").val());
    var coins_prev = coins_now;
    var username = $("#username_store").val();
    var bet_show = 0;

    socket.on('connect', function(){
        socket.emit('connect_event', {'data': username + ' Connected!'});
    });

    socket.on('start', function(msg){
        coins_prev = coins_now;
        $( ".added" ).remove();
        add_card("player",msg.player[0]);
        add_card("dealer",msg.dealer[0]);
        add_card("player",msg.player[1]);
        add_card("dealer",msg.dealer[1]);
        // document.getElementById("dealer").innerHTML=msg.dealer;
        socket.emit('check_start_status');
        // document.getElementById("log").innerHTML='';
        // $('#log').append('<br>' + $('<div/>').text('Received #: Start a new game.').html());
    });

    socket.on('continue_game', function(){
        $('form#take').find(':input[type=submit]').prop('disabled', false);
        $('form#stop').find(':input[type=submit]').prop('disabled', false);
    });

    socket.on('server_response', function(msg, cb){
        // $('#log').append('<br>' + $('<div/>').text('Received #' + ': ' + msg.data).html());
        // if(cb)
        //     cb();
    });

    socket.on('player_picked', function(msg){
        // $('#log').append('<br>' + $('<div/>').text('Received #: Player drew a card.').html());
        // document.getElementById("player").innerHTML=msg.cards;
        add_card("player",msg.cards[msg.cards.length-1]);
    });

    socket.on('player_bust', function(){
        // $('#log').append('<br>' + $('<div/>').text('Player Bust!').html());
        socket.emit('player_stop');
    });

    socket.on('player_21', function(){
        // $('#log').append('<br>' + $('<div/>').text('Player got 21!').html());
        alert("player 21!");
        socket.emit('player_stop');                
    });

    socket.on('dealer_picked', function(msg){
        //var color = ["C","D","H","S"];
        //$(".hidden").attr("src","static/images/cards/"+msg.cards[0]+color[Math.floor(Math.random() * 4)]+".png");
        for ( var i = 2; i < msg.cards.length; i++ ) {
            add_card("dealer",msg.cards[i]);
        }
        socket.emit('check_result');
    });

    socket.on('finish_game', function(msg){
        bet_show = 0;
        // document.getElementById("show_result").innerHTML= "<h4>Last time: " + msg.res + "</h4>";
        $('form#take').find(':input[type=submit]').prop('disabled', true);
        $('form#stop').find(':input[type=submit]').prop('disabled', true);
        $('form#start').find(':input[type=submit]').prop('disabled', false);
        $('form#start').find(':input[type=number]').prop('disabled', false);
        $('#user_coins').html("Coins: "+coins_now.toString());
        $('#last_earns').html("Last round earnings: "+(coins_now-coins_prev).toString());
        // document.getElementById("head").innerHTML='<h1>CSIE Online Games --- Black Jack</h1><h4>User: '+username+'<br> Coins: '+coins_now+'</h4>'
    });

    socket.on('draw', function(msg){
        var color = ["C","D","H","S"];
        $(".hidden").attr("src","static/images/cards/"+msg.cards[0]+color[Math.floor(Math.random() * 4)]+".png");
        alert('Draw!');
    });

    socket.on('blackjack', function(msg){
        var color = ["C","D","H","S"];
        $(".hidden").attr("src","static/images/cards/"+msg.cards[0]+color[Math.floor(Math.random() * 4)]+".png");
        alert('You Win!\nBlack Jack!');
        coins_now += Math.round(Number(bet_show)*1.5)
    });

    socket.on('player_win', function(msg){
        var color = ["C","D","H","S"];
        $(".hidden").attr("src","static/images/cards/"+msg.cards[0]+color[Math.floor(Math.random() * 4)]+".png");
        alert('You Win!');
        coins_now += Number(bet_show)
    });

    socket.on('dealer_win', function(msg){
        var color = ["C","D","H","S"];
        $(".hidden").attr("src","static/images/cards/"+msg.cards[0]+color[Math.floor(Math.random() * 4)]+".png");
        alert('Dealer Win!');
        coins_now -= Number(bet_show)
    });

    socket.on('bet_able', function(){
        $('form#start').find(':input[type=submit]').prop('disabled', true);
        $('form#start').find(':input[type=number]').prop('disabled', true);
        socket.emit('start_game');
    });

    socket.on('bet_refuse', function(){
        alert('Coins Not Enough!');
        document.getElementById('bet').value = coins_now;
    });

/*
    $('form#emit').submit(function(event){
        socket.emit('client_event', {'data': $('#emit_data').val()});
        return false;
    });

    $('form#disconnect').submit(function(event){
        socket.emit('disconnect_request');
        return false;
    });
*/
    $('form#start').submit(function(event){
        bet_show = $('#bet').val();
        socket.emit('check_bet', {'bet_coin': bet_show})
        //socket.emit('start_game', {'bet_coin': bet_show});
        return false;
    });

    $('form#take').submit(function(event){
        socket.emit('player_take_one');
        return false;
    });

    $('form#stop').submit(function(event){
        socket.emit('player_stop');
        return false;
    });

});