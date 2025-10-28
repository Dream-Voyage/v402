/**
 * V402 Web Component for Payment Processing
 * A custom web component that can be used in any web application
 */

class V402PaymentButton extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    
    // Component state
    this.state = {
      product: null,
      userAddress: '',
      amount: '',
      hasAccess: false,
      isProcessing: false,
      isLoading: true,
      error: null,
      paymentStatus: null
    };
    
    // Services
    this.v402Provider = null;
    this.paymentService = null;
    this.accessService = null;
    
    // Bind methods
    this.handleInputChange = this.handleInputChange.bind(this);
    this.handlePayment = this.handlePayment.bind(this);
    this.handleRetry = this.handleRetry.bind(this);
  }
  
  static get observedAttributes() {
    return ['product-id', 'api-url', 'public-key', 'private-key'];
  }
  
  get productId() {
    return this.getAttribute('product-id');
  }
  
  get apiUrl() {
    return this.getAttribute('api-url') || 'https://api.v402.network';
  }
  
  get publicKey() {
    return this.getAttribute('public-key');
  }
  
  get privateKey() {
    return this.getAttribute('private-key');
  }
  
  connectedCallback() {
    this.render();
    this.initializeServices();
    this.loadProduct();
  }
  
  disconnectedCallback() {
    // Cleanup event listeners
    const shadowRoot = this.shadowRoot;
    if (shadowRoot) {
      const inputs = shadowRoot.querySelectorAll('input');
      inputs.forEach(input => {
        input.removeEventListener('input', this.handleInputChange);
      });
      
      const buttons = shadowRoot.querySelectorAll('button');
      buttons.forEach(button => {
        button.removeEventListener('click', this.handlePayment);
        button.removeEventListener('click', this.handleRetry);
      });
    }
  }
  
  async initializeServices() {
    try {
      // Import services dynamically
      const { V402Provider } = await import('../services/V402Provider.js');
      const { PaymentService } = await import('../services/PaymentService.js');
      const { AccessService } = await import('../services/AccessService.js');
      
      this.v402Provider = new V402Provider({
        baseUrl: this.apiUrl,
        publicKey: this.publicKey,
        privateKey: this.privateKey
      });
      
      this.paymentService = new PaymentService(this.v402Provider);
      this.accessService = new AccessService(this.v402Provider);
      
    } catch (error) {
      this.setState({ error: `Failed to initialize services: ${error.message}` });
    }
  }
  
  async loadProduct() {
    if (!this.v402Provider || !this.productId) return;
    
    try {
      this.setState({ isLoading: true, error: null });
      
      const product = await this.v402Provider.getProduct(this.productId);
      this.setState({ 
        product, 
        amount: product.price,
        isLoading: false 
      });
      
      // Check access if user address is provided
      if (this.state.userAddress) {
        await this.checkAccess();
      }
      
    } catch (error) {
      this.setState({ 
        error: `Failed to load product: ${error.message}`,
        isLoading: false 
      });
    }
  }
  
  async checkAccess() {
    if (!this.state.userAddress || !this.accessService) return;
    
    try {
      const accessResponse = await this.accessService.checkAccess({
        productId: this.productId,
        userAddress: this.state.userAddress,
        timestamp: Date.now(),
        signature: 'mock-signature' // In real implementation, this would be generated
      });
      
      this.setState({ hasAccess: accessResponse.hasAccess });
      
      if (accessResponse.hasAccess) {
        this.setState({
          paymentStatus: {
            status: 'success',
            message: 'Access granted! You can now view the content.'
          }
        });
      }
    } catch (error) {
      console.warn('Failed to check access:', error.message);
    }
  }
  
  async handlePayment() {
    if (!this.state.userAddress || !this.state.amount) {
      this.setState({ error: 'Please provide your Ethereum address and amount' });
      return;
    }
    
    try {
      this.setState({ isProcessing: true, error: null, paymentStatus: null });
      
      const paymentRequest = {
        productId: this.productId,
        amount: this.state.amount,
        currency: this.state.product.currency,
        userAddress: this.state.userAddress,
        nonce: `nonce-${Date.now()}`,
        signature: 'mock-signature' // In real implementation, this would be generated
      };
      
      const paymentResponse = await this.paymentService.processPayment(paymentRequest);
      
      if (paymentResponse.status === 'completed') {
        this.setState({
          paymentStatus: {
            status: 'success',
            message: `Payment successful! Transaction: ${paymentResponse.transaction_hash}`
          },
          hasAccess: true
        });
        
        // Update product purchase count
        const updatedProduct = { ...this.state.product };
        updatedProduct.purchase_count += 1;
        this.setState({ product: updatedProduct });
        
        // Dispatch success event
        this.dispatchEvent(new CustomEvent('payment-success', {
          detail: {
            product: this.state.product,
            payment: paymentResponse
          }
        }));
        
      } else {
        this.setState({
          paymentStatus: {
            status: 'error',
            message: `Payment failed: ${paymentResponse.error || 'Unknown error'}`
          }
        });
      }
      
    } catch (error) {
      this.setState({ 
        error: `Payment failed: ${error.message}`,
        paymentStatus: {
          status: 'error',
          message: error.message
        }
      });
    } finally {
      this.setState({ isProcessing: false });
    }
  }
  
  handleInputChange(event) {
    const { name, value } = event.target;
    this.setState({ [name]: value });
    
    // Check access when user address changes
    if (name === 'userAddress' && value) {
      this.checkAccess();
    }
  }
  
  handleRetry() {
    this.setState({ error: null });
    this.loadProduct();
  }
  
  setState(newState) {
    this.state = { ...this.state, ...newState };
    this.render();
  }
  
  render() {
    const { product, userAddress, amount, hasAccess, isProcessing, isLoading, error, paymentStatus } = this.state;
    
    this.shadowRoot.innerHTML = `
      <style>
        :host {
          display: block;
          max-width: 600px;
          margin: 0 auto;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }
        
        .container {
          background: #fff;
          border-radius: 12px;
          box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
          overflow: hidden;
        }
        
        .product-header {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
          padding: 24px;
          display: flex;
          justify-content: space-between;
          align-items: center;
        }
        
        .product-title {
          margin: 0;
          font-size: 24px;
          font-weight: 600;
        }
        
        .product-price {
          font-size: 20px;
          font-weight: 700;
          background: rgba(255, 255, 255, 0.2);
          padding: 8px 16px;
          border-radius: 20px;
        }
        
        .product-content {
          padding: 24px;
        }
        
        .product-description {
          color: #666;
          line-height: 1.6;
          margin-bottom: 20px;
        }
        
        .product-stats {
          display: flex;
          gap: 20px;
          margin-bottom: 24px;
        }
        
        .stat {
          text-align: center;
        }
        
        .stat-label {
          display: block;
          font-size: 12px;
          color: #666;
          margin-bottom: 4px;
        }
        
        .stat-value {
          display: block;
          font-size: 18px;
          font-weight: 600;
          color: #333;
        }
        
        .payment-section {
          border-top: 1px solid #eee;
          padding: 24px;
        }
        
        .payment-status {
          margin-bottom: 20px;
        }
        
        .status-message {
          padding: 12px;
          border-radius: 8px;
          font-weight: 500;
        }
        
        .status-message.success {
          background: #d4edda;
          color: #155724;
          border: 1px solid #c3e6cb;
        }
        
        .status-message.error {
          background: #f8d7da;
          color: #721c24;
          border: 1px solid #f5c6cb;
        }
        
        .form-group {
          margin-bottom: 16px;
        }
        
        .form-group label {
          display: block;
          margin-bottom: 8px;
          font-weight: 500;
          color: #333;
        }
        
        .form-input {
          width: 100%;
          padding: 12px;
          border: 1px solid #ddd;
          border-radius: 8px;
          font-size: 14px;
          transition: border-color 0.2s;
          box-sizing: border-box;
        }
        
        .form-input:focus {
          outline: none;
          border-color: #667eea;
        }
        
        .form-input:disabled {
          background: #f5f5f5;
          cursor: not-allowed;
        }
        
        .payment-button {
          width: 100%;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
          border: none;
          padding: 16px;
          border-radius: 8px;
          font-size: 16px;
          font-weight: 600;
          cursor: pointer;
          transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .payment-button:hover:not(:disabled) {
          transform: translateY(-2px);
          box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }
        
        .payment-button:disabled {
          opacity: 0.6;
          cursor: not-allowed;
          transform: none;
        }
        
        .access-section {
          text-align: center;
        }
        
        .access-granted {
          background: #d4edda;
          color: #155724;
          padding: 24px;
          border-radius: 8px;
          border: 1px solid #c3e6cb;
        }
        
        .access-granted h3 {
          margin: 0 0 12px 0;
          color: #155724;
        }
        
        .content-link {
          display: inline-block;
          background: #28a745;
          color: white;
          padding: 12px 24px;
          text-decoration: none;
          border-radius: 6px;
          font-weight: 500;
          margin-top: 16px;
          transition: background-color 0.2s;
        }
        
        .content-link:hover {
          background: #218838;
        }
        
        .loading {
          text-align: center;
          padding: 40px;
        }
        
        .spinner {
          width: 40px;
          height: 40px;
          border: 4px solid #f3f3f3;
          border-top: 4px solid #667eea;
          border-radius: 50%;
          animation: spin 1s linear infinite;
          margin: 0 auto 16px;
        }
        
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
        
        .error {
          background: #f8d7da;
          color: #721c24;
          padding: 24px;
          border-radius: 8px;
          border: 1px solid #f5c6cb;
          text-align: center;
        }
        
        .error h3 {
          margin: 0 0 12px 0;
          color: #721c24;
        }
        
        .retry-button {
          background: #dc3545;
          color: white;
          border: none;
          padding: 8px 16px;
          border-radius: 4px;
          cursor: pointer;
          margin-top: 12px;
        }
        
        .retry-button:hover {
          background: #c82333;
        }
      </style>
      
      <div class="container">
        ${isLoading ? this.renderLoading() : ''}
        ${error ? this.renderError(error) : ''}
        ${product ? this.renderProduct(product, userAddress, amount, hasAccess, isProcessing, paymentStatus) : ''}
      </div>
    `;
    
    // Add event listeners
    this.addEventListeners();
  }
  
  renderLoading() {
    return `
      <div class="loading">
        <div class="spinner"></div>
        <p>Loading...</p>
      </div>
    `;
  }
  
  renderError(error) {
    return `
      <div class="error">
        <h3>Error</h3>
        <p>${error}</p>
        <button class="retry-button" data-action="retry">Retry</button>
      </div>
    `;
  }
  
  renderProduct(product, userAddress, amount, hasAccess, isProcessing, paymentStatus) {
    const conversionRate = product.view_count > 0 
      ? ((product.purchase_count / product.view_count) * 100).toFixed(2) 
      : 0;
    
    return `
      <div class="product-header">
        <h2 class="product-title">${product.title}</h2>
        <div class="product-price">${product.price} ${product.currency}</div>
      </div>
      
      <div class="product-content">
        <p class="product-description">${product.description}</p>
        
        <div class="product-stats">
          <div class="stat">
            <span class="stat-label">Views:</span>
            <span class="stat-value">${product.view_count}</span>
          </div>
          <div class="stat">
            <span class="stat-label">Purchases:</span>
            <span class="stat-value">${product.purchase_count}</span>
          </div>
          ${product.purchase_count > 0 ? `
            <div class="stat">
              <span class="stat-label">Conversion Rate:</span>
              <span class="stat-value">${conversionRate}%</span>
            </div>
          ` : ''}
        </div>
      </div>
      
      <div class="payment-section">
        ${paymentStatus ? this.renderPaymentStatus(paymentStatus) : ''}
        
        ${!hasAccess && !isProcessing ? this.renderPaymentForm(userAddress, amount) : ''}
        
        ${hasAccess ? this.renderAccessGranted(product) : ''}
      </div>
    `;
  }
  
  renderPaymentStatus(paymentStatus) {
    return `
      <div class="payment-status">
        <div class="status-message ${paymentStatus.status}">
          ${paymentStatus.message}
        </div>
      </div>
    `;
  }
  
  renderPaymentForm(userAddress, amount) {
    return `
      <div class="payment-form">
        <div class="form-group">
          <label for="userAddress">Your Ethereum Address:</label>
          <input
            id="userAddress"
            name="userAddress"
            type="text"
            placeholder="0x..."
            class="form-input"
            value="${userAddress}"
            ${isProcessing ? 'disabled' : ''}
          />
        </div>
        
        <div class="form-group">
          <label for="amount">Amount:</label>
          <input
            id="amount"
            name="amount"
            type="text"
            placeholder="${this.state.product?.price || ''}"
            class="form-input"
            value="${amount}"
            ${isProcessing ? 'disabled' : ''}
          />
        </div>
        
        <button
          class="payment-button"
          data-action="payment"
          ${isProcessing || !userAddress ? 'disabled' : ''}
        >
          ${isProcessing ? 'Processing...' : `Pay ${amount || this.state.product?.price || ''} ${this.state.product?.currency || ''}`}
        </button>
      </div>
    `;
  }
  
  renderAccessGranted(product) {
    return `
      <div class="access-section">
        <div class="access-granted">
          <h3>Access Granted!</h3>
          <p>You now have access to this content.</p>
          <a href="${product.content_url}" target="_blank" class="content-link">
            Access Content
          </a>
        </div>
      </div>
    `;
  }
  
  addEventListeners() {
    const shadowRoot = this.shadowRoot;
    if (!shadowRoot) return;
    
    // Input change listeners
    const inputs = shadowRoot.querySelectorAll('input');
    inputs.forEach(input => {
      input.addEventListener('input', this.handleInputChange);
    });
    
    // Button click listeners
    const buttons = shadowRoot.querySelectorAll('button');
    buttons.forEach(button => {
      const action = button.dataset.action;
      if (action === 'payment') {
        button.addEventListener('click', this.handlePayment);
      } else if (action === 'retry') {
        button.addEventListener('click', this.handleRetry);
      }
    });
  }
}

// Register the custom element
customElements.define('v402-payment-button', V402PaymentButton);

// Export for module usage
export { V402PaymentButton };
