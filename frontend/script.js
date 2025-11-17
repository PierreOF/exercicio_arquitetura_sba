// Configuração da API
const API_URL = 'http://localhost:8000';

// Estado da aplicação
let currentUser = null;

// Elementos DOM
const authSection = document.getElementById('auth-section');
const userSection = document.getElementById('user-section');
const registerForm = document.getElementById('register-form');
const loginForm = document.getElementById('login-form');
const purchaseForm = document.getElementById('purchase-form');
const logoutBtn = document.getElementById('logout-btn');
const refreshOrdersBtn = document.getElementById('refresh-orders-btn');
const notification = document.getElementById('notification');

// Inicialização
document.addEventListener('DOMContentLoaded', () => {
    // Verificar se há usuário logado no localStorage
    const savedUser = localStorage.getItem('currentUser');
    if (savedUser) {
        currentUser = JSON.parse(savedUser);
        showUserSection();
        loadUserOrders();
    }

    // Verificar saúde dos serviços
    checkHealth();
    setInterval(checkHealth, 30000); // Atualizar a cada 30 segundos

    // Event Listeners
    registerForm.addEventListener('submit', handleRegister);
    loginForm.addEventListener('submit', handleLogin);
    purchaseForm.addEventListener('submit', handlePurchase);
    logoutBtn.addEventListener('click', handleLogout);
    refreshOrdersBtn.addEventListener('click', loadUserOrders);
});

// Funções de Notificação
function showNotification(message, type = 'info') {
    notification.textContent = message;
    notification.className = `notification ${type}`;
    notification.classList.remove('hidden');

    setTimeout(() => {
        notification.classList.add('hidden');
    }, 4000);
}

// Verificar Saúde dos Serviços
async function checkHealth() {
    try {
        const response = await fetch(`${API_URL}/health`);
        const data = await response.json();

        const healthStatus = document.getElementById('health-status');
        healthStatus.innerHTML = '';

        // Status geral
        const overallBadge = document.createElement('div');
        overallBadge.className = `health-badge ${data.status === 'healthy' ? 'healthy' : 'unhealthy'}`;
        overallBadge.innerHTML = `<strong>Sistema:</strong> ${data.status === 'healthy' ? '✓ Operacional' : '⚠ Degradado'}`;
        healthStatus.appendChild(overallBadge);

        // Status de cada serviço
        Object.entries(data.services).forEach(([service, status]) => {
            const badge = document.createElement('div');
            badge.className = `health-badge ${status === 'healthy' ? 'healthy' : 'unhealthy'}`;
            badge.innerHTML = `<strong>${service}:</strong> ${status === 'healthy' ? '✓' : '✗'}`;
            healthStatus.appendChild(badge);

            // Atualizar indicador no diagrama
            const indicator = document.getElementById(`status-${service}`);
            if (indicator) {
                indicator.className = `status-indicator ${status === 'healthy' ? 'healthy' : 'unhealthy'}`;
            }
        });

        // Atualizar indicador do gateway
        const gatewayIndicator = document.getElementById('status-gateway');
        if (gatewayIndicator) {
            gatewayIndicator.className = `status-indicator ${data.status === 'healthy' ? 'healthy' : 'unhealthy'}`;
        }

    } catch (error) {
        console.error('Erro ao verificar saúde:', error);
        const healthStatus = document.getElementById('health-status');
        healthStatus.innerHTML = '<div class="health-badge unhealthy"><strong>Erro ao conectar aos serviços</strong></div>';
    }
}

// Registro de Usuário
async function handleRegister(e) {
    e.preventDefault();

    const name = document.getElementById('reg-name').value;
    const email = document.getElementById('reg-email').value;

    const submitBtn = registerForm.querySelector('button[type="submit"]');
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="loading"></span> Registrando...';

    try {
        const response = await fetch(`${API_URL}/gateway/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, email })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Erro ao registrar usuário');
        }

        showNotification(`Usuário ${name} registrado com sucesso!`, 'success');
        registerForm.reset();

        // Auto-login após registro
        currentUser = data.user;
        localStorage.setItem('currentUser', JSON.stringify(currentUser));
        showUserSection();
        loadUserOrders();

    } catch (error) {
        showNotification(error.message, 'error');
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Registrar';
    }
}

// Login de Usuário
async function handleLogin(e) {
    e.preventDefault();

    const email = document.getElementById('login-email').value;

    const submitBtn = loginForm.querySelector('button[type="submit"]');
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="loading"></span> Entrando...';

    try {
        const response = await fetch(`${API_URL}/gateway/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Erro ao fazer login');
        }

        currentUser = data.user;
        localStorage.setItem('currentUser', JSON.stringify(currentUser));
        showNotification(`Bem-vindo de volta, ${currentUser.name}!`, 'success');
        loginForm.reset();
        showUserSection();
        loadUserOrders();

    } catch (error) {
        showNotification(error.message, 'error');
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Entrar';
    }
}

