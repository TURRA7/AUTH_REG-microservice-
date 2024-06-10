document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('authorization-form').addEventListener('submit', async function (event) {
        event.preventDefault();

        const login = document.getElementById('login').value;
        const password = document.getElementById('password').value;

        let isValid = true;

        if (!login) {
            document.getElementById('login-error').innerText = 'Введите ваш логин!';
            isValid = false;
        } else {
            document.getElementById('login-error').innerText = '';
        }

        if (!password) {
            document.getElementById('password-error').innerText = 'Введите пароль!';
            isValid = false;
        } else {
            document.getElementById('password-error').innerText = '';
        }

        if (isValid) {
            const response = await fetch('/authorization', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams({
                    'login': login,
                    'password': password,
                }),
            });

            const data = await response.json();
            
            if (response.status !== 200) {
                alert(data.message);
            } else {
                alert('Авторизация успешна!');
            }
        }
    });
});