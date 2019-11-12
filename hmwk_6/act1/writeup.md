[reflected]: ./reflected.png "Reflected XSS in Search Bar"
[stored]: ./stored.png "Stored XSS in the Posts"
# XSS On Armbook
------------------

## Reflected XSS

The first type of XSS is reflected XSS. The issue is in the `search` bar of the application. The problem is that the input into the `search` bar is not being sanatized at all. If we do not include any spaces in the `<script>...</script>` payload in the search bar, the JS will make it all the way through the PHP without being modified. It will then be rendered on the page as _HTML_ which will cause the browser to execute the JS. We cannot include spaces in the payload because the PHP `explodes()` the input and grabs the _first_ and _second_ items assuming they will be a first and last name. 

### Example Payload
> `<script>alert("SearchBarDoesNotLikeSpaces")</script>`

![reflected]

------------------

## Stored XSS

The second type of XSS is stored XSS. The issue is in the `Posts` section of the page. The problem is that the input into the `Posts` section is not sanatized at all. The comments are directly written to the database without being modified. When being displayed, the comments are directly read from the database, and displayed as _HTML_ which causes the browser to execute the JS in the comment. The only restriction here is the 300 character limit that the comment box sets.

### Example Payload
> `<script>alert("I wish we could delete posts")</script>`

![stored]

------------------