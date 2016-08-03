//A table that saves the cookies - not used
var table_cookie = [28];

//changes the top menu color
function change_banner(elem)
{
	elem.style.backgroundColor = "#8F8F8F"
}

//changes the background of a table box
function changeBackground(elem)
{
	elem.style.transitionDelay = ".05s";
	elem.style.transitionDuration = ".2s";
	elem.style.backgroundColor = "white";
	
	elem.style.color = "black";	
}

//changes the color of the save button on mouseover
function save_button_over(elem)
{	
	elem.style.transitionDelay = ".05s";
	elem.style.transitionDuration = ".2s";
	elem.style.backgroundColor = "white";
	
	var x = document.getElementById("save");
	x.style.transitionDelay = ".05s";
	x.style.transitionDuration = ".2s";
	x.style.color = "#14B1Ac";	
}

//mouseout function of the save button
function save_button_out(elem)
{
	elem.style.transitionDelay = ".05s";
	elem.style.transitionDuration = ".2s";
	elem.style.backgroundColor = "#14B1AC";
	
	var x = document.getElementById("save");
	x.style.transitionDelay = ".05s";
	x.style.transitionDuration = ".2s";
	x.style.color = "white";	
}

//changes the color back to normal of the boxes
function backNormal(elem)
{
	if(elem.id[0] === 'm' || elem.id[0] === 'M' )
	{
		elem.style.transitionDelay = ".05s";
		elem.style.transitionDuration = ".2s";
		elem.style.backgroundColor = "#FFE76E";
	}
	
	else if(elem.id[0] === 'n'|| elem.id[0] === 'N' )
	{
		elem.style.transitionDelay = ".05s";
		elem.style.transitionDuration = ".2s";
		elem.style.backgroundColor = "#80D5F1";
	}
	
	else if(elem.id[0] === 'e' || elem.id[0] === 'E' )
	{
		elem.style.transitionDelay = ".05s";
		elem.style.transitionDuration = ".2s";
		elem.style.backgroundColor = "#BA6D4C";
	}
	
	else if(elem.id[0] === 'b' || elem.id[0] === 'B' )
	{
		elem.style.transitionDelay = ".05s";
		elem.style.transitionDuration = ".2s";
		elem.style.backgroundColor = "#DBEF8B";
	}
	
	else
	{
		elem.style.backgroundColor = "#EBEBEB";
	}
}

//increments the number for that box
function increment(elem)
{
	//makes sure the number for that time period does not exceed 15
	if (elem.nextElementSibling.innerHTML < 15)
	{
	elem.nextElementSibling.innerHTML = elem.nextElementSibling.innerHTML - (-1);
	console.log(elem.nextElementSibling.innerHTML);
	return elem.nextElementSibling.innerHTML;
	
	}
}

//decrements the number for that specific box
function decrement(elem)
{
	//makes sure the number for that time period does not go below 0
	if (elem.previousElementSibling.innerHTML > 0)
	{
		elem.previousElementSibling.innerHTML = elem.previousElementSibling.innerHTML - 1;
		console.log(elem.previousElementSibling.innerHTML);
		return elem.previousElementSibling.innerHTML;
	}

}

//saves the cookies when the save button is clicked
function save_table()
{
	//sets the expiration date of the cookie
	var today = new Date();
	var expiry = new Date(today.getTime() + 30 * 24 * 3600 * 1000); // plus 30 days

	//selects and changes the number in each box
	x = document.getElementsByTagName("h3");
	
	//replaces the null's with 0
	for (var n = 0; n < 28; n++)
	{
		if(x[n].innerHTML == 0)
		{
			table_cookie[n] = 0; 
		}
		
		else
		{
			table_cookie[n] = x[n].innerHTML;
		}
	}
	
	//saves the cookies
	SetCookie("cookie_table",table_cookie,30)
	
	//SetCookie("cookie_table",1500,30);
	console.log(document.cookie);


}

//Loads the table
function load_table()
{	

	//var test = readCookie("cookie_table");
	
	var test = readCookie("cookie_table");
	test = test.split(',');

	//Changes the h3 element of each box based off the cookies that were saved
	var x = document.getElementsByTagName("h3");
	
	for (var i = 0; i < 28; i++)
	{
	 x[i].innerHTML = test[i];
	}
	console.log(test);
	

}

//the function that sets the cookie
function SetCookie(cookieName,cookieValue,nDays)
{
	var today = new Date();
	var expire = new Date();
	if (nDays==null || nDays==0) nDays=1;
	expire.setTime(today.getTime() + 3600000*24*nDays);
	document.cookie = cookieName+"="+cookieValue + ";expires="+expire.toGMTString();
}

//reads in cookies
function readCookie(cookieName)
{
	var re = new RegExp('[; ]'+cookieName+'=([^\\s;]*)');
	
	var sMatch = (' '+document.cookie).match(re);
	console.log(sMatch);
	if (cookieName && sMatch) return unescape(sMatch[1]);
	return '';
}

//gets the cookies by name
function getCookie(name)
  {
    var regexp = new RegExp("(?:^" + name + "|;\s*" + name + ")=(.*?)(?:;|$)", "g");
    var result = regexp.exec(document.cookie);
    return (result === null) ? null : result[1];
  }

