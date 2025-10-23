// /static/js/script.js

// Система логирования
const DEBUG_LEVEL = 0; // 0 - нет логов, 1 - ошибки, 2 - предупреждения, 3 - все логи

function logError(...args) {
    if (DEBUG_LEVEL >= 1) {
        console.error('❌', ...args);
    }
}

function logWarning(...args) {
    if (DEBUG_LEVEL >= 2) {
        console.warn('⚠️', ...args);
    }
}

function logInfo(...args) {
    if (DEBUG_LEVEL >= 3) {
        console.log('ℹ️', ...args);
    }
}

function logSuccess(...args) {
    if (DEBUG_LEVEL >= 2) {
        console.log('✅', ...args);
    }
}

// Обработка кликов по вкладкам
document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', () => showTab(tab.dataset.tab));
});

// Функция отображения выбранной вкладки
function showTab(tabName) {
    document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
    document.querySelectorAll('.form').forEach(form => form.classList.remove('active'));

    document.querySelector(`.tab[data-tab="${tabName}"]`).classList.add('active');
    document.getElementById(`${tabName}-form`).classList.add('active');
}

// Инициализация обработчиков событий после загрузки DOM
document.addEventListener('DOMContentLoaded', function() {
    logInfo('Инициализация обработчиков форм...');
    
    // Обработчики для форм
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('registration-form');
    
    if (loginForm) {
        logInfo('Найдена форма логина');
        loginForm.addEventListener('submit', loginFunction);
    } else {
        logError('Форма логина не найдена');
    }
    
    if (registerForm) {
        logInfo('Найдена форма регистрации');
        registerForm.addEventListener('submit', regFunction);
    } else {
        logError('Форма регистрации не найдена');
    }
    
    logInfo('Все формы инициализированы');
});

async function regFunction(event) {
    logInfo('Обработка регистрации...');
    event.preventDefault();

    const form = event.target;
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());

    logInfo('Данные регистрации:', data);

    // Клиентская проверка совпадения паролей
    if (data.user_pass !== data.user_pass_check) {
        showNotification('Пароли не совпадают!', 'error');
        return;
    }

    try {
        logInfo('Отправка запроса регистрации...');
        const response = await fetch('/users/register/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data),
            credentials: 'include'
        });

        logInfo('Ответ регистрации:', response.status);

        if (!response.ok) {
            const errorData = await response.json();
            logError('Ошибка регистрации:', errorData);
            displayErrors(errorData);
            return;
        }

        const result = await response.json();
        logSuccess('Успешная регистрация:', result);

        if (result.message) {
            showNotification(result.message, 'success');
            setTimeout(() => {
                showTab('login');
            }, 2000);
        } else {
            showNotification(result.message || 'Неизвестная ошибка', 'error');
        }
    } catch (error) {
        logError('Ошибка сети при регистрации:', error);
        showNotification('Произошла ошибка при регистрации. Пожалуйста, попробуйте снова.', 'error');
    }
}

async function loginFunction(event) {
    logInfo('Обработка авторизации...');
    event.preventDefault();

    const form = event.target;
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());

    logInfo('Данные авторизации:', { user_email: data.user_email });

    try {
        logInfo('Отправка запроса авторизации...');
        const response = await fetch('/users/login/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data),
            credentials: 'include'
        });

        logInfo('Ответ авторизации:', response.status, response.statusText);

        // Получаем текст ответа для отладки
        const responseText = await response.text();
        logInfo('Текст ответа:', responseText);

        // Пытаемся распарсить JSON
        let result;
        try {
            result = JSON.parse(responseText);
        } catch (parseError) {
            logError('Ошибка парсинга JSON:', parseError);
            showNotification('Неверный формат ответа от сервера', 'error');
            return;
        }

        if (!response.ok) {
            logError('Ошибка авторизации:', result);
            displayErrors(result);
            return;
        }

        logSuccess('Успешная авторизация:', result);

        // Проверяем успешность разными способами
        if (result.ok === true || result.message || result.user_id) {
            showNotification(result.message || 'Авторизация успешна!', 'success');
            logSuccess('Выполняем редирект на:', result.redirect_url || '/lk/plist');
            
            setTimeout(() => {
                window.location.href = result.redirect_url || '/lk/plist';
            }, 1000);
        } else {
            logWarning('Непонятный ответ от сервера:', result);
            showNotification(result.message || 'Неизвестная ошибка', 'error');
        }
    } catch (error) {
        logError('Ошибка сети при авторизации:', error);
        showNotification('Произошла ошибка при входе. Пожалуйста, попробуйте снова.', 'error');
    }
}

// Функция для отображения ошибок
function displayErrors(errorData) {
    let message = 'Произошла ошибка';

    if (errorData && errorData.detail) {
        if (Array.isArray(errorData.detail)) {
            message = errorData.detail.map(error => {
                if (error.type === 'string_too_short') {
                    return `Поле "${error.loc[1]}" должно содержать минимум ${error.ctx.min_length} символов.`;
                }
                return error.msg || 'Произошла ошибка';
            }).join('\n');
        } else {
            message = errorData.detail || 'Произошла ошибка';
        }
    }

    showNotification(message, 'error');
}

// Функция показа уведомлений
function showNotification(message, type) {
    // Удаляем существующие уведомления
    const existingNotifications = document.querySelectorAll('.notification');
    existingNotifications.forEach(notification => notification.remove());

    // Создаем элемент уведомления
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        border-radius: 8px;
        color: white;
        z-index: 1000;
        font-weight: bold;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        ${type === 'success' ? 'background: #28a745;' : 'background: #dc3545;'}
    `;
    
    document.body.appendChild(notification);
    
    // Удаляем уведомление через 4 секунды
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 4000);
}

// Функции для других страниц
async function logoutUser() {
    try {
        const response = await fetch('/users/logout/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include'
        });

        if (response.ok) {
            showNotification('Выход выполнен успешно', 'success');
            setTimeout(() => {
                window.location.href = '/';
            }, 1000);
        } else {
            const errorData = await response.json();
            logError('Ошибка при выходе:', errorData);
            showNotification('Ошибка при выходе', 'error');
        }
    } catch (error) {
        logError('Ошибка сети', error);
        showNotification('Ошибка сети', 'error');
    }
}

// Управление сервисами (для личного кабинета)
async function manageService(action, serviceId) {
    try {
        logInfo(`Управление сервисом: ${action} для ID: ${serviceId}`);
        const response = await fetch(`/services/${serviceId}/${action}`, { 
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include'
        });

        if (response.ok) {
            showNotification(`Сервис успешно ${getActionText(action)}`, 'success');
            setTimeout(() => {
                window.location.reload();
            }, 2000);
        } else {
            const errorData = await response.json();
            logError('Ошибка управления сервисом:', errorData);
            showNotification(errorData.detail || 'Ошибка при выполнении действия', 'error');
        }
    } catch (error) {
        logError('Error:', error);
        showNotification('Ошибка сети', 'error');
    }
}

function getActionText(action) {
    const actions = {
        'start': 'запущен',
        'stop': 'остановлен', 
        'restart': 'перезапущен'
    };
    return actions[action] || 'обновлен';
}

// Инициализация обработчиков для личного кабинета
document.addEventListener('DOMContentLoaded', function() {
    // Обработчики для кнопок управления сервисами
    document.querySelectorAll('.service-actions button[data-action]').forEach(button => {
        button.addEventListener('click', function() {
            const action = this.getAttribute('data-action');
            const serviceId = this.getAttribute('data-service-id');
            manageService(action, serviceId);
        });
    });
});