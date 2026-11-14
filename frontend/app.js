const API_BASE = '/cosmetology';

let allCategories = [];
let currentUser = null;

// --- Утилиты ---
function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), 4500);
}

function getTokens() {
    return {
        access: localStorage.getItem('access_token'),
        refresh: localStorage.getItem('refresh_token')
    };
}

function saveTokens(access, refresh) {
    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);
}

function clearAuth() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    currentUser = null;
}

// Обертка над fetch с автоматической ротацией токенов при 401
async function apiFetch(endpoint, options = {}, retry = true) {
    const tokens = getTokens();
    const headers = {
        'Content-Type': 'application/json',
        ...(options.headers || {})
    };

    if (tokens.access) {
        headers['Authorization'] = `Bearer ${tokens.access}`;
    }

    const response = await fetch(`${API_BASE}${endpoint}`, {
        ...options,
        headers
    });

    if (response.status === 401 && retry && tokens.refresh) {
        const refreshed = await tryRefreshTokens();
        if (refreshed) {
            return apiFetch(endpoint, options, false);
        } else {
            clearAuth();
            renderApp();
        }
    }

    return response;
}

async function tryRefreshTokens() {
    const tokens = getTokens();
    if (!tokens.refresh) return false;

    try {
        const res = await fetch(`${API_BASE}/rotation`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh_token: tokens.refresh })
        });
        if (!res.ok) return false;
        const data = await res.json();
        saveTokens(data.access_token, data.refresh_token);
        return true;
    } catch {
        return false;
    }
}

// --- Инициализация и роутинг интерфейса ---
async function initApp() {
    const tokens = getTokens();
    if (tokens.access) {
        try {
            const res = await apiFetch('/me');
            if (res.ok) {
                currentUser = await res.json();
            } else {
                clearAuth();
            }
        } catch {
            clearAuth();
        }
    }
    renderApp();
}

function renderApp() {
    const nav = document.getElementById('nav-menu');
    const authSec = document.getElementById('auth-section');
    const clientSec = document.getElementById('client-section');
    const adminSec = document.getElementById('admin-section');

    authSec.classList.add('hidden');
    clientSec.classList.add('hidden');
    adminSec.classList.add('hidden');

    if (!currentUser) {
        nav.innerHTML = `<span class="user-badge">Онлайн-запись 24/7</span>`;
        authSec.classList.remove('hidden');
        return;
    }

    const roleLabel = currentUser.role === 'admin' ? 'Администратор' : 'Клиент';
    nav.innerHTML = `
        <span class="user-badge">${currentUser.name} ${currentUser.surname} (${roleLabel})</span>
        <button class="btn btn-outline" id="logout-btn">Выйти</button>
    `;
    document.getElementById('logout-btn').addEventListener('click', () => {
        clearAuth();
        renderApp();
        showToast('Вы вышли из аккаунта');
    });

    if (currentUser.role === 'admin') {
        adminSec.classList.remove('hidden');
        loadAdminEntries();
    } else {
        clientSec.classList.remove('hidden');
        loadCategories();
        loadMyEntries();
    }
}

// --- Авторизация и регистрация ---
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const tab = btn.dataset.tab;
        document.getElementById('login-form').classList.toggle('hidden', tab !== 'login');
        document.getElementById('register-form').classList.toggle('hidden', tab !== 'register');
    });
});

