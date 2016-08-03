//checks to see if group of dots have been selected
var highlightCheck = false;

//changes the background of te banner when hovering over a section
function changeBackground(elem)
{
	elem.style.backgroundColor = "#8F8F8F";
}

//changes the selected item back to the color on hover out
function backNormal(elem)
{
	elem.style.backgroundColor = "#EBEBEB";
}

//mouseover changes the colors of the hovered dot and displays the time which the patient ate
function mouseoverC()
{ 
	///changes the dot white and gives it a black border
 	d3.select(this).style("fill", "white");
 	d3.select(this).attr("stroke-width", "2px");
 	d3.select(this).attr("stroke", "#2C2C2C");
 	
 	//finds the selected dot
   	var xPosition = d3.select(this).attr("cx");
   	var yPosition = d3.select(this).attr("cy");
   	
	
	var value = (((d3.select(this).attr("cx") - (-40)) / 83) -1);

	//gets the time at which the patient ate
	
	//converts the bar's height to the proper time the user ate
	var text = d3.select(this).attr("cy");
	text = text - 305;
	text = text/33;
	text = text * (-1);
	text = text.toFixed(2);
	
	text = text.toString()
	console.log(text);
	
	text = text.split(".");
	
	//converts it so the minutes doesn't go above 60
	if ((text[1] * 60)/100 < 10)
	{
		text = text[0] + ":" + '0' + Math.round(text[1] * 60 /100);
	}
	
	else
	{
		text = text[0] + ":" + Math.round(text[1] * 60 / 100);
	}
   	
   	//gets the infobox
   	var z = document.getElementById("infoText");
   	
   	//converts the time from military to standard  and prints it to the infobox
   	z.innerHTML = ConvertToStandardTime(text);
   	
   	console.log(text);
    
    var boxPositionX = xPosition - (-242);
    var boxPositionY = yPosition - (-480);
    
    var box = document.getElementById("infobox");
    
    //makes the box visible to the user
    box.style.marginLeft = boxPositionX;
    box.style.marginTop = boxPositionY;
    
    box.style.backgroundColor = "white";
    box.style.border = "2px solid black";   
}


//mouseout reverts the selected dot back to its original colors
function mouseoutC()
{
//finds the proper dot that was being hovered over
//reverts the colors back to what they were based on the id of the dot

	if (d3.select(this).attr("id")[0] === "o")
	{
	d3.select(this).style("fill","orange");
	d3.select(this).attr("stroke-width", "0px");
	}
	else if (d3.select(this).attr("id")[0] === "b")
	{
	d3.select(this).style("fill","blue");
	d3.select(this).attr("stroke-width", "0px");
	}
	else if (d3.select(this).attr("id")[0] === "r")
	{
	d3.select(this).style("fill","red");
	d3.select(this).attr("stroke-width", "0px");
	}
	else if (d3.select(this).attr("id")[0] === "p")
	{
	d3.select(this).style("fill","purple");
	d3.select(this).attr("stroke-width", "0px");
	}
	else
	{
	d3.select(this).style("fill","green");
	d3.select(this).attr("stroke-width", "0px");
	}
	
	var box = document.getElementById("infobox");
	box.style.backgroundColor = "transparent";
    box.style.border = "0px solid #2C2C2C";
    
    var t = document.getElementById("infoText");
    t.innerHTML = "";

}

//convert to standard time takes military time and converts it to standard time
function ConvertToStandardTime(militaryTime)
{
//parses at the colon
	var new_parse = militaryTime.split(":");
	
	//converts military time to standard time
	var hours;
	if(((new_parse[0]) % 12) == 0)
	{
		hours = 12;
	}
	
	else
	{
		hours = (new_parse[0]) % 12;
	}
	//finds if it is am or pm
	var amPm = 'am';
	if(new_parse[0] > 11)
	{
		amPm = 'pm';
	}

    var minutes = new_parse[1];
	
	//returns standard time
	return hours + ':' + minutes + amPm;
}

