document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('authorization-form').addEventListener('submit', async function (event) {
        event.preventDefault();

        const login = document.getElementById('login').value;
        const password = document.getElementById('password').value;
        const rememberMe = document.getElementById('memorize-user').checked;

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
                    'rememberMe': rememberMe
                }),
            });

            const data = await response.json();
            
            if (response.status !== 200) {
                alert(data.message);
            } else {
                window.location.href = '/authorization/verification';
            }
        }
    });
});

document.getElementById("redirect_reg").onclick = function() {
    window.location.href = "/registration";
};


document.getElementById('show-password').addEventListener('change', function() {
    var passwordInput = document.getElementById('password');
    if (this.checked) {
        passwordInput.type = 'text';
    } else {
        passwordInput.type = 'password';
    }
});

document.getElementById('memorize-user').addEventListener('change', function() {
    localStorage.setItem('rememberMe', this.checked ? 'true' : 'false');
});

document.addEventListener('DOMContentLoaded', function() {
    const rememberMe = localStorage.getItem('rememberMe') === 'true';
    document.getElementById('memorize-user').checked = rememberMe;
});

document.getElementById("btn_recover").onclick = function() {
    window.location.href = "/authorization/recover";
};