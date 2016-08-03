//test data
//medication data was not given to us so we made test data

var medData = [2,1,3,1,2,1,3,
			 0,2,1,3,1,2,1,
			 3,3,2,1,3,4,2,
			 1,3,2,1,2,1,2];
			 
var fakeCookies = [2,2,3,1,2,1,4,
				   0,1,1,2,2,1,3,
				   3,2,1,3,4,2,1,
				   3,1,1,1,2,1,1];
				   
var medTime = ['7:00am','7:30am' ,'10:23am' ,'9:00am' ,'8:00am' ,'9:52am' ,'7:15am',
			   '1:00pm','2:11pm' ,'1:20pm','2:30pm' ,'1:35pm' ,'3:10pm' ,'4:15pm',
			   '5:30pm','5:45pm' ,'5:30pm' ,'6:00pm' ,'7:25pm' ,'6:30pm' ,'5:30pm',
			   '9:15pm','10:00pm' ,'9:30pm' ,'10:15pm' ,'9:45pm' ,'9:00pm' ,'10:00pm']



//changes the banner color on hover over
function change_banner(elem)
{
	elem.style.backgroundColor = "#8F8F8F"
}


//changes the background of boxes depending on which box was hovered over
function changeBackground(elem)
{
	var text;
	var super_index;
	
	//we check to see the range of the id (0-6 is morning) (7-13 is noon)(14-20 is evening)(21-27 is evening)
	if(elem.id >= 0 && elem.id <= 6 )
	{
		//we update information in the infobox
		document.getElementById("subText1").innerHTML = "Morning ";
		document.getElementById("subText2").innerHTML = "(6:00am - 12:00pm)";
		
		
		for (var index = 0 ; index < 7; index++)
		{
			if (elem.id == index)
			{
			//we get the specific box that was hovered over
				var temp = "morningText" + index;
				
			//then the information is displayed in the infobox
				text = document.getElementById(temp).innerHTML;
				super_index = elem.id;
			}
		
		}
	}
	
	else if(elem.id >= 7 && elem.id <= 13 )
	{
		document.getElementById("subText1").innerHTML = "Noon ";
		document.getElementById("subText2").innerHTML = "(12:00pm - 5:00pm)";
		
		for (var index = 0; index < 7; index++)
		{
			if (elem.id == index + 7)
			{
				var temp = "noonText" + index;
				
				text = document.getElementById(temp).innerHTML;
				super_index = elem.id;
			}
		
		}
	}
	
	else if(elem.id >= 14 && elem.id <= 20 )
	{
		document.getElementById("subText1").innerHTML = "Evening ";
		document.getElementById("subText2").innerHTML = "(5:00pm - 9:00pm)";
		
		for (var index = 0; index < 7; index++)
		{
			if (elem.id == index + 14)
			{
				var temp = "eveText" + index;
				
				text = document.getElementById(temp).innerHTML;
				super_index = elem.id;
			}
		
		}
	}
	
	else if(elem.id >= 21 && elem.id <= 27 )
	{
		document.getElementById("subText1").innerHTML = "Bed ";
		document.getElementById("subText2").innerHTML = "(9:00am - 12:00pm)";
		
		for (var index = 0; index < 7; index++)
		{
			if (elem.id == index + 21)
			{
				var temp = "bedText" + index;
				
				text = document.getElementById(temp).innerHTML;
				super_index = elem.id;
			}
		
		}
	}
	


//the selected box is then turned white to help show the user which box they are hovering
	elem.style.transitionDelay = ".05s";
	elem.style.transitionDuration = ".2s";
	elem.style.backgroundColor = "white";

	
	//infobox variables are set up
	var x = document.getElementById("infobox1");
	var m = document.getElementById("infoMid");
	var u = document.getElementById("subText1");
	var y = document.getElementById("subText2");
	var z = document.getElementById("subText3");
	var a = document.getElementById("subText4");

	//transitions are placed in and the box is revealed to the users (normally the box is transparent
	x.style.transitionDuration = ".2s";
	x.style.border = "2px solid #414141";
	
	m.style.backgroundColor = "white";
	
	u.style.transitionDuration = ".2s";
	u.style.color = "black";
	
	y.style.transitionDuration = ".2s";
	y.style.color = "black";
	y.style.transitionDuration = ".2s";
	
	z.style.transitionDuration = ".2s";
	z.style.color = "black";
	z.innerHTML = "Medication Taken: ";
	
	a.style.transitionDuration = ".2s";
	a.style.color = "black";
	a.innerHTML = medTime[super_index];
	

//striped borders in case solid borders around the box does not look good
			var k;
			var i;
			var j;
	
			if (medData[elem.id] < fakeCookies[elem.id])
			{
			//red
			
			//If you want a striped border
			
			//x.style.background = "repeating-linear-gradient(135deg,#FF8383,#FF8383 10px,white 10px,white 20px";
			
			x.style.background = "#F8B6B6";

			}
		
			else if (medData[elem.id] > fakeCookies[elem.id])
			{
			//yellow
			
			//If you want a striped border
			
			//x.style.background = "repeating-linear-gradient(135deg,#FFE783,#FFE783 10px,white 10px,white 20px";
			
			x.style.background = "#F8EE91";
			}
		
			else
			{
			//green
			
			//If you want a striped border
			
			//x.style.background = "repeating-linear-gradient(135deg,#3DCD66,#3DCD66 10px,white 10px,white 20px";
			
			x.style.background = "#9EF4B6";
			}
			

		
		
	
}

