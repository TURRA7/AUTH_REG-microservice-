document.getElementById('recover_form').addEventListener('submit', async function(event) {
    event.preventDefault();

    const user = document.getElementById('user').value;

    try {
        const response = await fetch('/authorization/recover', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams({
                'user': user,
            }),
        });

        if (response.ok) {
            window.location.href = '/authorization/recover/reset_code';
        } else {
            const data = await response.json();
            alert(data.message);
            window.location.href = '/authorization/recover';
        }
    } catch (error) {
        console.error('Ошибка:', error);
        alert('Произошла ошибка при обработке запроса');
    }
});