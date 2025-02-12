<?php
    include("Includes/config.php");
    if(!isset($_SESSION['adminLoggedIn'])) {
        header("Location: adminLogin.php");
        exit();
    }


    // Handle form submission for adding a new song
    if(isset($_POST['addSong'])) {
        $title = $_POST['title'];
        $artist = $_POST['artist'];
        $album = $_POST['album'];
        $genre = $_POST['genre'];
        $duration = $_POST['duration'];
        $path = $_POST['path'];
        $albumOrder = $_POST['albumOrder'];
        $plays = $_POST['plays'];

        $query = mysqli_query($con, "INSERT INTO songs (title, artist, album, genre, duration, path, albumOrder, plays) 
                                     VALUES ('$title', '$artist', '$album', '$genre', '$duration', '$path', '$albumOrder', '$plays')");

        if($query) {
            echo "New song added successfully.";
        } else {
            echo "Failed to add the song.";
        }
    }

    // Handle form submission for deleting a song by ID
    if(isset($_POST['deleteSong'])) {
        $songId = $_POST['songId'];

        $query = mysqli_query($con, "DELETE FROM songs WHERE id='$songId'");

        if($query) {
            echo "Song deleted successfully.";
        } else {
            echo "Failed to delete the song.";
        }
    }
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" type="text/css" href="assets/css/admin.css">
    <title>Admin Dashboard</title>
</head>
<body>

    <h1>Admin Dashboard</h1>

    <!-- Form to add a new song -->
    <form method="POST" action="adminDashboard.php">
        <h2>Add New Song</h2>
        <label for="title">Title:</label>
        <input type="text" name="title" id="title" required><br>

        <label for="artist">Artist ID:</label>
        <input type="number" name="artist" id="artist" required><br>

        <label for="album">Album ID:</label>
        <input type="number" name="album" id="album" required><br>

        <label for="genre">Genre ID:</label>
        <input type="number" name="genre" id="genre" required><br>

        <label for="duration">Duration:</label>
        <input type="text" name="duration" id="duration" required><br>

        <label for="path">Path:</label>
        <input type="text" name="path" id="path" required><br>

        <label for="albumOrder">Album Order:</label>
        <input type="number" name="albumOrder" id="albumOrder" required><br>

        <label for="plays">Plays:</label>
        <input type="number" name="plays" id="plays" required><br>

        <button type="submit" name="addSong">Add Song</button>
    </form>

    <hr>

    <!-- Form to delete a song by ID -->
    <form method="POST" action="adminDashboard.php">
        <h2>Delete Song</h2>
        <label for="songId">Song ID:</label>
        <input type="number" name="songId" id="songId" required><br>
        
        <button type="submit" name="deleteSong">Delete Song</button>
    </form>

</body>
</html>
