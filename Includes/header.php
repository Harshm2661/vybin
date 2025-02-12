<?php
    include("Includes/config.php");
    include("Includes/classes/User.php");
    include("Includes/classes/Artist.php");
    include("Includes/classes/Album.php");
    include("Includes/classes/Song.php");
    include("Includes/classes/Playlist.php");

    // LOGOUT
    // session_destroy();

    if(isset($_SESSION['userLoggedIn'])) {
        $userLoggedIn = new User($con, $_SESSION['userLoggedIn']);
        $username = $userLoggedIn->getUsername();
        echo "<script>userLoggedIn = '$username';</script>";
    }
    else {
        header("Location: register.php");
    }
?>
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8" />
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <title>Vybin</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" type="text/css" href="assets/css/perfect-scrollbar.css">
    <link rel="stylesheet" type="text/css" media="screen" href="assets/css/style.css" />
    <link rel="shortcut icon" href="favicon.ico" type="image/x-icon"/>
    <script type="text/javascript" src="assets/js/jquery-3.3.1.min.js" ></script>
    <script src="assets/js/script.js"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600&display=swap" rel="stylesheet">
</head>
<body>
    <div id="mainContainer">
        <div id="topContainer">
            <?php include("Includes/navBarContainer.php"); ?>

            <div id="mainViewContainer">
                <div id="mainContent">