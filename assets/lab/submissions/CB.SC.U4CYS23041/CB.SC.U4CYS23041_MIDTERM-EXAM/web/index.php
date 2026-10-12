<?php

$conn = new mysqli("localhost", "midterm_user", "midterm_pass", "midterm_db");

if ($conn->connect_error) {
    die("Database connection failed");
}

if (isset($_POST['login'])) {

    $username = $_POST['username'];
    $password = $_POST['password'];

    $sql = "SELECT * FROM users WHERE username='$username' AND password='$password'";

    $result = $conn->query($sql);

    if ($result->num_rows > 0) {
        echo "<h2>Login Successful</h2>";
        echo "Welcome " . $username;
    } else {
        echo "<h2>Login Failed</h2>";
        echo "Invalid Username or Password";
    }
}

?>

<!DOCTYPE html>
<html>

<head>
    <title>Web Authentication</title>
</head>

<body>

<h1>Web Authentication Application</h1>

<h2>Login Page</h2>

<form method="POST">

    Username:
    <input type="text" name="username">

    <br><br>

    Password:
    <input type="password" name="password">

    <br><br>

    <input type="submit" name="login" value="Login">

</form>

</body>

</html>
