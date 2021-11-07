function myFunction() {
    var request = require('request')
    request.post('http://localhost/notify', 
    function (error, response, body) 
    {
      if (!error && response.statusCode == 200) 
      {
        console.log(body);
      }
    })
  }