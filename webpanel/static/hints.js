function getHints(inputText, hintsContainer, table) {
  // Make an AJAX request to the Django view
  const xhr = new XMLHttpRequest();
  xhr.onreadystatechange = function() {
    if (xhr.readyState === XMLHttpRequest.DONE) {
      if (xhr.status === 200) {
        const hints = JSON.parse(xhr.responseText);
        // Populate the hints in the UI
        displayHints(hints, hintsContainer);
      } else {
        console.error('Error:', xhr.status);
      }
    }
  };
  const encodedInputText = encodeURIComponent(inputText);  // URL encode the inputText
  const url = '/get-hints/?input_text=' + encodedInputText + '&table=' + table;
  xhr.open('GET', url);
  xhr.send();
}

function displayHints(hints, hintsContainer) {
  // Clear previous hints and display new hints
  hintsContainer.innerHTML = '';

  hints.forEach(function(hint) {
    const hintItem = document.createElement('div');
    hintItem.textContent = hint;
    hintItem.addEventListener('click', function() {
      populateInputField(hint, hintsContainer);
    });
    hintsContainer.appendChild(hintItem);
  });
}

function populateInputField(value, hintsContainer) {
  const inputField = document.getElementById('input-field');
  const inputValue = inputField.value;
  const inputText = inputValue.trim();
  const words = inputText.split(' ');
  const lastChar = inputValue.charAt(inputValue.length - 1);
  if (lastChar !== ' ') {
    const lastWordIndex = words.length - 1;
    words[lastWordIndex] = value;
  } else {
    words.push(value);
  }
  const updatedInputText = words.join(' ');
  inputField.value = updatedInputText;
}



document.addEventListener('DOMContentLoaded', function() {
  // Get the input, hints, and table container elements
  const input = document.getElementById('input-field');
  const hintsContainer = document.getElementById('hints-container');
  const tableContainer = document.getElementById('id_database_table');

  // Event listener for input field focus
  input.addEventListener('focus', function() {
    const inputText = input.value;
    getHints(inputText, hintsContainer, tableContainer.value);
  });

  // Event listener for input field blur
  input.addEventListener('blur', function() {
    // Hide hints after a slight delay to allow click events to trigger
    setTimeout(function() {
      hintsContainer.innerHTML = '';
    }, 200);
  });

  // Event listener for input field input
  input.addEventListener('input', function() {
    const inputText = input.value;
    getHints(inputText, hintsContainer, tableContainer.value);
  });
});