//mouse click check highlights a section of dots 
function mouseClickCheck()
{
//checks if there are dots already highlighted
	if(highlightCheck === false)
	{


//if not then we select all of the dots with the same id
//all dots not with the same id become grey
if (d3.select(this).attr("id")[0] === "o")
	{
		for (var x = 0; x < 8; x++)
	{
		var b = document.getElementById("blueCircle" + x);
		b.style.fill = "#BABABA";

		var c = document.getElementById("redCircle" + x);
		c.style.fill = "#BABABA";
	
		if (document.getElementById("purpleCircle" + x) != null)
		{
		var d = document.getElementById("purpleCircle" + x);
		d.style.fill = "#BABABA";
		}
	
		if (document.getElementById("greenCircle" + x) != null)
		{
		var e = document.getElementById("greenCircle" + x);
		e.style.fill = "#BABABA";
		}
	}
	
	}
	else if (d3.select(this).attr("id")[0] === "b")
	{
		for (var x = 0; x < 8; x++)
	{

		var a = document.getElementById("orangeCircle" + x);
		a.style.fill = "#BABABA";

		var c = document.getElementById("redCircle" + x);
		c.style.fill = "#BABABA";
	
		if (document.getElementById("purpleCircle" + x) != null)
		{
		var d = document.getElementById("purpleCircle" + x);
		d.style.fill = "#BABABA";
		}
	
		if (document.getElementById("greenCircle" + x) != null)
		{
		var e = document.getElementById("greenCircle" + x);
		e.style.fill = "#BABABA";
		}
	}
	}
	else if (d3.select(this).attr("id")[0] === "r")
	{
	for (var x = 0; x < 8; x++)
	{

		var a = document.getElementById("orangeCircle" + x);
		a.style.fill = "#BABABA";

		var b = document.getElementById("blueCircle" + x);
		b.style.fill = "#BABABA";
	
		if (document.getElementById("purpleCircle" + x) != null)
		{
		var d = document.getElementById("purpleCircle" + x);
		d.style.fill = "#BABABA";
		}
	
		if (document.getElementById("greenCircle" + x) != null)
		{
		var e = document.getElementById("greenCircle" + x);
		e.style.fill = "#BABABA";
		}
	}
	}
	else if (d3.select(this).attr("id")[0] === "p")
	{
	for (var x = 0; x < 8; x++)
	{

		var a = document.getElementById("orangeCircle" + x);
		a.style.fill = "#BABABA";

		var b = document.getElementById("blueCircle" + x);
		b.style.fill = "#BABABA";

		var c = document.getElementById("redCircle" + x);
		c.style.fill = "#BABABA";
	
		if (document.getElementById("greenCircle" + x) != null)
		{
		var e = document.getElementById("greenCircle" + x);
		e.style.fill = "#BABABA";
		}
	}
	
	}
	else
	{
	for (var x = 0; x < 8; x++)
	{

		var a = document.getElementById("orangeCircle" + x);
		a.style.fill = "#BABABA";

		var b = document.getElementById("blueCircle" + x);
		b.style.fill = "#BABABA";

		var c = document.getElementById("redCircle" + x);
		c.style.fill = "#BABABA";
	
		if (document.getElementById("purpleCircle" + x) != null)
		{
		var d = document.getElementById("purpleCircle" + x);
		d.style.fill = "#BABABA";
		}
	}
	}
	
	
	
		highlightCheck = true;
	}

//if a group is already highlighted then we change all the greyed out dots back to their original colors
	else
	{
		console.log("we enter unhiglightCheck");
		for (var x = 1; x < 8; x++)
	{
		var a = document.getElementById("orangeCircle" + x);
		a.style.fill = "orange";

		var b = document.getElementById("blueCircle" + x);
		b.style.fill = "blue";

		var c = document.getElementById("redCircle" + x);
		c.style.fill = "red";
	
		if (document.getElementById("purpleCircle" + x) != null)
		{
			var d = document.getElementById("purpleCircle" + x);
			d.style.fill = "purple";
		}
		
		if (document.getElementById("greenCircle" + x) != null)
		{
			var e = document.getElementById("greenCircle" + x);
			e.style.fill = "green";
		}
	}

	document.getElementById("orangeCircle0").style.fill = "orange";
	document.getElementById("blueCircle0").style.fill = "blue";
	document.getElementById("redCircle0").style.fill = "red";
	document.getElementById("purpleCircle0").style.fill = "purple";
	document.getElementById("greenCircle0").style.fill = "green";
	
		highlightCheck = false;
	}

}
