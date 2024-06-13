document.getElementById('registration-form').addEventListener('submit', async function (event) {
    event.preventDefault();

    const email = document.getElementById('email').value;
    const login = document.getElementById('login').value;
    const password = document.getElementById('password').value;
    const passwordTwo = document.getElementById('password_two').value;

    const emailPattern = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    const loginPattern = /^(?=.*[A-Z])(?=.*\d).+$/
    const passwordPattern = /^(?=.*[A-Z])(?=.*\d)(?=.*[_\-]).+$/;
    
    let isValid = true;

    if (!email) {
        document.getElementById('email-error').innerText = 'Введите вашу почту!';
        isValid = false;
    } else if (!emailPattern.test(email)) {
        document.getElementById('email-error').innerText = 'Введите правильную почту!';
        isValid = false;
    } else {
        document.getElementById('email-error').innerText = '';
    }

    if (!login) {
        document.getElementById('login-error').innerText = 'Введите ваш логин!';
        isValid = false;
    } else if (login.length < 5) {
        document.getElementById('login-error').innerText = 'Логин слишком короткий!';
        isValid = false;
    } else if (!loginPattern.test(login)) {
        document.getElementById('login-error').innerText = 'Логин должен содержать заглавные буквы, цифры и символы "_" или "-"';
        isValid = false;
    } else {
        document.getElementById('login-error').innerText = '';
    }

    if (!password) {
        document.getElementById('password-error').innerText = 'Введите ваш пароль!';
        isValid = false;
    } else if (password.length < 7) {
        document.getElementById('password-error').innerText = 'Пароль слишком короткий!';
        isValid = false;
    } else if (!passwordPattern.test(password)) {
        document.getElementById('password-error').innerText = 'Пароль должен содержать заглавные буквы, цифры и специальные символы!';
        isValid = false;
    } else {
        document.getElementById('password-error').innerText = '';
    }

    if (!passwordTwo) {
        document.getElementById('password-two-error').innerText = 'Повторите ваш пароль!';
        isValid = false;
    } else if (password !== passwordTwo) {
        document.getElementById('password-two-error').innerText = 'Пароли не совпадают!';
        isValid = false;
    } else {
        document.getElementById('password-two-error').innerText = '';
    }

    if (isValid) {
        const response = await fetch('/registration', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams({
                'email': email,
                'login': login,
                'password': password,
                'password_two': passwordTwo,
            }),
        });

        const data = await response.json();
        
        if (response.status !== 200) {
            alert(data.message);
        } else {
            window.location.href = '/registration/confirm';
        }
    }
});
