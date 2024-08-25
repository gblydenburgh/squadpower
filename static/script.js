document.addEventListener('DOMContentLoaded', function() {
    const input = document.getElementById('name');
    const results = document.getElementById('results');

    input.addEventListener('input', function() {
        fetch('/search', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: input.value }),
        })
        .then(response => response.json())
        .then(data => {
            results.innerHTML = '';
            data.forEach(item => {
                const li = document.createElement('li');
                li.textContent = item[0];
                li.addEventListener('click', () => {
                    window.location.href = '/update/' + item[2];
                });
                results.appendChild(li);
            });
        });
    });
});
