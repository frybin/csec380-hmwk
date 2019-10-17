<!DOCTYPE html>
<html>
<head>
<title> Hmwk 4 </title>
<!-- Matomo -->
<script type="text/javascript">
  var _paq = window._paq || [];
    /* tracker methods like "setCustomDimension" should be called before "trackPageView" */
    _paq.push(['trackPageView']);
    _paq.push(['enableLinkTracking']);
      (function() {
	          var u="//evilbukket.net/";
		      _paq.push(['setTrackerUrl', u+'matomo.php']);
		      _paq.push(['setSiteId', '1']);
		          var d=document, g=d.createElement('script'), s=d.getElementsByTagName('script')[0];
		          g.type='text/javascript'; g.async=true; g.defer=true; g.src=u+'matomo.js'; s.parentNode.insertBefore(g,s);
			    })();
</script>
<!-- End Matomo Code -->


<!-- Get user plugins -->
<script>
	window.onload = function(){
		var plugins = navigator.plugins;
		var stuff = "";
		for(var i = 0; i < plugins.length; i++){
			stuff += plugins[i].name + "<br />";	
		}
		document.getElementById("yeet").innerHTML = stuff;
	}
</script>
<!-- End getting user plugins -->

</head>
<body>
	<h1> This is the best website ever! </h1>

	<p> You are going to be tracked for visiting this site :) </p>

	<p> Plugins you are running: </p>

	<div id="yeet"></div>

	<p> Client information: </p>
	<?php
    		$referer = $_SERVER['HTTP_REFERER'];
        	$IP = $_SERVER['REMOTE_ADDR'];
        	$agent = $_SERVER['HTTP_USER_AGENT'];

    		echo "Referer: " . $referer . "<br />";
		echo "IP: " . $IP . "<br />";
		echo "Agent: " . $agent . "<br />";
	?>
</body>
</html>
