<template>
  <div class="v402-payment-container">
    <div class="product-card" v-if="product">
      <div class="product-header">
        <h2 class="product-title">{{ product.title }}</h2>
        <div class="product-price">
          {{ product.price }} {{ product.currency }}
        </div>
      </div>

      <div class="product-content">
        <p class="product-description">{{ product.description }}</p>

        <div class="product-meta" v-if="product.category || product.tags.length">
          <div class="product-category" v-if="product.category">
            <span class="label">Category:</span>
            <span class="value">{{ product.category }}</span>
          </div>

          <div class="product-tags" v-if="product.tags.length">
            <span class="label">Tags:</span>
            <span class="tag" v-for="tag in product.tags" :key="tag">
              {{ tag }}
            </span>
          </div>
        </div>

        <div class="product-stats">
          <div class="stat">
            <span class="stat-label">Views:</span>
            <span class="stat-value">{{ product.view_count }}</span>
          </div>
          <div class="stat">
            <span class="stat-label">Purchases:</span>
            <span class="stat-value">{{ product.purchase_count }}</span>
          </div>
          <div class="stat" v-if="product.purchase_count > 0">
            <span class="stat-label">Conversion Rate:</span>
            <span class="stat-value">{{ conversionRate }}%</span>
          </div>
        </div>
      </div>

      <div class="payment-section">
        <div class="payment-status" v-if="paymentStatus">
          <div class="status-message" :class="paymentStatus.status">
            {{ paymentStatus.message }}
          </div>
        </div>

        <div class="payment-form" v-if="!hasAccess && !isProcessing">
          <div class="form-group">
            <label for="userAddress">Your Ethereum Address:</label>
            <input
              id="userAddress"
              v-model="userAddress"
              type="text"
              placeholder="0x..."
              class="form-input"
              :disabled="isProcessing"
            />
          </div>

          <div class="form-group">
            <label for="amount">Amount:</label>
            <input
              id="amount"
              v-model="amount"
              type="text"
              :placeholder="product.price"
              class="form-input"
              :disabled="isProcessing"
            />
          </div>

          <button
            @click="processPayment"
            :disabled="isProcessing || !userAddress"
            class="payment-button"
          >
            <span v-if="isProcessing">Processing...</span>
            <span v-else>Pay {{ amount || product.price }} {{ product.currency }}</span>
          </button>
        </div>

        <div class="access-section" v-if="hasAccess">
          <div class="access-granted">
            <h3>Access Granted!</h3>
            <p>You now have access to this content.</p>
            <a :href="product.content_url" target="_blank" class="content-link">
              Access Content
            </a>
          </div>
        </div>
      </div>
    </div>

    <div class="loading" v-if="isLoading">
      <div class="spinner"></div>
      <p>Loading...</p>
    </div>

    <div class="error" v-if="error">
      <h3>Error</h3>
      <p>{{ error }}</p>
      <button @click="clearError" class="retry-button">Retry</button>
    </div>
  </div>
</template>

<script>
import {computed, onMounted, ref, watch} from 'vue'
import {V402Provider} from '../services/V402Provider'
import {PaymentService} from '../services/PaymentService'
import {AccessService} from '../services/AccessService'

