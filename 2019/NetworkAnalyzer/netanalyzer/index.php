<?php
$db = new mysqli('localhost', 'root', '', 'pi');

if ($db->connect_errno > 0) {
	die("Unable to connect to database [" . $db->connect_error . "]");
}

function fact( $int ){
	$result = 1;
	for( $loop = 1; $loop <= $int; $loop++ ){
		$result = $loop * $result;
	}
	return $result;
}

function GoS($A){
	$N = 10;
	$k = 0;
	$sum = 0;
	//Summation
	for( $loop = $k; $loop <= $N; $loop++ ){
		$sum += ( pow( $A, $k ) ) / ( fact($k) );
	}
	$result = ( ( pow( $A, $N ) / fact( $N ) ) /  $sum ) * 100 ;
	return $result.' %';
}

?>

<html>
<head>
	<title> Network Traffic Analyser </title>
	<link href="style.css" rel="stylesheet" type="text/css">
	<link rel="shortcut icon" HREF="./icon.png">

	<script>
		var xmlhttp = new Array();
		var elementID = new Array();

// This is an ajax call to do the DNS lookup. We want the table to load quickly and resolve will happen when it's ready
// Since we will have many ajax calls at once, we need to index them as they async coming back to us
		function dnsLookup (elementID, ipToLookup) {
			index = xmlhttp.length;
			xmlhttp[index] = (new XMLHttpRequest());
			xmlhttp[index].cellID = elementID;
			xmlhttp[index].onreadystatechange=function() {
				if (this.readyState==4 && this.status==200) {
					document.getElementById(this.cellID).innerHTML = ' (' + this.responseText + ')';
				}
			}
			elementID[index] = ipToLookup;
			xmlhttp[index].open("GET","ajax.php?dnslookup=" + ipToLookup, true);
			xmlhttp[index].send();
		}

// This is an ajax call to do expande the source list
		function expandDetails(dstIP) {
			var td = document.getElementById(dstIP + '_dst'), rowLocation = td.parentNode.rowIndex + 1;

			originalInnerHTML = td.innerHTML;
			td.innerHTML = '<img src=./loading.gif width="30" height="30"/>';

			xmlhttp = (new XMLHttpRequest());
			xmlhttp.onreadystatechange=function() {
				if (this.readyState==4 && this.status==200) {
					var tableToExpand = document.getElementById("networkDetails");

					// the ajax returns a JSON string with the list
					var list = JSON.parse(this.response);

    				for(i = 0; i < list.length; i++) {
						var row = tableToExpand.insertRow(rowLocation + i);
						var name = row.insertCell(0);
						var traffic = row.insertCell(1);
						var firstSeen = row.insertCell(2);
						var lastUpdate = row.insertCell(3);

						var uniqid = Date.now();
						var dnsLookupResult = dnsLookup(uniqid + '_resolve', list[i].ip);

						name.innerHTML = '<span id="' + uniqid + '" OnClick="PopupEditName(\'' + list[i].ip + '\', \'' + list[i].name +'\')">' + list[i].name + '</span><span id="' + uniqid + '_resolve" OnClick="window.open(\'whois.php?ip=' + list[i].ip + '\')">' + dnsLookupResult + '</span>';
						name.innerHTML = name.innerHTML + '<div class="inlineIcons"><span OnDblClick="deleteIP(\''+list[i].ip+'\')"><img src="./delete.png" /></span></div>';
						name.className = "expanded leftAlign";
						if (list[i].ip == list[i].name) {
							name.style.color = 'red';
						}
						traffic.innerHTML = list[i].traffic + " Mb"; traffic.className = "expanded centerAlign";
						firstSeen.innerHTML = list[i].firstSeen; firstSeen.className = "expanded centerAlign";
						lastUpdate.innerHTML = list[i].lastUpdate; lastUpdate.className = "expanded centerAlign";
					}
				td.innerHTML = originalInnerHTML;
				td.parentNode.className = "bold";
				// Removing the expand icon
				document.getElementById(dstIP + '_expand').style.display = 'none';
				}
			}
			xmlhttp.open("GET","ajax.php?expandSourceIP=" + dstIP, true);
			xmlhttp.send();
		}

