<?php
session_start();
require 'config.php';
$message = "";
if ($_SERVER["REQUEST_METHOD"] == "POST") {

    $username = $_POST['username'];
    $password = $_POST['password'];
    $sql = "SELECT * FROM users WHERE username = ? AND password = ?";
    $stmt = $conn->prepare($sql);
    $stmt->bind_param("ss", $username, $password);
    $stmt->execute();
    $result = $stmt->get_result();
    if ($result->num_rows > 0) {
        $message = "Login successful! Welcome, " . htmlspecialchars($username);
    } else {
        $message = "Login failed! Invalid username or password.";
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Web Authentication Application</title>
</head>
<body>
    <div class="box">
        <h2>Login Page</h2>
        <p>Web Authentication Application</p>
        <?php if ($message != "") { ?>
            <p class="<?php echo (strpos($message, "successful") !== false) ? "success" : "failed"; ?>">
                <?php echo $message; ?>
            </p>
        <?php } ?>
        <form method="POST" action="">
            <label for="username">Username</label>
            <input type="text" name="username" id="username" required>
            <br><br>
            <label for="password">Password</label>
            
            <input type="password" name="password" id="password" required>
            <br><br>
            <button type="submit">Login</button>
        </form>
    </div>
</body>
</html>
