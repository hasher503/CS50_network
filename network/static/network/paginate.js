document.addEventListener('DOMContentLoaded', () => {
    // addd listener to all Like buttons
    document.querySelectorAll('.fa-thumbs-up').forEach(btn => {
        btn.onclick = like
    })
    // add event listener to all edit buttons
    document.querySelectorAll('.edit').forEach(btn => {
        btn.onclick = edit
    })
})

function like() {
    const pk = this.parentElement.getAttribute('id')
    // if already liked, change to un-liked, and vice versa
    if (this.className === "fa fa-thumbs-up btn btn-danger") {
        this.className = "fa fa-thumbs-up btn btn-outline-danger"
    } else {
        this.className = "fa fa-thumbs-up btn btn-danger"
    }
    fetch(`/like/${pk}`, {
        method: 'PUT',
        body: JSON.stringify({
            pk: pk
        })
    })
    .then(response => response.json())
    // update likes number within button
    .then(data => {
        this.innerHTML = ` ${data.likenum}`
    })
}

function edit() {
    // get current post text from primary key stored in parent div's ID
    // (there must be a smarter way to create these elements??)
    const pk = this.parentElement.getAttribute('id')
    const submitbtn = document.createElement('button')
    submitbtn.disabled = 'true'
    submitbtn.className = 'btn btn-sm btn-warning'
    submitbtn.innerHTML = 'Submit'
    const body = document.getElementById(`${pk}-body`)
    const editbox = document.createElement('textarea')
    editbox.value = body.innerHTML
    editbox.maxLength = 280
    editbox.className = 'editbox'

    // hide post body and show textarea for editing
    body.style.display = 'none'
    document.getElementById(`${pk}-body`).parentElement.append(editbox)
    this.style.display = 'none'
    this.parentElement.append(submitbtn)

    // enable submit button if there is text in editbox (on focus and on key up)
    editbox.onfocus = () => checkcontent(editbox, submitbtn)
    editbox.onkeyup = () => checkcontent(editbox, submitbtn)

    submitbtn.onclick = () => {
        // https://www.w3schools.com/jsref/jsref_trim_string.asp
        newtext = editbox.value.trim()

        fetch(`/update/${pk}`, {
            method: 'PUT',
            body: JSON.stringify({
                pk: pk,
                newtext: newtext
            })
        })
        .then(response => response.json())
        .then(data => {
            // if promise not resolved with success, return alert
            if (data.message == undefined) {
                alert('Something went wrong')
            } else {
                submitbtn.style.display = 'none'
                this.style.display = 'inline'
                editbox.remove()
                submitbtn.remove()
                body.innerHTML = newtext
                body.style.display = 'block'
            }
        })
    }
}

function checkcontent (input, button) {
       // enable submit only if there is text in the input field
       if (input.value === "") {
        button.disabled = true
    } else {
        button.disabled = false
    }
}