// Realizar Compra
async function handlePurchase(e) {
    e.preventDefault();

    if (!currentUser) {
        showNotification('Você precisa estar logado para comprar', 'error');
        return;
    }

    const productName = document.getElementById('product-name').value;
    const amount = parseFloat(document.getElementById('product-amount').value);
    const paymentMethod = document.getElementById('payment-method').value;

    const submitBtn = purchaseForm.querySelector('button[type="submit"]');
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="loading"></span> Processando...';

    try {
        const response = await fetch(`${API_URL}/gateway/purchase`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: currentUser.user_id,
                amount,
                product_name: productName,
                payment_method: paymentMethod
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Erro ao processar compra');
        }

        if (data.purchase_status === 'paid') {
            showNotification(
                `Compra de ${productName} (R$ ${amount.toFixed(2)}) realizada com sucesso!`,
                'success'
            );
            purchaseForm.reset();
            loadUserOrders(); // Atualizar lista de pedidos
        } else {
            showNotification(
                `Falha no pagamento: ${data.transaction.message}`,
                'error'
            );
        }

    } catch (error) {
        showNotification(error.message, 'error');
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Comprar';
    }
}

// Carregar Pedidos do Usuário
async function loadUserOrders() {
    if (!currentUser) return;

    const ordersList = document.getElementById('orders-list');
    ordersList.innerHTML = '<p class="empty-state">Carregando pedidos...</p>';

    refreshOrdersBtn.disabled = true;
    refreshOrdersBtn.innerHTML = '<span class="loading"></span> Atualizando...';

    try {
        const response = await fetch(`${API_URL}/gateway/user/${currentUser.user_id}/orders`);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Erro ao carregar pedidos');
        }

        if (data.total_orders === 0) {
            ordersList.innerHTML = '<p class="empty-state">Você ainda não tem pedidos</p>';
        } else {
            ordersList.innerHTML = '';
            // Ordenar pedidos do mais recente para o mais antigo
            const sortedOrders = data.orders.sort((a, b) =>
                new Date(b.created_at) - new Date(a.created_at)
            );

            sortedOrders.forEach(order => {
                const orderItem = createOrderElement(order);
                ordersList.appendChild(orderItem);
            });
        }

    } catch (error) {
        ordersList.innerHTML = `<p class="empty-state">Erro ao carregar pedidos: ${error.message}</p>`;
    } finally {
        refreshOrdersBtn.disabled = false;
        refreshOrdersBtn.textContent = 'Atualizar Pedidos';
    }
}

// Criar Elemento de Pedido
function createOrderElement(order) {
    const orderItem = document.createElement('div');
    orderItem.className = `order-item ${order.status}`;

    const statusText = {
        'completed': 'Concluído',
        'payment_failed': 'Pagamento Falhou',
        'pending': 'Pendente'
    }[order.status] || order.status;

    const date = new Date(order.created_at);
    const formattedDate = date.toLocaleDateString('pt-BR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });

    orderItem.innerHTML = `
        <div class="order-header">
            <span class="order-product">${order.product_name}</span>
            <span class="order-amount">R$ ${order.amount.toFixed(2)}</span>
        </div>
        <div class="order-details">
            <div>Pedido #${order.order_id}</div>
            <div>${formattedDate}</div>
        </div>
        <span class="order-status ${order.status}">${statusText}</span>
    `;

    return orderItem;
}

// Logout
function handleLogout() {
    currentUser = null;
    localStorage.removeItem('currentUser');
    showAuthSection();
    showNotification('Logout realizado com sucesso', 'info');
}

// Mostrar Seção de Autenticação
function showAuthSection() {
    authSection.classList.remove('hidden');
    userSection.classList.add('hidden');
}

// Mostrar Seção de Usuário
function showUserSection() {
    authSection.classList.add('hidden');
    userSection.classList.remove('hidden');

    // Preencher informações do usuário
    document.getElementById('user-name').textContent = currentUser.name;
    document.getElementById('user-email').textContent = currentUser.email;
    document.getElementById('user-id').textContent = currentUser.user_id;
}

// Utilitários
function formatCurrency(value) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(value);
}
