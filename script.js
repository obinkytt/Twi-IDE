function insertChar(char) {
    const textarea = document.getElementById('code');
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const text = textarea.value;
    textarea.value = text.substring(0, start) + char + text.substring(end);
    textarea.focus();
    textarea.selectionEnd = start + char.length;
}

function toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
}

function runCode() {
    const code = document.getElementById('code').value;
    fetch('/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code: code })
    })
    .then(res => res.json())
    .then(data => {
        document.getElementById('output').innerText = data.output;
    });
}
