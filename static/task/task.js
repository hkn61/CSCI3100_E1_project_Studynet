// Create a new list item when clicking on the "Add" button
function newElement() {
  var li = document.createElement("li");
  var inputValue = document.getElementById("myInput").value;
  var t = document.createTextNode(inputValue);
  li.appendChild(t);
  if (inputValue === '') {
    alert("You must write something!");
  } else {
    document.getElementById("myUL").appendChild(li);
  }
  document.getElementById("myInput").value = "";

  var span = document.createElement("SPAN");
  var txt = document.createTextNode("\u00D7");
  span.className = "close";
  span.appendChild(txt);

  li.appendChild(span);


  const formData = new FormData();
  formData.append('taskname', inputValue);
  formData.append('csrfmiddlewaretoken', csrftoken);

  fetch("inserttask", {
    headers:{'X-CSRFToken': csrftoken},
    credentials: 'same-origin',
    method: 'POST',
    body: formData,
  })

  for (i = 0; i < close.length; i++) {
    close[i].onclick = function() {
      var div = this.parentElement;
      div.style.display = "none";
    }
  }
}