// Function to reveal the hidden div to put the screen on and the edit input, filling the input with pre-exsiting name
		function PopupEditName (ip, name) {
			document.getElementById('editPopupDiv').style.display = "block";

			document.getElementById('editPopupInputIP').innerHTML = ip;
			if (ip != name) {
				document.getElementById('editPopupInputName').value = name;
			  }
			  else {
			  	document.getElementById('editPopupInputName').value = '';	
			  }

			document.getElementById('editPopupInputName').focus();

  			xmlhttp = (new XMLHttpRequest());
			xmlhttp.onreadystatechange=function() {
				if (this.readyState==4 && this.status==200) {
				var list = JSON.parse(this.responseText);
				console.log(this.responseText);
				console.log(list);
				var editPopupInputName = document.getElementById('editPopupInputName');
				document.getElementById("commonlyUsed").innerHTML = '<p>Commonly used before (click to insert):</p>'
   				for(i = 0; i < list.length; i++) {
					document.getElementById("commonlyUsed").innerHTML += '<span OnClick=\'editPopupInputName.value = "'+list[i]+'"\'>'+list[i]+'</span><br />';
					}
				}
			}
			xmlhttp.open("GET","ajax.php?commonlyUsed", true);
			xmlhttp.send();
		}

// Ajax call to create or update the alias and the IP, and hide the update div screen.
		function updateNameInDB () {
			var ip = document.getElementById('editPopupInputIP').innerHTML;
			var name = document.getElementById('editPopupInputName').value;

			xmlhttp = (new XMLHttpRequest());
			xmlhttp.open("GET","ajax.php?updateName=" + name + "&ip=" + ip, true);
			xmlhttp.send();

			document.getElementById('editPopupDiv').style.display = "none";
		}

// Ajax call to delete an IP completely from the database		
		function deleteIP (ip) {
			var confirm = prompt('Are you sure you want to delete all records with the IP ' + ip + '?\n\nType "YES"');

			if (confirm == "YES") {
				xmlhttp = (new XMLHttpRequest());
				xmlhttp.open("GET","ajax.php?deleteIP=" + ip, true);
				xmlhttp.send();
			}
		}
		</script>

</head>
<body>

<!--                       -->
<!-- The Edit popup window -->
<!--                       -->

<div id="editPopupDiv" class="editPopup">
	<div class="editPopupContent">
		<span id="editPopupClose" class="editPopupClose" OnClick="document.getElementById('editPopupDiv').style.display='none'">×</span>
		<p>Assign name to <span id="editPopupInputIP"></span>: <input type="text" id="editPopupInputName" size="30" OnKeyDown="if (event.keyCode == 13) updateNameInDB()" /><button OnClick="updateNameInDB();">Update</button></p>
		<div id="commonlyUsed" class="commonlyUsed"></div>
	</div>
	
</div>

<script>
// Hiding the popup div if clicked outside the box or ESC was pressed
	window.onclick = function(event) {
		if (event.target == document.getElementById('editPopupDiv')) {
			document.getElementById('editPopupDiv').style.display = "none";
		}
	}
	window.onkeydown = function(event) {
		if (event.keyCode == 27) {
			document.getElementById('editPopupDiv').style.display = "none";	
		}
	}
</script>


<?php
// Get the destination list. Only those who overall traffic of more then 1Mbytes
//$sql = 'select ips.name as name, INET_NTOA(dstIP) as dstIP, sum(traffic)/1048576 as totalTraffic from traffic left join ips on traffic.dstIP = ips.ip group by dstIP having totalTraffic > 5 order by totalTraffic desc';
$sql = 'select ips.name as name, INET_NTOA(dstIP) as dstIP, sum(traffic)/1048576 as totalTraffic from traffic left join ips on traffic.dstIP = ips.ip GROUP BY dstIP HAVING totalTraffic > 1 order by totalTraffic desc';
if (!$traffic = $db->query($sql)) {
	die ('Error: '.$sql.'<br>'.$db->error);
}
?>
	<table id="networkDetails" border="1" class="Table" style="width: 100%">
		<tr>
			<th style="width: 65%";>Destination</th>
			<th style="width: 25%";>Traffic</th>
			<th style="width: 5%";>First Seen<br />(days)</th>
			<th style="width: 5%";>Last update<br />(days)</th>
		</tr>