//returns the hovered box back to the original colors
function backNormal(elem)
{
//checks the IDs of the boxes
	if(elem.id >= 0 && elem.id <= 6 )
	{
	//converts the box back to the proper color
		elem.style.transitionDelay = ".05s";
		elem.style.transitionDuration = ".2s";
		elem.style.backgroundColor = "#FFE76E";
		
		//if it is a current day box then we give it a lighter color
		if (elem.id == 6)
		{
			elem.style.transitionDelay = ".05s";
			elem.style.transitionDuration = ".2s";
			elem.style.backgroundColor = "#FFFEDA";
		}
	}
	
	else if(elem.id >= 7 && elem.id <= 13  )
	{
		elem.style.transitionDelay = ".05s";
		elem.style.transitionDuration = ".2s";
		elem.style.backgroundColor = "#80D5F1";
		
		if (elem.id == 13)
		{
			elem.style.transitionDelay = ".05s";
			elem.style.transitionDuration = ".2s";
			elem.style.backgroundColor = "#D8F2F5";
		}
	}
	
	else if(elem.id >= 14 && elem.id <= 20  )
	{
		elem.style.transitionDelay = ".05s";
		elem.style.transitionDuration = ".2s";
		elem.style.backgroundColor = "#BA6D4C";
		
		if (elem.id == 20)
		{
			elem.style.transitionDelay = ".05s";
			elem.style.transitionDuration = ".2s";
			elem.style.backgroundColor = "#CEA08C";
		}
	}
	
	else if(elem.id >= 21 && elem.id <= 27 )
	{
		elem.style.transitionDelay = ".05s";
		elem.style.transitionDuration = ".2s";
		elem.style.backgroundColor = "#DBEF8B";
		
		if (elem.id == 27)
		{
			elem.style.transitionDelay = ".05s";
			elem.style.transitionDuration = ".2s";
			elem.style.backgroundColor = "#EAF2C7";
		}
	}
	
	else
	{
		elem.style.backgroundColor = "#EBEBEB";
	}
	
	//gets all infobox
	var x = document.getElementById("infobox1");
	var m = document.getElementById("infoMid");
	var y = document.getElementById("subText1");
	var z = document.getElementById("subText2");
	var h = document.getElementById("subText3");
	var a = document.getElementById("subText4");
	 
	 //makes the infobox transparent again
	x.style.transitionDuration = ".08s";
	x.style.background = "transparent";
	x.style.border = "0px solid #414141";
	m.style.backgroundColor = "transparent";
	y.style.transitionDuration = ".2s";
	y.style.color = "transparent";
	z.style.transitionDuration = ".2s";
	z.style.color = "transparent";	
	h.style.transitionDuration = ".2s";
	h.style.color = "transparent";
	a.style.color = "transparent";
	a.style.transitionDuration = ".2s";
}


//gets the pictures on startup
//looks at the data and shows the proper icon
function build_up()
{
	for(var g = 0; g < 28; g++)
		{
			var text = document.getElementsByTagName("h2")
			var k;
			var i;
			var j;
	
	//red x is shown if the patient took less than what was needed
			if (medData[g] < fakeCookies[g])
			{
			//red x
			k = document.getElementById(g).getElementsByClassName("redX");
			i = document.getElementById(g).getElementsByClassName("checkMark");
			j = document.getElementById(g).getElementsByClassName("asterisk");
		
			k[0].style.width = "30px";
			i[0].style.width = "0px";
			j[0].style.width = "0px";
			}
	
	//yellow asterisk is shown if the patient took more than what was needed
			else if (medData[g] > fakeCookies[g])
			{
			//yellow asterisk
			k = document.getElementById(g).getElementsByClassName("redX");
			i = document.getElementById(g).getElementsByClassName("checkMark");
			j = document.getElementById(g).getElementsByClassName("asterisk");
	
			k[0].style.width = "0px";
			i[0].style.width = "0px";
			j[0].style.width = "30px";
	
			}
	
	//green check mark is shown if the patient took exactly what was needed	
			else
			{
			//green check
			k = document.getElementById(g).getElementsByClassName("redX");
			i = document.getElementById(g).getElementsByClassName("checkMark");
			j = document.getElementById(g).getElementsByClassName("asterisk");
		
	
			k[0].style.width = "0px";
			i[0].style.width = "30px";
			j[0].style.width = "0px";
			}
			
			
	
		}


}

