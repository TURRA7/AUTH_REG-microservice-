document.getElementById('registration-form').addEventListener('submit', async function (event) {
    event.preventDefault();
    
    const login = document.getElementById('login').value;
    const password = document.getElementById('password').value;
    const passwordTwo = document.getElementById('password_two').value;
    
    let isValid = true;

    if (!login) {
        document.getElementById('login-error').innerText = 'Введите ваш логин';
        isValid = false;
    } else {
        document.getElementById('login-error').innerText = '';
    }

    if (!password) {
        document.getElementById('password-error').innerText = 'Введите ваш пароль';
        isValid = false;
    } else {
        document.getElementById('password-error').innerText = '';
    }

    if (!passwordTwo) {
        document.getElementById('password-two-error').innerText = 'Повторите ваш пароль';
        isValid = false;
    } else {
        document.getElementById('password-two-error').innerText = '';
    }

    if (password !== passwordTwo) {
        document.getElementById('password-two-error').innerText = 'Пароли не совпадают';
        isValid = false;
    }

    if (login.length < 7) {
        document.getElementById('login-error').innerText = 'Логин слишком короткий';
        isValid = false;
    }

    if (password.length < 10) {
        document.getElementById('password-error').innerText = 'Пароль слишком короткий';
        isValid = false;
    }

    if (isValid) {
        const response = await fetch('/registration', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams({
                'login': login,
                'password': password,
                'password_two': passwordTwo,
            }),
        });

        const data = await response.json();
        
        if (response.status !== 200) {
            alert(data.message);
        } else {
            alert('Регистрация успешна!');
        }
    }
});