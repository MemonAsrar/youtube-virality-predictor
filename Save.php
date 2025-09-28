<?php
$sever = "localhost";
$username = "root";
$password = "";
$dbname = "link_storage";

$con = mysqli_connect($sever, $username, $password, $dbname);

if(!$con)
{
    echo "Not connected";
}

$Link = $_POST['A_link'];

$sql = "INSERT INTO `interface`(`Link`) VALUES ('$Link')";

$result = mysqli_query($con , $sql);

if($result)
{
    echo "Data Submited";
}

else
{
    echo "Query faild....!";
}


?>