
  function _update_recipients(options){

   var select = document.getElementById("recipient");
   select.textContent = ""

   for(var i = 0; i < options.length; i++) {
      var opt = options[i];
      var el = document.createElement("option");
      el.textContent = opt[1];
      el.value = opt[0];
      select.appendChild(el);
    }
  }

function _test(){
  var filter = document.getElementById("search").value;
  fetch('/recipients/' + filter).
      then(
          function(response) {
              return response.json();
          }
      ).then(
          function(result) {
              console.log(result.recipients);
              _update_recipients(result.recipients)
          }
      );
}
