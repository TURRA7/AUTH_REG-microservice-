document.getElementById('verification_form').addEventListener('submit', async function(event) {
    event.preventDefault();

    const code = document.getElementById('code').value;

    try {
        const response = await fetch('/authorization/verification', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams({
                'code': code,
            }),
        });

        if (response.ok) {
            alert('Успешно!');
        } else {
            const data = await response.json();
            alert(data.message);
            window.location.href = '/authorization/verification';
        }
    } catch (error) {
        console.error('Ошибка:', error);
        alert('Произошла ошибка при обработке запроса');
    }
});
