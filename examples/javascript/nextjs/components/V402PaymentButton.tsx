import React, {useCallback, useEffect, useState} from 'react';
import {V402Provider} from '../services/V402Provider';
import {PaymentService} from '../services/PaymentService';
import {AccessService} from '../services/AccessService';
import styles from './V402PaymentButton.module.css';

interface Product {
  id: string;
  title: string;
  description: string;
  price: string;
  currency: string;
  content_url: string;
  category?: string;
  tags: string[];
  author?: string;
  status: string;
  view_count: number;
  purchase_count: number;
  created_at: string;
  updated_at: string;
}

interface PaymentRequest {
  productId: string;
  amount: string;
  currency: string;
  userAddress: string;
  nonce: string;
  signature: string;
}

interface PaymentResponse {
  transaction_hash: string;
  status: string;
  amount: string;
  currency: string;
  timestamp: string;
  block_number?: number;
  gas_used?: number;
  error?: string;
}

interface AccessRequest {
  productId: string;
  userAddress: string;
  timestamp: number;
  signature: string;
}

interface AccessResponse {
  has_access: boolean;
  reason?: string;
  expires_at?: number;
}

interface V402PaymentButtonProps {
  productId: string;
  apiUrl?: string;
  publicKey: string;
  privateKey: string;
  onPaymentSuccess?: (data: { product: Product; payment: PaymentResponse }) => void;
  onPaymentError?: (error: string) => void;
  className?: string;
}

interface PaymentStatus {
  status: 'success' | 'error';
  message: string;
}

