var coins_now = Number($("#coins-store").val());
var total_earnings_now = Number($("#total-earnings").val());
var last_earnings_now = Number($("#last-earnings").val());

var cols = [[$("#col-0 > .row-0"), $("#col-0 > .row-1"), $("#col-0 > .row-2")],
			[$("#col-1 > .row-0"), $("#col-1 > .row-1"), $("#col-1 > .row-2")],
			[$("#col-2 > .row-0"), $("#col-2 > .row-1"), $("#col-2 > .row-2")]
];
function blink(a, b, c){
	cols[a][b].css("opacity",c);
}
function setint(i,j){
	setInterval(blink, 1000, i, j, "1");
}
if (performance.navigation.type == 1 || rounds_played==0) {
	console.info( "This page is reloaded" );
} else {
	// code這麼醜是因為timeout 不吃global
	//line 0
	for (var i = 0; i < 100; i++) {
		if (i<80) {
			setTimeout(function(){
				for (var j = 0; j < 3; j++) {
					cols[0][j].css("background-image", "url(static/images/slot_"+Math.floor(Math.random() * 8)+".png)");  
				}
			}, 10*i);
		}
		else{
			setTimeout(function(){
				for (var j = 0; j < 3; j++) {
					cols[0][j].css("background-image", "url(static/images/slot_"+Math.floor(Math.random() * 8)+".png)");  	
				}
			}, 10*(i+(i-80)*5));
		}
	}
	setTimeout(function(){
		for (var j = 0; j < 3; j++)
			cols[0][j].css("background-image", "url(static/images/slot_"+slot_result[j][0].toString()+".png)");  
	}, 10*(100+20*5));
	//line 1
	for (var i = 0; i < 200; i++) {
		if (i<180) {
			setTimeout(function(){
				for (var j = 0; j < 3; j++) {
					cols[1][j].css("background-image", "url(static/images/slot_"+Math.floor(Math.random() * 8)+".png)");  
				}
			}, 10*i);
		}
		else{
			setTimeout(function(){
				for (var j = 0; j < 3; j++) {
					cols[1][j].css("background-image", "url(static/images/slot_"+Math.floor(Math.random() * 8)+".png)");  
				}
			}, 10*(i+(i-180)*5));
		}
	}
	setTimeout(function(){
		for (var j = 0; j < 3; j++)
			cols[1][j].css("background-image", "url(static/images/slot_"+slot_result[j][1].toString()+".png)");  
	}, 10*(200+20*5));
	//line 2
	for (var i = 0; i < 300; i++) {
		if (i<280) {
			setTimeout(function(){
				for (var j = 0; j < 3; j++) {
					cols[2][j].css("background-image", "url(static/images/slot_"+Math.floor(Math.random() * 8)+".png)");  
				}
			}, 10*i);
		}
		else{
			setTimeout(function(){
				for (var j = 0; j < 3; j++) {
					cols[2][j].css("background-image", "url(static/images/slot_"+Math.floor(Math.random() * 8)+".png)");  
				}
			}, 10*(i+(i-280)*5));
		}
	}
	setTimeout(function(){
		for (var j = 0; j < 3; j++){
			cols[2][j].css("background-image", "url(static/images/slot_"+slot_result[j][2].toString()+".png)");
			if (win_lines[j]<=0){
				cols[0][j].css("opacity","0.5");
				cols[1][j].css("opacity","0.5");
				cols[2][j].css("opacity","0.5");
			}
			if(win_lines[j]>0) {
				setInterval(blink, 1000, 0, j, "0.5");
				setTimeout(setint, 500, 0,j);
				setInterval(blink, 1000, 1, j, "0.5");
				setTimeout(setint, 500, 1,j);
				setInterval(blink, 1000, 2, j, "0.5");
				setTimeout(setint, 500, 2,j);
			}
		}
		$('#user_coins').html("Coins: "+coins_now.toString());
		$('#total_earnings').html("Total Earnings: "+total_earnings_now.toString());
		$('#last_earnings').html("Current Round Earnings: "+last_earnings_now.toString());
	}, 10*(300+20*5));
}