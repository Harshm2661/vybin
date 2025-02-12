<?php
    // Include the necessary configuration
    include("../config.php");
    include("../Classes/Account.php");
    include("../Classes/Constants.php");

    $account = new Account($con);

    if (isset($_POST["loginButton"])) {
        $username = $_POST['loginUsername'];
        $password = $_POST['loginPassword'];

        $result = $account->login($username, $password);

        if ($result) {
            // Assuming admin login will have a different session identifier
            $_SESSION['adminLoggedIn'] = $username;
            header("Location: ../../adminDashboard.php");
        } else {
            // Redirect back with an error message (this part can be customized)
            header("Location: ../../adminLogin.php?error=login_failed");
        }
    }
?>
