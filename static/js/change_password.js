document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('change_password_form').addEventListener('submit', async function (event) {
        event.preventDefault();

        const password = document.getElementById('password').value;
        const password_two = document.getElementById('password_two').value;

        let isValid = true;

        if (!password) {
            document.getElementById('password-error').innerText = 'Введите ваш пароль!';
            isValid = false;
        } else {
            document.getElementById('password-error').innerText = '';
        }
    
        if (!password_two) {
            document.getElementById('password-two-error').innerText = 'Повторите ваш пароль!';
            isValid = false;
        } else if (password !== password_two) {
            document.getElementById('password-two-error').innerText = 'Пароли не совпадают!';
            isValid = false;
        } else {
            document.getElementById('password-two-error').innerText = '';
        }

        if (isValid) {
            const response = await fetch('/authorization/recover/reset_code/change_password', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams({
                    'password': password,
                    'password_two': password_two
                }),
            });

            const data = await response.json();
        
            if (response.status !== 200) {
                alert(data.message);
            } else {
                window.location.href = '/authorization';
            }
        }
    });
});