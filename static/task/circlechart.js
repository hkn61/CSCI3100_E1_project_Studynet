var ctx1 = document.getElementById('pieChart');
var internetType = []; 	
var onePercentage = [];  
var backColor1 = [];
for(var i = 0; ith = data.actiontype.length, i < ith; i++){
internetType.push(data.actiontype[i].type);
onePercentage.push(data.actiontype[i].percent);				                                                                                                                    
    backColor1.push('#FF6384','#36A2EB','#FFCE96','#FFCE00','#36E2EB','#838B2E','#B2E6C3','#DCB4B8','#9FC3F7');
}
	var pirChart = new Chart(ctx1,{
		type:'pie',
		data:{
			labels: internetType, 
			datasets:[{
			    data: onePercentage, 
				backgroundColor:backColor1, 
				hoverBackgroundColor:backColor1
			}]
		}
	});