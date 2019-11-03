<?php
include_once("common.php");

// Get the raw POST data.
$data = file_get_contents('php://input');
if($stmt = $mysqli->prepare("INSERT INTO report (datuh) VALUES (?)")){
    if($stmt->bind_param("s", $data)){
		if(!$stmt->execute()){
			die("Error - Issue executing prepared statement: " . mysqli_error($mysqli));
        }
        else{
            $id = $stmt->insert_id;
            die("full send; it worked");
        }
    }
    else{
        die("Error - Issue binding prepared statement: " . mysqli_error($mysqli));
    }
    if($stmt->close()){
        $good = true;
        die("closed");
    }
    else{
        die("Error - Failed to close prepared statement" . mysqli_error($mysqli));
    }
}
else{
    die("Error - Issue preparing statement: " . mysqli_error($mysqli));
}
die("no wonder no one uses this");
?>