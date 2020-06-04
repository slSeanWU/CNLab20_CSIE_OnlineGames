function Card(type, num) {
	this.type = type;
	this.num = num;
}
function new_card(){
	var i = Math.floor(Math.random() * 52)+ 1;
	var type_i = floor((i-1)/13);
	var num_i = i%13;
	Card(type_i, num_i);
}
function disp_card(card){
	result = '';
	switch(card.type){
		case 0:
			result += 'Spade ';
			break;
		case 1:
			result += 'Heart ';
			break;
		case 2:
			result += 'Diamond ';
			break;
		case 3:
			result += 'Clover ';
			break;
	}
	switch(card.num){
		case 1:
			result +='A';
			break;
		case 11:
			result +='J';
			break;
		case 12:
			result +='Q';
			break;
		case 0:
			result +='K';
			break;
		default:
			result += card.num;
	}
	return result;
}
mid_public=[new_card(),new_card(),new_card(),new_card(),new_card()];
