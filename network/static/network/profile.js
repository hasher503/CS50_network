document.addEventListener('DOMContentLoaded', function() {
    load_followers()
    document.querySelector('#followbtn').addEventListener('click', follow)

})

function follow(){
    const button = document.querySelector('#followbtn')
    const targetuser = document.querySelector('#target_user').dataset.username
    if (button.innerHTML == 'Follow') {
            // request user to follow target user
            fetch(`/follow/${targetuser}`, {
            method: 'PUT',
            body: JSON.stringify({
                addfollow: true
            })
        })
        .then(() => load_followers())
    } else if (button.innerHTML == 'Unfollow') {
        // request user will unfollow target user
        fetch(`/follow/${targetuser}`, {
            method: 'PUT',
            body: JSON.stringify({
                unfollow: true
            })
        })
        .then(() => load_followers())
    }
}


function load_followers() {
    const targetuser = document.querySelector('#target_user').dataset.username
    fetch(`/follow/${targetuser}`)
    .then(response => response.json())
    .then(data => {
        // update followers count, following count, and button
        document.querySelector('#following_count').innerHTML = `<b>${data.followingnum}</b> Following`
        document.querySelector('#followers_count').innerHTML = `<b>${data.followersnum}</b> Followers`
        if (data.followbool) {
            document.querySelector('#followbtn').innerHTML = 'Unfollow'
        } else {
            document.querySelector('#followbtn').innerHTML = 'Follow'
        }
    })
}