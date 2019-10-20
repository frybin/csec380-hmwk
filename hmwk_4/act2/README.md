[proof]: ./proof.png
# How I Got _Jon Doe_ to be Friends With Me

First, after studying the `add_friend.php` script, I noticed that the script took an `id` parameter. This `id` parameter is used as the id of the account you want to friend. After seeing this, I made this link:

> http://csec380-core.csec.rit.edu:84/add_friend.php?id=36

And posted it to the message board. My username:

> oneNutW0nder reee :: id=36

![Friends][proof]


# How I Fixed This Issue

This issue can be fixed by implementing CSRF tokens. These tokens will be generated when a user logs in, and they  will be sent with each request. When the request reaches its destination (application endpoints) the token sent with the request will be checked against the token generated for the session.

__Files Edited__  
> login.php -- Generate a token when successful login occurs  
> home.php -- Added tokens to requests to add/del_friend.php  
> search.php -- Added tokens to requests to add/del_friend.php  
> add_friend.php -- Check session token against request token  
> del_friend.php -- Check session token against request token   

Now, if I send the same link to _Jon Doe_ he will not be able to friend me because a token is not included in his request.
