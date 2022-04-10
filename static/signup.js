function email_r(e) {

    name = document.getElementById("username").value;
    email = document.getElementById("email").value

    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    const formData = new FormData();
    formData.append('name', name);
    formData.append('email', email);
    formData.append('csrfmiddlewaretoken', csrftoken);
  // console.log(formData);
    fetch("send_email", {
        headers:{'X-CSRFToken': csrftoken},
        method: 'POST',
        body: formData,
    })
}