export const V402PaymentButton: React.FC<V402PaymentButtonProps> = ({
  productId,
  apiUrl = 'https://api.v402.network',
  publicKey,
  privateKey,
  onPaymentSuccess,
  onPaymentError,
  className
}) => {
  // State
  const [product, setProduct] = useState<Product | null>(null);
  const [userAddress, setUserAddress] = useState('');
  const [amount, setAmount] = useState('');
  const [hasAccess, setHasAccess] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [paymentStatus, setPaymentStatus] = useState<PaymentStatus | null>(null);

  // Services
  const [v402Provider, setV402Provider] = useState<V402Provider | null>(null);
  const [paymentService, setPaymentService] = useState<PaymentService | null>(null);
  const [accessService, setAccessService] = useState<AccessService | null>(null);

  // Initialize services
  useEffect(() => {
    try {
      const provider = new V402Provider({
        baseUrl: apiUrl,
        publicKey,
        privateKey
      });

      const paymentSvc = new PaymentService(provider);
      const accessSvc = new AccessService(provider);

      setV402Provider(provider);
      setPaymentService(paymentSvc);
      setAccessService(accessSvc);
    } catch (err) {
      setError(`Failed to initialize services: ${err instanceof Error ? err.message : 'Unknown error'}`);
      setIsLoading(false);
    }
  }, [apiUrl, publicKey, privateKey]);

  // Load product
  const loadProduct = useCallback(async () => {
    if (!v402Provider || !productId) return;

    try {
      setIsLoading(true);
      setError(null);

      const productData = await v402Provider.getProduct(productId);
      setProduct(productData);
      setAmount(productData.price);

      // Check access if user address is provided
      if (userAddress) {
        await checkAccess();
      }
    } catch (err) {
      setError(`Failed to load product: ${err instanceof Error ? err.message : 'Unknown error'}`);
    } finally {
      setIsLoading(false);
    }
  }, [v402Provider, productId, userAddress]);

  // Check access
  const checkAccess = useCallback(async () => {
    if (!userAddress || !accessService) return;

    try {
      const accessResponse = await accessService.checkAccess({
        productId,
        userAddress,
        timestamp: Date.now(),
        signature: 'mock-signature' // In real implementation, this would be generated
      });

      setHasAccess(accessResponse.has_access);

      if (accessResponse.has_access) {
        setPaymentStatus({
          status: 'success',
          message: 'Access granted! You can now view the content.'
        });
      }
    } catch (err) {
      console.warn('Failed to check access:', err instanceof Error ? err.message : 'Unknown error');
    }
  }, [userAddress, accessService, productId]);

  // Process payment
  const processPayment = useCallback(async () => {
    if (!userAddress || !amount || !paymentService || !product) {
      setError('Please provide your Ethereum address and amount');
      return;
    }

    try {
      setIsProcessing(true);
      setError(null);
      setPaymentStatus(null);

      const paymentRequest: PaymentRequest = {
        productId,
        amount,
        currency: product.currency,
        userAddress,
        nonce: `nonce-${Date.now()}`,
        signature: 'mock-signature' // In real implementation, this would be generated
      };

      const paymentResponse = await paymentService.processPayment(paymentRequest);

      if (paymentResponse.status === 'completed') {
        setPaymentStatus({
          status: 'success',
          message: `Payment successful! Transaction: ${paymentResponse.transaction_hash}`
        });

        // Update product purchase count
        setProduct(prev => prev ? { ...prev, purchase_count: prev.purchase_count + 1 } : null);

        // Grant access
        setHasAccess(true);

        // Call success callback
        onPaymentSuccess?.({
          product: product,
          payment: paymentResponse
        });
      } else {
        setPaymentStatus({
          status: 'error',
          message: `Payment failed: ${paymentResponse.error || 'Unknown error'}`
        });
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      setError(`Payment failed: ${errorMessage}`);
      setPaymentStatus({
        status: 'error',
        message: errorMessage
      });
      onPaymentError?.(errorMessage);
    } finally {
      setIsProcessing(false);
    }
  }, [userAddress, amount, paymentService, product, productId, onPaymentSuccess, onPaymentError]);

  // Clear error
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  // Load product when services are ready
  useEffect(() => {
    if (v402Provider) {
      loadProduct();
    }
  }, [v402Provider, loadProduct]);

  // Check access when user address changes
  useEffect(() => {
    if (userAddress) {
      checkAccess();
    }
  }, [userAddress, checkAccess]);

  // Computed values
  const conversionRate = product && product.view_count > 0
    ? ((product.purchase_count / product.view_count) * 100).toFixed(2)
    : '0';

  if (isLoading) {
    return (
      <div className={`${styles.container} ${className || ''}`}>
        <div className={styles.loading}>
          <div className={styles.spinner}></div>
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`${styles.container} ${className || ''}`}>
        <div className={styles.error}>
          <h3>Error</h3>
          <p>{error}</p>
          <button onClick={clearError} className={styles.retryButton}>
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!product) {
    return (
      <div className={`${styles.container} ${className || ''}`}>
        <div className={styles.error}>
          <h3>Product Not Found</h3>
          <p>The requested product could not be loaded.</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`${styles.container} ${className || ''}`}>
      <div className={styles.productCard}>
        <div className={styles.productHeader}>
          <h2 className={styles.productTitle}>{product.title}</h2>
          <div className={styles.productPrice}>
            {product.price} {product.currency}
          </div>
        </div>

        <div className={styles.productContent}>
          <p className={styles.productDescription}>{product.description}</p>

          {(product.category || product.tags.length > 0) && (
            <div className={styles.productMeta}>
              {product.category && (
                <div className={styles.productCategory}>
                  <span className={styles.label}>Category:</span>
                  <span className={styles.value}>{product.category}</span>
                </div>
              )}

              {product.tags.length > 0 && (
                <div className={styles.productTags}>
                  <span className={styles.label}>Tags:</span>
                  {product.tags.map(tag => (
                    <span key={tag} className={styles.tag}>
                      {tag}
                    </span>
                  ))}
                </div>
              )}
            </div>
          )}

          <div className={styles.productStats}>
            <div className={styles.stat}>
              <span className={styles.statLabel}>Views:</span>
              <span className={styles.statValue}>{product.view_count}</span>
            </div>
            <div className={styles.stat}>
              <span className={styles.statLabel}>Purchases:</span>
              <span className={styles.statValue}>{product.purchase_count}</span>
            </div>
            {product.purchase_count > 0 && (
              <div className={styles.stat}>
                <span className={styles.statLabel}>Conversion Rate:</span>
                <span className={styles.statValue}>{conversionRate}%</span>
              </div>
            )}
          </div>
        </div>

        <div className={styles.paymentSection}>
          {paymentStatus && (
            <div className={styles.paymentStatus}>
              <div className={`${styles.statusMessage} ${styles[paymentStatus.status]}`}>
                {paymentStatus.message}
              </div>
            </div>
          )}

          {!hasAccess && !isProcessing && (
            <div className={styles.paymentForm}>
              <div className={styles.formGroup}>
                <label htmlFor="userAddress">Your Ethereum Address:</label>
                <input
                  id="userAddress"
                  type="text"
                  placeholder="0x..."
                  className={styles.formInput}
                  value={userAddress}
                  onChange={(e) => setUserAddress(e.target.value)}
                  disabled={isProcessing}
                />
              </div>

              <div className={styles.formGroup}>
                <label htmlFor="amount">Amount:</label>
                <input
                  id="amount"
                  type="text"
                  placeholder={product.price}
                  className={styles.formInput}
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                  disabled={isProcessing}
                />
              </div>

              <button
                onClick={processPayment}
                disabled={isProcessing || !userAddress}
                className={styles.paymentButton}
              >
                {isProcessing ? 'Processing...' : `Pay ${amount || product.price} ${product.currency}`}
              </button>
            </div>
          )}

          {hasAccess && (
            <div className={styles.accessSection}>
              <div className={styles.accessGranted}>
                <h3>Access Granted!</h3>
                <p>You now have access to this content.</p>
                <a href={product.content_url} target="_blank" rel="noopener noreferrer" className={styles.contentLink}>
                  Access Content
                </a>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default V402PaymentButton;
