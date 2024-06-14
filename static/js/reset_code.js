document.getElementById('reset_code_form').addEventListener('submit', async function(event) {
    event.preventDefault();

    const code = document.getElementById('code').value;

    try {
        const response = await fetch('/authorization/recover/reset_code', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams({
                'code': code,
            }),
        });

        if (response.ok) {
            window.location.href = '/authorization/recover/reset_code/change_password';
        } else {
            const data = await response.json();
            alert(data.message);
            window.location.href = '/authorization/recover/reset_code';
        }
    } catch (error) {
        console.error('Ошибка:', error);
        alert('Произошла ошибка при обработке запроса');
    }
});
