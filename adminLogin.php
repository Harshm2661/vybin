<?php
    // Include the existing configuration file
    include("Includes/config.php");

    // Example of admin login handling
    if(isset($_POST['adminLoginButton'])) {
        $adminUsername = $_POST['adminUsername'];
        $adminPassword = $_POST['adminPassword'];

        $query = mysqli_query($con, "SELECT * FROM Admins WHERE username='$adminUsername'");

        if(mysqli_num_rows($query) == 1) {
            $row = mysqli_fetch_assoc($query);

            if(password_verify($adminPassword, $row['password'])) {
                // Login successful
                $_SESSION['adminLoggedIn'] = $adminUsername;
                header("Location: adminDashboard.php");
                exit();
            } else {
                echo "Incorrect password.";
            }
        } else {
            echo "Admin username not found.";
        }
    }
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Admin Login</title>
    <link rel="stylesheet" type="text/css" href="assets\css\register.css">
</head>
<body>

    <div id="background">

        <div id="loginContainer">

            <div id="inputContainer">
            <form id="loginForm" action="Includes/Handlers/adminLogin-handler.php" method="POST">
    <h2>Admin Login</h2>
    <p>
        <label for="loginUsername">Username</label>
        <input id="loginUsername" name="loginUsername" type="text" placeholder="e.g. admin123" required>
    </p>
    <p>
        <label for="loginPassword">Password</label>
        <input id="loginPassword" name="loginPassword" type="password" placeholder="Your password" required>
    </p>
    <button type="submit" name="loginButton">LOG IN</button>
</form>

            </div>

            <div id="loginText">
                <h1>Admin Login</h1>
                <h2>Welcome back!</h2>
            </div>

        </div>

    </div>

</body>
</html>
