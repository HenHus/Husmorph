document.getElementById('greet-btn').addEventListener('click', function() {
    // Call the Python function 'greet' and pass a parameter
    eel.greet('World')(function(response) {
      console.log(response);  // Outputs: Hello, World from Python!
      alert(response);
    });
  });
  