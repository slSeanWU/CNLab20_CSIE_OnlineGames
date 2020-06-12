// console.log(rounds_played);
if (performance.navigation.type == 1 || rounds_played==0) {
	console.info( "This page is reloaded" );
} else {
	var cols = [[$("#col-0 > .row-0"), $("#col-0 > .row-1"), $("#col-0 > .row-2")],
				[$("#col-1 > .row-0"), $("#col-1 > .row-1"), $("#col-1 > .row-2")],
				[$("#col-2 > .row-0"), $("#col-2 > .row-1"), $("#col-2 > .row-2")]
	];
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
		for (var j = 0; j < 3; j++)
			cols[2][j].css("background-image", "url(static/images/slot_"+slot_result[j][2].toString()+".png)");  
	}, 10*(300+20*5));
}