export default {
  name: 'V402PaymentButton',
  props: {
    productId: {
      type: String,
      required: true
    },
    apiUrl: {
      type: String,
      default: 'https://api.v402.network'
    },
    publicKey: {
      type: String,
      required: true
    },
    privateKey: {
      type: String,
      required: true
    }
  },
  setup(props) {
    // Reactive data
    const product = ref(null)
    const userAddress = ref('')
    const amount = ref('')
    const hasAccess = ref(false)
    const isProcessing = ref(false)
    const isLoading = ref(true)
    const error = ref(null)
    const paymentStatus = ref(null)

    // Services
    const v402Provider = ref(null)
    const paymentService = ref(null)
    const accessService = ref(null)

    // Computed properties
    const conversionRate = computed(() => {
      if (!product.value || product.value.view_count === 0) return 0
      return ((product.value.purchase_count / product.value.view_count) * 100).toFixed(2)
    })

    // Methods
    const initializeServices = () => {
      try {
        v402Provider.value = new V402Provider({
          baseUrl: props.apiUrl,
          publicKey: props.publicKey,
          privateKey: props.privateKey
        })

        paymentService.value = new PaymentService(v402Provider.value)
        accessService.value = new AccessService(v402Provider.value)
      } catch (err) {
        error.value = `Failed to initialize services: ${err.message}`
        isLoading.value = false
      }
    }

    const loadProduct = async () => {
      try {
        isLoading.value = true
        error.value = null

        const productData = await v402Provider.value.getProduct(props.productId)
        product.value = productData

        // Set default amount
        amount.value = productData.price

        // Check if user already has access
        await checkAccess()

      } catch (err) {
        error.value = `Failed to load product: ${err.message}`
      } finally {
        isLoading.value = false
      }
    }

    const checkAccess = async () => {
      if (!userAddress.value) return

      try {
        const accessResponse = await accessService.value.checkAccess({
          productId: props.productId,
          userAddress: userAddress.value,
          timestamp: Date.now(),
          signature: 'mock-signature' // In real implementation, this would be generated
        })

        hasAccess.value = accessResponse.hasAccess

        if (accessResponse.hasAccess) {
          paymentStatus.value = {
            status: 'success',
            message: 'Access granted! You can now view the content.'
          }
        }
      } catch (err) {
        console.warn('Failed to check access:', err.message)
      }
    }

    const processPayment = async () => {
      if (!userAddress.value || !amount.value) {
        error.value = 'Please provide your Ethereum address and amount'
        return
      }

      try {
        isProcessing.value = true
        error.value = null
        paymentStatus.value = null

        const paymentRequest = {
          productId: props.productId,
          amount: amount.value,
          currency: product.value.currency,
          userAddress: userAddress.value,
          nonce: `nonce-${Date.now()}`,
          signature: 'mock-signature' // In real implementation, this would be generated
        }

        const paymentResponse = await paymentService.value.processPayment(paymentRequest)

        if (paymentResponse.status === 'completed') {
          paymentStatus.value = {
            status: 'success',
            message: `Payment successful! Transaction: ${paymentResponse.transaction_hash}`
          }

          // Update product purchase count
          product.value.purchase_count += 1

          // Grant access
          hasAccess.value = true

          // Emit success event
          emit('payment-success', {
            product: product.value,
            payment: paymentResponse
          })
        } else {
          paymentStatus.value = {
            status: 'error',
            message: `Payment failed: ${paymentResponse.error || 'Unknown error'}`
          }
        }

      } catch (err) {
        error.value = `Payment failed: ${err.message}`
        paymentStatus.value = {
          status: 'error',
          message: err.message
        }
      } finally {
        isProcessing.value = false
      }
    }

    const clearError = () => {
      error.value = null
    }

    // Watchers
    watch(userAddress, () => {
      if (userAddress.value) {
        checkAccess()
      }
    })

    // Lifecycle
    onMounted(async () => {
      initializeServices()
      if (v402Provider.value) {
        await loadProduct()
      }
    })

    return {
      product,
      userAddress,
      amount,
      hasAccess,
      isProcessing,
      isLoading,
      error,
      paymentStatus,
      conversionRate,
      processPayment,
      clearError
    }
  }
}
</script>

<style scoped>
.v402-payment-container {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.product-card {
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

.product-meta {
  margin-bottom: 20px;
}

.product-category,
.product-tags {
  margin-bottom: 8px;
}

.label {
  font-weight: 600;
  color: #333;
  margin-right: 8px;
}

.value {
  color: #666;
}

.tag {
  display: inline-block;
  background: #f0f0f0;
  color: #666;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  margin-right: 4px;
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
