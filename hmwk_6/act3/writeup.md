[newpassword]: ./newpassword.png "New password for Andy"
[oldpassword]: ./oldpasswordPost.png "Andy's old password"

# Changing Andy's Password
--------------------------

## How to change the admin password

I found a hidden page at `/admin/admin.php` which shows all users and their passwords. I found that if I submit a post request to `/admin/adduser.php` I can change a current user's password.

`$.post("/admin/adduser.php", {email: "andy@culler.com", password: "oneNutW0nder"});`

Here is the post on my page with Andy's password: _thisisgoodpasslol_
![oldpassword]

--------------------------

Here is the updated password: _oneNutW0nder_
![newpassword]

