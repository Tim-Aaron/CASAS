function change_banner(elem)
{
	elem.style.backgroundColor = "#8F8F8F"
}

function backNormal(elem)
{
	elem.style.backgroundColor = "#EBEBEB"
}

function mouseoverC(d)
{ 
  
     d3.select(this).transition(1000)
   		.style("fill", "#FBFBFB")
   		.style("stroke","#787878")
   		.style("stroke-width", 2);
   	
   	var mouseY = d3.mouse(this);
    var boxPositionY = 0
    boxPositionY = 50;
    var arrowPositionY = 50;
    

	//new problem in the if statement

    if (d3.select(this).attr("height") == 30.01)
    {
    //canvas 1
    var boxText = "Hours: " + d.sleep_time.hours;
    var boxText2 = "Minutes: " + d.sleep_time.minutes;
    var boxText3 = "Start Time: " + ConvertToStandardTime(d.sleep_time.start_time);
    var boxText4 = "End Time: " + ConvertToStandardTime(d.sleep_time.end_time);
    
    var s = document.getElementById("subText2");
   		s.innerHTML = boxText2;
   		s.style.color = "#232323";
   		s.style.fontFamily = "helvetica";
   		s.style.transitionDelay = ".05s";
 		s.style.transitionDuration = ".15s";
 		
 	var e = document.getElementById("subText3");
   		e.innerHTML = boxText3;
   		e.style.color = "#232323";
   		e.style.fontFamily = "helvetica";
   		e.style.transitionDelay = ".05s";
 		e.style.transitionDuration = ".15s";
 		
	 var f = document.getElementById("subText4");
   		f.innerHTML = boxText4;
   		f.style.color = "#232323";
   		f.style.fontFamily = "helvetica";
   		f.style.transitionDelay = ".05s";
 		f.style.transitionDuration = ".15s";
    }
    else if (d3.select(this).attr("height") == 30.02)
    {
    //canvas 2
    boxPositionY = 380;
    arrowPositionY = 380;
    boxText = "Interruptions: " + d.inter_time.interruptions;
    }
    else
    {
    //canvas 3
    boxPositionY = 610;
    arrowPositionY = 610;
    boxText = "Total Duration: " + d.inter_time.minutes;
    
    
    }
	var position = d3.select(this).attr("y") / 80;
   	
   	var boxPositionX = d3.select(this).attr("y");
   	var slide = boxPositionX - (-370);
   	var arrow_slide = boxPositionX - (-358);
   	//JSONData[position].hours;
   	//var boxText2 = "interruptions: " + JSONData[position].interruptions;
   	
   	
 var x = document.getElementById("infobox1");
    	x.style.left = slide + "px";
    	x.style.top = boxPositionY + "px";
    	//mouseX + "px";
    	x.style.transitionDelay = ".05s";
    	x.style.transitionDuration = ".2s";
    	x.style.backgroundColor = "#F3F3F3";
    	x.style.zIndex = "1";
        x.style.borderWidth = "2px";    

 var y = document.getElementById("arrow-left1");
 		y.style.marginLeft = arrow_slide + "px";
 		y.style.top = arrowPositionY + "px";
 		y.style.transitionDelay = ".05s";
 		y.style.transitionDuration = ".15s";
 		y.style. borderTop = "15px solid transparent";
 		y.style. borderBottom = "15px solid transparent";
 		y.style. borderRight = "15px solid black";
 	
 var z = document.getElementById("subText1");
   		z.innerHTML = boxText;
   		z.style.color = "#232323";
   		z.style.fontFamily = "helvetica";
   		z.style.transitionDelay = ".05s";
 		z.style.transitionDuration = ".15s";

 	
}

function change_color(elem)
{
	document.body.style.backgroundColor = "blue";
	update_data();
}


function mouseoutC()
{
	var color =  d3.scale.linear()
  		.domain([6,12])
  		.range(["#55F3A4", "#020761"]);
	
	if (d3.select(this).attr("height") == 30.01)
    {
    //canvas 1
    d3.select(this).transition(1000)
   		.style("fill", function(d) {return color(d.sleep_time.hours + (d.sleep_time.minutes/60));})
   		//.style("fill", function(d) {return new_color(hours(d));})
   		.style("stroke-width", 0);
    
    }
    else if (d3.select(this).attr("height") == 30.02)
    {
    //canvas 2
    d3.select(this).transition(1000)
   		.style("fill", function(d) {return color(d.sleep_time.hours + (d.sleep_time.minutes/60));})
   		//.style("fill", function(d) {return new_color(hours(d));})
   		.style("stroke-width", 0);
    
    }
    else
    {
    //canvas 3
  	 d3.select(this).transition(1000)
   		.style("fill", function(d) {return color(d.sleep_time.hours + (d.sleep_time.minutes/60));})
   		//.style("fill", function(d) {return new_color(hours(d));})
   		.style("stroke-width", 0);
    
    }
  		
	
   		
   	var x = document.getElementById("infobox1");
        x.style.backgroundColor = "transparent";
        x.style.zIndex = "-3";
        x.style.borderWidth = "0px";
    
    var y = document.getElementById("arrow-left1");

 		y.style. borderTop = "15px solid transparent";
 		y.style. borderBottom = "15px solid transparent";
 		y.style. borderRight = "15px solid transparent";
 	
 	var z = document.getElementById("subText1");
   		z.style.color = "transparent";
   		z.style.zIndex = "-3";
        z.style.borderWidth = "0px";
   		
   	var s = document.getElementById("subText2");
   		s.style.color = "transparent";
   		s.style.zIndex = "-3";
        s.style.borderWidth = "0px";
 		
	var e = document.getElementById("subText3");
   		e.style.color = "transparent";
   		e.style.zIndex = "-3";
        e.style.borderWidth = "0px";
 		
	var f = document.getElementById("subText4");
   		f.style.color = "transparent";
   		f.style.zIndex = "-3";
        f.style.borderWidth = "0px";
}



function MouseOverMonth()
{
 	d3.select(this).transition(1000)
 		//.attr("height","1000")
 		.style("fill", "#0F9761");
}

function MouseOutMonth()
{
d3.select(this).transition(1000)
		//.attr("height","35")
 		.style("fill", "#35D379");
}

function MouseClick()
{
	if (d3.select(this).attr("height") == 35)
	{
		d3.select(this).transition(1000)
		.attr("height","220");
	
	}
	
	
	else
	{
		d3.select(this).transition(1000)
		.attr("height","35");
	
	}
}

function ConvertToStandardTime(militaryTime)
{
	var new_parse = militaryTime.split(":");
	
	var hours;
	if(((new_parse[0]) % 12) == 0)
	{
		hours = 12;
	}
	
	else
	{
		hours = (new_parse[0]) % 12;
	}
	var amPm = 'am';
	if(new_parse[0] > 11)
	{
		amPm = 'pm';
	}

    var minutes = new_parse[1];
	
	return hours + ':' + minutes + amPm;
}

 function getMaxY(data) {
                var max = 0;
                
                for(var i = 0; i < data.length; i++) {
                    if(data[i].inter_time.minutes > max) {
                        max = data[i].inter_time.minutes;
                    }
                }
                
                max += 10 - max % 10;
                return max;
            }
