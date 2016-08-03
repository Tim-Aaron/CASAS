//change banner changes the color of the banner at the top of the 
function change_banner(elem)
{
	elem.style.backgroundColor = "#8F8F8F"
}

//backNormal changes the banner back to its original color
function backNormal(elem)
{
	elem.style.backgroundColor = "#EBEBEB"
}

//mouseoverC changes the color of the selected bar and displays the data in the infobox
function mouseoverC(d)
{ 
  //transition color change
     d3.select(this).transition(1000)
   		.style("fill", "#FBFBFB")
   		.style("stroke","#787878")
   		.style("stroke-width", 2);
   	
   	//gets mouse position and sets positions for box and arrow
   	var mouseY = d3.mouse(this);
    var boxPositionY = 0;
    var arrowPositionY = 225;
    

    //checks to see which canvas the user is in (this method is really ugly)
    //we set the canvas size to be .01 different so we can check the canvas based on the size
     //canvas 1
    if (d3.select(this).attr("height") == 60.01)
    {
    //get the data from the bars
    var boxText = "Hours: " + d.sleep_time.hours;
    var boxText2 = "Minutes: " + d.sleep_time.minutes;
    var boxText3 = "Start Time: " + ConvertToStandardTime(d.sleep_time.start_time);
    var boxText4 = "End Time: " + ConvertToStandardTime(d.sleep_time.end_time);
    
    //set the texts for the infobox
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
    
    //canvas 2
    else if (d3.select(this).attr("height") == 60.02)
    { 
    boxPositionY = 380;
    arrowPositionY = 605;
    boxText = "Interruptions: " + d.inter_time.interruptions;
    }
    
    //canvas 3
    else
    {
    
    boxPositionY = 610;
    arrowPositionY = 845;
    boxText = "Total Duration: " + d.inter_time.minutes;
    
    
    }
    
    //gets the position for the infobox and the arrow
	var position = d3.select(this).attr("y") / 80;	
   	var boxPositionX = d3.select(this).attr("y");
   	var slide = boxPositionX - (-370);
   	var arrow_slide = boxPositionX - (-358);
   	//JSONData[position].hours;
   	//var boxText2 = "interruptions: " + JSONData[position].interruptions;
   	
//sets the location of the box so it is right next to the selected bar
 var x = document.getElementById("infobox1");
    	x.style.left = slide + "px";
    	x.style.top = boxPositionY + "px";
    	x.style.transitionDelay = ".05s";
    	x.style.transitionDuration = ".2s";
    	x.style.backgroundColor = "#F3F3F3";
    	x.style.zIndex = "1";
        x.style.borderWidth = "2px";    

//sets the location of the arrow so it is right next to the selected bar
 var y = document.getElementById("arrow-left1");
 		y.style.marginLeft = arrow_slide + "px";
 		y.style.top = arrowPositionY + "px";
 		y.style.transitionDelay = ".05s";
 		y.style.transitionDuration = ".15s";
 		y.style.borderTop = "15px solid transparent";
 		y.style.borderBottom = "15px solid transparent";
 		y.style.borderRight = "15px solid black";
 		
//sets the location of the text so it is right next to the selected bar 	
 var z = document.getElementById("subText1");
   		z.innerHTML = boxText;
   		z.style.color = "#232323";
   		z.style.fontFamily = "helvetica";
   		z.style.transitionDelay = ".05s";
 		z.style.transitionDuration = ".15s";

 	
}

//
/*function change_color(elem)
{
	document.body.style.backgroundColor = "blue";
	update_data();
}*/


//mouseoutC returns the bars back to their original color
function mouseoutC()
{
//sets up the color template
	var color =  d3.scale.linear()
  		.domain([6,12])
  		.range(["#55F3A4", "#020761"]);
	
	//checks which canvas the user is in
	if (d3.select(this).attr("height") == 60.01)
    {
    //canvas 1
    
    //changes the bar back to its original color
    //has a transition to make it a smooth change
    d3.select(this).transition(1000)
   		.style("fill", function(d) {return color(d.sleep_time.hours + (d.sleep_time.minutes/60));})
   		.style("stroke-width", 0);
    
    }
    else if (d3.select(this).attr("height") == 60.02)
    {
    //canvas 2
    d3.select(this).transition(1000)
   		.style("fill", function(d) {return color(d.sleep_time.hours + (d.sleep_time.minutes/60));})
   		.style("stroke-width", 0);
    
    }
    else
    {
    //canvas 3
  	 d3.select(this).transition(1000)
   		.style("fill", function(d) {return color(d.sleep_time.hours + (d.sleep_time.minutes/60));})
   		.style("stroke-width", 0);
    
    }
  		
	
   		
   	//selects the infobox the arrows and the text
   	//switches them to be transparent
   	var x = document.getElementById("infobox1");
        x.style.backgroundColor = "transparent";
        x.style.zIndex = "-3";
        x.style.borderWidth = "0px";
    
    var y = document.getElementById("arrow-left1");

 		y.style.borderTop = "15px solid transparent";
 		y.style.borderBottom = "15px solid transparent";
 		y.style.borderRight = "15px solid transparent";
 	
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

//converts military time to standard time 
function ConvertToStandardTime(militaryTime)
{
//splits the military time at the colon
	var new_parse = militaryTime.split(":");
	
	//converts the hours to standard time
	var hours;
	//there was something going on where the zero was being shown with extra symbols
	//the if statement fixes that
	if(((new_parse[0]) % 12) == 0)
	{
		hours = 12;
	}
	
	else
	{
		hours = (new_parse[0]) % 12;
	}
	
	//checks if it is am or pm
	var amPm = 'am';
	if(new_parse[0] > 11)
	{
		amPm = 'pm';
	}

    var minutes = new_parse[1];
	
	return hours + ':' + minutes + amPm;
}

//getMaxY gets the max data point and returns it
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
