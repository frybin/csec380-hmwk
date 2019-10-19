<?php
include_once("common.php");
session_start();
$has_session = session_status() == PHP_SESSION_ACTIVE;
if($has_session){
	$destroy = false;
	if (!isset($_SESSION['login']) or !isset($_SESSION['user_id'])){
		session_regenerate_id(true);
		session_destroy();
		die("<script>window.location.href = '/index.php';</script>Invalid Session");
	}
	if($_SERVER['REMOTE_ADDR'] !== $_SESSION['login']['ip']){
		$destroy = true;
	}
	//if($_SESSION['login']['born'] < time() - 300){
	//	$destroy = true;	
	//}
	if($_SESSION['login']["valid"] !== true){
		$destroy = true;
	}
	if($destroy===true){
		session_destroy();
	}
	// Reset our counter
	$_SESSION['login']['born'] = time();	

	// Get Profile data
	// Prepare a statement
	if($stmt = $mysqli->prepare("SELECT * from profiles where user_id=?")){
		//Bind the "user_id" to the "?" param from the statement
		if($stmt->bind_param("i", $_SESSION['user_id'])){
			// Execute statement
			if(!$stmt->execute()){
				die("Error - Issue executing prepared statement: " . mysqli_error($mysqli));
			}
			// Get the resulting columns/rows from stmt
			if($res = $stmt->get_result()){
				// row is now an associative array that corresponds to fetched row
				$row = $res->fetch_assoc();
				//Should only get 1 row back
				if($res->num_rows !== 1){
					die('Error - There is an issue with the database, contact your administrator');
				}else{
					// friends is a string of friends seperated by commas
					$friends = $row['Friends'];
				}
			}else{
				die("Error - Getting results: " . mysqli_error($mysqli));
			}
		}else{
			die("Error - Issue binding prepared statement: " . mysqli_error($mysqli));
		}
	}else{
		die("Error - Issue preparing statement: " . mysqli_error($mysqli));
	}
	// If "id" is set in params it overrides session id
	$id_to_get = $_SESSION['user_id'];
	if(isset($_GET['id'])){
		$id_to_get = $_GET['id'];
	}	

	// If the array isn't us
	if($id_to_get === $_SESSION['user_id']){
		die("There was an issue contact your administrator");
	}
	// If the element is numeric
	if(!is_numeric($id_to_get)){
		die("There was an issue contact your administrator");
	}
	// Friends is now array of friends
	$friends = explode(',',$friends);
	// If it's already in the array
	if(array_search($id_to_get,$friends)){
		die("There was an issue contact your administrator");
	}	
	// Push new user id to friend into array of friends
	array_push($friends,$id_to_get);
	// Put the array back into a string
	$ids = implode(',',$friends);
	// Update the friends table
	if($stmt = $mysqli->prepare("UPDATE profiles SET Friends=? WHERE user_id=?")){
		if($stmt->bind_param("si", $ids, $_SESSION['user_id'])){
			if(!$stmt->execute()){
				die("Error - Issue executing prepared statement: " . mysqli_error($mysqli));
			}
		}else{
			die("Error - Issue binding prepared statement: " . mysqli_error($mysqli));
		}
		if($stmt->close()){
			echo "True - Friend Added Successfully";
		}else{
			die("Error - Failed to close prepared statement" . mysqli_error($mysqli));
		}
	}else{
		die("Error - Issue preparing statement: " . mysqli_error($mysqli));
	}
}
?>
