
  function _update_recipients(options, id){

   var select = document.getElementById("recipients-" + id + "-recipient");
   select.textContent = ""

   for(var i = 0; i < options.length; i++) {
      var opt = options[i];
      var el = document.createElement("option");
      el.textContent = opt[1];
      el.value = opt[0];
      select.appendChild(el);
    }
  }

function trigger_update(id){
  var filter = document.getElementById("recipients-" + id + "-search").value;
  fetch('/recipients?q=' + filter).
      then(
          function(response) {
              return response.json();
          }
      ).then(
          function(result) {
              _update_recipients(result.recipients, id)
          }
      );
}