document.getElementById('login-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const phone = document.getElementById('login-phone').value.trim();
    const password = document.getElementById('login-password').value;

    const res = await fetch(`${API_BASE}/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone, password })
    });

    const data = await res.json();
    if (!res.ok) {
        showToast(data.detail || 'Ошибка входа', 'error');
        return;
    }

    saveTokens(data.access_token, data.refresh_token);
    await initApp();
    showToast('Добро пожаловать!');
});

document.getElementById('register-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const payload = {
        name: document.getElementById('reg-name').value.trim(),
        surname: document.getElementById('reg-surname').value.trim(),
        phone: document.getElementById('reg-phone').value.trim(),
        email: document.getElementById('reg-email').value.trim(),
        password: document.getElementById('reg-password').value
    };

    const res = await fetch(`${API_BASE}/registration`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });

    const data = await res.json();
    if (!res.ok) {
        const msg = Array.isArray(data.detail) ? data.detail[0].msg : data.detail;
        showToast(msg || 'Ошибка регистрации', 'error');
        return;
    }

    showToast('Регистрация успешна! Теперь войдите в аккаунт.');
    document.querySelector('.tab-btn[data-tab="login"]').click();
    document.getElementById('login-phone').value = payload.phone;
});

/// --- Клиент: Каталог и запись ---
document.querySelectorAll('.dash-tab').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.dash-tab').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const view = btn.dataset.view;
        document.getElementById('catalog-view').classList.toggle('hidden', view !== 'catalog');
        document.getElementById('my-entries-view').classList.toggle('hidden', view !== 'my-entries');
        document.getElementById('profile-view').classList.toggle('hidden', view !== 'profile');
        if (view === 'my-entries' || view === 'profile') loadMyEntries();
    });
});

async function loadCategories() {
    const res = await apiFetch('/categories');
    if (!res.ok) return;
    allCategories = await res.json();

    const filters = document.getElementById('category-filters');
    filters.innerHTML = `<button class="cat-chip active" data-cat="all">Все услуги</button>` +
        allCategories.map(c => `<button class="cat-chip" data-cat="${c.id}">${c.name}</button>`).join('');

    filters.querySelectorAll('.cat-chip').forEach(chip => {
        chip.addEventListener('click', () => {
            filters.querySelectorAll('.cat-chip').forEach(c => c.classList.remove('active'));
            chip.classList.add('active');
            renderProcedures(chip.dataset.cat);
        });
    });

    renderProcedures('all');
}

function renderProcedures(catId) {
    const grid = document.getElementById('procedures-grid');
    let items = [];

    allCategories.forEach(cat => {
        if (catId === 'all' || String(cat.id) === String(catId)) {
            cat.procedures.forEach(proc => items.push({ ...proc, categoryName: cat.name }));
        }
    });

    grid.innerHTML = items.map(p => `
        <div class="proc-card">
            <div>
                <div class="proc-category-tag">${p.categoryName}</div>
                <h3>${p.name}</h3>
                <p class="proc-desc">${p.description}</p>
            </div>
            <div class="proc-footer">
                <span class="proc-price">${p.price.toLocaleString('ru-RU')} ₽</span>
                <button class="btn btn-primary" onclick="openBookingModal(${p.id}, '${p.name.replace(/'/g, "\\'")}', ${p.price})">Записаться</button>
            </div>
        </div>
    `).join('');
}

// Модальное окно записи
function openBookingModal(id, name, price) {
    document.getElementById('booking-proc-id').value = id;
    document.getElementById('modal-proc-title').textContent = name;
    document.getElementById('modal-proc-price').textContent = `Стоимость: ${price.toLocaleString('ru-RU')} ₽`;

    const dateInput = document.getElementById('booking-date');
    const today = new Date();
    const maxDate = new Date();
    maxDate.setDate(today.getDate() + 30);

    dateInput.min = today.toISOString().split('T')[0];
    dateInput.max = maxDate.toISOString().split('T')[0];
    dateInput.value = dateInput.min;

    document.getElementById('booking-modal').classList.remove('hidden');
}

document.getElementById('modal-close').addEventListener('click', () => {
    document.getElementById('booking-modal').classList.add('hidden');
});

document.getElementById('booking-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const payload = {
        procedure_id: Number(document.getElementById('booking-proc-id').value),
        entry_date: document.getElementById('booking-date').value,
        entry_time: document.getElementById('booking-time').value
    };

    const res = await apiFetch('/new_entry', {
        method: 'POST',
        body: JSON.stringify(payload)
    });

    const data = await res.json();
    if (!res.ok) {
        const msg = Array.isArray(data.detail) ? data.detail[0].msg : data.detail;
        showToast(msg || 'Не удалось создать запись', 'error');
        return;
    }

    document.getElementById('booking-modal').classList.add('hidden');

    showToast(data.message || 'Вы успешно записаны!');
    loadMyEntries();
});

async function loadMyEntries() {
    const res = await apiFetch('/my_entries');
    if (!res.ok) return;
    const entries = await res.json();

    // Заполняем карточку "Личные данные" во вкладке "Мой профиль"
    const profileCard = document.getElementById('client-profile-card');
    if (profileCard && currentUser) {
        profileCard.innerHTML = `
            <div class="profile-info">
                <h3>${currentUser.name} ${currentUser.surname}</h3>
                <div class="profile-details">
                    <span>Телефон: <strong>${currentUser.phone}</strong></span>
                    <span>Email: <strong>${currentUser.email || 'Не указан'}</strong></span>
                    <span>Номер карты клиента: <strong>#${currentUser.id}</strong></span>
                </div>
            </div>
            <div class="profile-stats">
                <span class="profile-stats-num">${entries.length}</span>
                <span class="profile-stats-label">Активных записей</span>
            </div>
        `;
    }

    const list = document.getElementById('my-entries-list');

    if (entries.length === 0) {
        list.innerHTML = `<p class="entry-meta">У вас пока нет активных записей.</p>`;
        return;
    }

    list.innerHTML = entries.map(e => `
        <div class="entry-item">
            <div>
                <strong>${e.name_procedures}</strong>
                <div class="entry-meta">Дата: ${e.entry_date} | Время: ${e.entry_time.slice(0, 5)} | Стоимость: ${e.price} ₽</div>
            </div>
            <button class="btn btn-danger" onclick="cancelMyEntry(${e.id})">Отменить</button>
        </div>
    `).join('');
}

async function cancelMyEntry(id) {
    const res = await apiFetch(`/my_entries/${id}`, { method: 'DELETE' });
    if (res.ok) {
        showToast('Запись отменена');
        loadMyEntries();
    } else {
        showToast('Ошибка при отмене записи', 'error');
    }
}

// --- Администратор: Управление всеми записями ---
async function loadAdminEntries(dateFilter = '') {
    const url = dateFilter ? `/get_entries?date=${dateFilter}T00:00:00` : '/get_entries';
    const res = await apiFetch(url);
    if (!res.ok) return;
    const entries = await res.json();
    const tbody = document.getElementById('admin-entries-body');
    if (entries.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; color:#7a726d;">Записей не найдено</td></tr>`;
        return;
    }
    tbody.innerHTML = entries.map(e => `
        <tr>
            <td>#${e.id}</td>
            <td>${e.entry_date}</td>
            <td>${e.entry_time.slice(0, 5)}</td>
            <td>${e.name_user} ${e.surname_user}</td>
            <td>${e.name_procedures}</td>
            <td>${e.price} ₽</td>
            <td><button class="btn btn-danger" onclick="adminDeleteEntry(${e.id})">Удалить</button></td>
        </tr>
    `).join('');
}

async function adminDeleteEntry(id) {
    const res = await apiFetch(`/delete_entries/${id}`, { method: 'DELETE' });
    if (res.ok) {
        showToast(`Запись #${id} удалена`);
        loadAdminEntries(document.getElementById('admin-date-filter').value);
    } else {
        showToast('Ошибка при удалении', 'error');
    }
}

document.getElementById('admin-date-filter').addEventListener('change', (e) => {
    loadAdminEntries(e.target.value);
});

document.getElementById('admin-reset-date').addEventListener('click', () => {
    document.getElementById('admin-date-filter').value = '';
    loadAdminEntries();
});

// Старт приложения
initApp();