<?php		
			
			while ($row = $traffic->fetch_assoc()) { ?>
			<tr>
				<td id="<?php echo ($row['dstIP'])?>_dst" class="leftAlign">
					<?php if ($row['name'] == NULL) $row['name'] = $row['dstIP']; ?>
					<span id="<?php echo($row['dstIP'])?>_name" OnClick="PopupEditName('<?php echo($row['dstIP'])?>', '<?php echo($row['name'])?>')">
						<?php echo($row['name'])?>
					</span>
					<span id="<?php echo($row['dstIP'])?>_resolve" OnClick="window.open('whois.php?ip=<?php echo($row['dstIP'])?>')">
						<script>dnsLookup("<?php echo($row['dstIP'])?>_resolve", "<?php echo($row['dstIP'])?>")</script>
					</span>
					<div class="inlineIcons">
						<span OnDblClick="deleteIP('<?php echo($row['dstIP'])?>')">
							<img src="./delete.png" />
						</span>
						<span id="<?php echo($row['dstIP'])?>_expand" OnClick="expandDetails('<?php echo($row['dstIP'])?>')">
							<img src="./expand.png" />
						</span>
					</div>
				</td>
				<td class="centerAlign"><?php echo ((number_format($row['totalTraffic'],2,'.',',')))?> Mb</td>
				<td>&nbsp;</td>
				<td>&nbsp;</td>
			</tr>
		<?php			}
			$sql = 'select sum(traffic)/1048576 as totalTraffic from traffic';
			if (!$totalTraffic = $db->query($sql)) {
				die ('Error: '.$sql.'<br>'.$db->error);
			}
			$row = $totalTraffic->fetch_assoc();
		?>
		<tr>
			<td>Total</td>
			<td colspan="3"><?php echo ((number_format($row['totalTraffic'],2,'.',',')))?> Mb</td>
		</tr>
	</table></br>
	<table id="leasesDetails" border="1" class="Table" style="width: 100%">
		<th style="width: 5%">No</th>
		<th style="width: 50%";>Clients</th>
		<th style="width: 30%";>MAC</th>
		<th style="width: 15%";>Status</th>
		<?php
			$sql = "SELECT INET_NTOA(ip) AS ip, host, mac, leaseStatus FROM leases";
			if (!$leases = $db->query($sql)) {
				die ('Error: '.$sql.'<br>'.$db->error);
			}
			$cnt=1;
			while ($row = $leases->fetch_assoc()) { ?>
		<tr>
			<td><?php echo $cnt; $cnt += 1;?></td>
			<td><?php echo $row['host'];?></td>
			<td><?php echo $row['mac'];?></td>
			<td><?php if($row['leaseStatus'] == 'u'){echo 'Online';}else if($row['leaseStatus'] == 'd'){echo 'Offline';}?></td>
		</tr>
		<?php			}
			$sql = "SELECT COUNT(leaseStatus) as totalOnline FROM leases WHERE leaseStatus = 'u'";
			if (!$totalOnline = $db->query($sql)) {
				die ('Error: '.$sql.'<br>'.$db->error);
			}
			$row = $totalOnline->fetch_assoc();
		?>
		<tr>
			<td colspan="3">Total online</td>
			<td><?php echo $row['totalOnline']; ?> User</td>
		</tr>
	</table></br>
<?php
$db->close();

exec('pgrep -f "python /usr/local/bin/sniffer.py"', $pids);
if(!empty($pids))
	echo ('Sniffer is <span style="color: green;">RUNNING</span><br />');
  else
  	echo ('Sniffer is <span style="color: red;">NOT RUNNING</span><br />');

exec('pgrep tcpdump', $pids);
if(!empty($pids))
	echo ('tcpdump is <span style="color: green;">RUNNING</span><br />');
  else
  	echo ('tcpdump is <span style="color: red;">NOT RUNNING</span><br />');
?>
