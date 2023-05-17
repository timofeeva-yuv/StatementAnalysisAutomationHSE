function drawTextOne(canvas, constantValue) {
    var ctx = canvas.getContext('2d');
  // Clear the canvas
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // Calculate the font size based on the canvas width
  var fontSize = canvas.width * 0.1; // Adjust the scaling factor as needed

  // Set the font style for the text
  ctx.font = fontSize + 'px Arial';

  // Set the text color
  ctx.fillStyle = 'black';

  // Calculate the position for centering the text
  var x = canvas.width / 2;
  var y = canvas.height / 2;

  // Draw the constant value on the canvas
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText(constantValue, x, y);
}

function handleResizeOne(canvas, constantValue) {
    // Set the canvas dimensions to match the container size
  canvas.width = canvas.parentNode.offsetWidth;
  canvas.height = canvas.parentNode.offsetHeight;

  // Call the drawText function to redraw the text with the updated size
  drawTextOne(canvas, constantValue);
}