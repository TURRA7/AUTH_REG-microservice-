document.getElementById('confirm_form').addEventListener('submit', async function(event) {
    event.preventDefault();

    const code = document.getElementById('code').value;

    try {
        const response = await fetch('/registration/confirm', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams({
                'code': code,
            }),
        });

        if (response.ok) {
            alert('Регистрация успешна!');
            window.location.href = '/authorization';
        } else {
            const data = await response.json();
            alert(data.message);
            window.location.href = '/registration/confirm';
        }
    } catch (error) {
        console.error('Ошибка:', error);
        alert('Произошла ошибка при обработке запроса');
    }
});
