// static/magazin/js/cart.js

class CartManager {
    constructor() {
        this.CART_STORAGE_KEY = 'shopping_cart';
        this.initializeCart();
        this.setupEventListeners();
    }

    initializeCart() {
        if (!localStorage.getItem(this.CART_STORAGE_KEY)) {
            localStorage.setItem(this.CART_STORAGE_KEY, JSON.stringify([]));
        }
        this.updateCartDisplay();
        this.updateCartBadge();
    }

    setupEventListeners() {
        window.addEventListener('storage', () => {
            this.updateCartDisplay();
            this.updateCartBadge();
        });
    }

    async addToCart(productId, productType) {
        try {
            const quantityInput = document.getElementById(`quantity-${productId}`);
            const quantity = parseInt(quantityInput?.value || 1);
            
            const response = await fetch('/magazin/cart/add/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify({
                    product_id: productId,
                    product_type: productType,
                    quantity: quantity
                })
            });

            const data = await response.json();
            if (data.success) {
                const cart = this.getCart();
                const existingItem = cart.find(item => 
                    item.id === productId && item.type === productType
                );

                const newItem = {
                    id: productId,
                    type: productType,
                    name: data.product_name,
                    price: data.product_price,
                    quantity: quantity,
                    max_stock: data.stock_count
                };

                if (existingItem) {
                    existingItem.quantity += quantity;
                    if (existingItem.quantity > existingItem.max_stock) {
                        existingItem.quantity = existingItem.max_stock;
                    }
                } else {
                    cart.push(newItem);
                }

                this.saveCart(cart);
                this.showNotification('Produsul a fost adăugat în coș');
            } else {
                this.showNotification(data.message || 'Eroare la adăugarea în coș', 'danger');
            }
        } catch (error) {
            console.error('Error:', error);
            this.showNotification('Eroare la adăugarea în coș', 'danger');
        }
    }

    getCart() {
        return JSON.parse(localStorage.getItem(this.CART_STORAGE_KEY) || '[]');
    }

    saveCart(cart) {
        localStorage.setItem(this.CART_STORAGE_KEY, JSON.stringify(cart));
        this.updateCartDisplay();
        this.updateCartBadge();
    }

    updateQuantity(productId, productType, newQuantity) {
        const cart = this.getCart();
        const item = cart.find(item => 
            item.id === productId && item.type === productType
        );

        if (item) {
            newQuantity = Math.max(1, Math.min(newQuantity, item.max_stock));
            item.quantity = newQuantity;
            this.saveCart(cart);
        }
    }

    removeItem(productId, productType) {
        let cart = this.getCart();
        cart = cart.filter(item => !(item.id === productId && item.type === productType));
        this.saveCart(cart);
        this.showNotification('Produs eliminat din coș');
    }

    updateCartDisplay() {
        const cart = this.getCart();
        const cartItemsDiv = document.getElementById('cart-items');
        const totalItemsSpan = document.getElementById('total-items');
        const totalPriceSpan = document.getElementById('total-price');

        if (!cartItemsDiv) return; // Ne aflăm pe altă pagină

        cartItemsDiv.innerHTML = '';
        let totalItems = 0;
        let totalPrice = 0;

        cart.forEach(item => {
            totalItems += item.quantity;
            totalPrice += item.price * item.quantity;

            const itemDiv = document.createElement('div');
            itemDiv.className = 'col-md-4 mb-4';
            itemDiv.innerHTML = `
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">${item.name}</h5>
                        <p class="card-text">
                            Preț: ${item.price} RON<br>
                            Cantitate: 
                            <div class="input-group input-group-sm" style="max-width: 150px;">
                                <button class="btn btn-outline-secondary" type="button" 
                                        onclick="cartManager.updateQuantity('${item.id}', '${item.type}', ${item.quantity - 1})">-</button>
                                <input type="number" class="form-control text-center" 
                                       value="${item.quantity}" min="1" max="${item.max_stock}"
                                       onchange="cartManager.updateQuantity('${item.id}', '${item.type}', this.value)">
                                <button class="btn btn-outline-secondary" type="button"
                                        onclick="cartManager.updateQuantity('${item.id}', '${item.type}', ${item.quantity + 1})">+</button>
                            </div>
                        </p>
                        <button class="btn btn-danger" 
                                onclick="cartManager.removeItem('${item.id}', '${item.type}')">
                            Șterge
                        </button>
                    </div>
                </div>
            `;
            cartItemsDiv.appendChild(itemDiv);
        });

        if (totalItemsSpan) totalItemsSpan.textContent = totalItems;
        if (totalPriceSpan) totalPriceSpan.textContent = `${totalPrice.toFixed(2)} RON`;
    }

    updateCartBadge() {
        const badge = document.querySelector('#cart-icon .badge');
        if (badge) {
            const cart = this.getCart();
            const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);
            badge.textContent = totalItems;
        }
    }

    sortByName() {
        const cart = this.getCart();
        cart.sort((a, b) => a.name.localeCompare(b.name));
        this.saveCart(cart);
    }

    sortByPrice() {
        const cart = this.getCart();
        cart.sort((a, b) => a.price - b.price);
        this.saveCart(cart);
    }

    getCsrfToken() {
        const name = 'csrftoken';
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    showNotification(message, type = 'success') {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 1050;';
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        document.body.appendChild(alertDiv);
        setTimeout(() => alertDiv.remove(), 3000);
    }
}

// Inițializare
const cartManager = new CartManager();