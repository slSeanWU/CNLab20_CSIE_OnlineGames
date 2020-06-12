function add_card(who, card){
    var new_card = $("#example-card").clone();
    new_card.addClass("added");
    if (card!="X")
        new_card.attr("src","static/images/cards/"+card+"C"+".png");
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
    var username = $("#username_store").val();
    var bet_show = 0;

    socket.on('connect', function(){
        socket.emit('connect_event', {'data': username + ' Connected!'});
    });

    socket.on('start', function(msg){
        $( ".added" ).remove();
        add_card("player",msg.player[0]);
        add_card("dealer",msg.dealer[0]);
        add_card("player",msg.player[1]);
        add_card("dealer",msg.dealer[1]);
        // document.getElementById("dealer").innerHTML=msg.dealer;
        $('form#take').find(':input[type=submit]').prop('disabled', false);
        $('form#stop').find(':input[type=submit]').prop('disabled', false);
        // document.getElementById("log").innerHTML='';
        // $('#log').append('<br>' + $('<div/>').text('Received #: Start a new game.').html());
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
        $(".hidden").attr("src","static/images/cards/"+msg.cards[0]+"C"+".png");
        for ( var i = 2; i < msg.cards.length; i++ ) {
            add_card("dealer",msg.cards[i]);
        }
        
    });

    socket.on('finish_game', function(msg){
        bet_show = 0;
        // document.getElementById("show_result").innerHTML= "<h4>Last time: " + msg.res + "</h4>";
        $('form#take').find(':input[type=submit]').prop('disabled', true);
        $('form#stop').find(':input[type=submit]').prop('disabled', true);
        $('form#start').find(':input[type=submit]').prop('disabled', false);
        $('form#start').find(':input[type=number]').prop('disabled', false);
        $('#user_coins').html("Coins: "+coins_now.toString());
        // document.getElementById("head").innerHTML='<h1>CSIE Online Games --- Black Jack</h1><h4>User: '+username+'<br> Coins: '+coins_now+'</h4>'
    });

    socket.on('draw', function(){
        alert('Draw!');
    });

    socket.on('player_win', function(){
        alert('You Win!')
        coins_now += Number(bet_show)
    });

    socket.on('dealer_win', function(){
        alert('Dealer Win!')
        coins_now -= Number(bet_show)
    });

    socket.on('blackjack', function(){
        alert('You Win!<br>Black Jack!')
        coins_now += Math.round(Number(bet_show)*1.5)
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
        $('form#start').find(':input[type=submit]').prop('disabled', true);
        $('form#start').find(':input[type=number]').prop('disabled', true);
        bet_show = $('#bet').val();
        socket.emit('start_game', {'bet_coin': bet_show});
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