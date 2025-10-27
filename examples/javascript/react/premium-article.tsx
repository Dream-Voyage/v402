/**
 * Premium Article Example with React
 *
 * Demonstrates a complete premium article component with:
 * - Content paywall
 * - Payment integration with v402
 * - Access management
 * - User-friendly UI/UX
 * - Error handling
 */

import React, {useState} from 'react';
import {useV402Payment} from '@v402/providers/react';
import './premium-article.css';

interface Article {
  id: string;
  title: string;
  author: string;
  publishDate: string;
  category: string;
  preview: string;
  content: string;
  isPremium: boolean;
  paymentAmount: string;
  currency: string;
}

interface PremiumArticleProps {
  article: Article;
  userAddress?: string;
  hasAccess: boolean;
}

const PremiumArticle: React.FC<PremiumArticleProps> = ({
  article,
  userAddress,
  hasAccess
}) => {
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [accessGranted, setAccessGranted] = useState(hasAccess);

  const {
    initiatePayment,
    processing,
    error,
    transactionHash,
  } = useV402Payment({
    productId: article.id,
    amount: article.paymentAmount,
    currency: article.currency,
    onSuccess: handlePaymentSuccess,
    onError: handlePaymentError,
  });

  function handlePaymentSuccess(result: any) {
    console.log('Payment successful:', result);
    setAccessGranted(true);
    setShowPaymentModal(false);

    // Track analytics
    if (window.gtag) {
      window.gtag('event', 'payment_success', {
        'value': article.paymentAmount,
        'currency': article.currency,
        'article_id': article.id,
      });
    }
  }

  function handlePaymentError(error: Error) {
    console.error('Payment failed:', error);

    // Show user-friendly error message
    alert(`Payment failed: ${error.message}`);

    // Track error analytics
    if (window.gtag) {
      window.gtag('event', 'payment_error', {
        'error_message': error.message,
        'article_id': article.id,
      });
    }
  }

  async function handleUnlockClick() {
    try {
      await initiatePayment();
      setShowPaymentModal(true);
    } catch (error) {
      console.error('Failed to initiate payment:', error);
    }
  }

  if (accessGranted) {
    return (
      <div className="premium-article">
        <header className="article-header">
          <div className="badge premium-badge">Premium</div>
          <h1>{article.title}</h1>
          <div className="article-meta">
            <span className="author">By {article.author}</span>
            <span className="date">{new Date(article.publishDate).toLocaleDateString()}</span>
            <span className="category">{article.category}</span>
          </div>
        </header>

        <main className="article-content">
          <div dangerouslySetInnerHTML={{ __html: article.content }} />
        </main>

        <footer className="article-footer">
          <div className="share-buttons">
            <button className="share-btn twitter">Share on Twitter</button>
            <button className="share-btn linkedin">Share on LinkedIn</button>
            <button className="share-btn facebook">Share on Facebook</button>
          </div>

          <div className="feedback">
            <button className="like-btn">👍 Like</button>
            <button className="comment-btn">💬 Comment</button>
            <button className="bookmark-btn">🔖 Bookmark</button>
          </div>
        </footer>
      </div>
    );
  }

  return (
    <div className="premium-article-paywall">
      <header className="article-header">
        <div className="badge premium-badge">Premium</div>
        <h1>{article.title}</h1>
        <div className="article-meta">
          <span className="author">By {article.author}</span>
          <span className="date">{new Date(article.publishDate).toLocaleDateString()}</span>
          <span className="category">{article.category}</span>
        </div>
      </header>

      <div className="preview-content">
        <p>{article.preview}</p>
      </div>

      <div className="paywall">
        <div className="paywall-content">
          <h2>🔒 Premium Content</h2>
          <p className="paywall-description">
            This article contains exclusive premium content.
            Unlock full access to continue reading.
          </p>

          <div className="payment-section">
            <div className="price-display">
              <span className="amount">{parseFloat(article.paymentAmount) / 1e18}</span>
              <span className="currency">{article.currency}</span>
            </div>

            <div className="payment-features">
              <div className="feature">
                <span className="icon">✓</span>
                <span>Instant access</span>
              </div>
              <div className="feature">
                <span className="icon">✓</span>
                <span>Lifetime ownership</span>
              </div>
              <div className="feature">
                <span className="icon">✓</span>
                <span>Support the author</span>
              </div>
            </div>

            <button
              className="unlock-button"
              onClick={handleUnlockClick}
              disabled={processing || !userAddress}
            >
              {processing ? (
                <>
                  <span className="spinner">⏳</span>
                  Processing...
                </>
              ) : (
                <>
                  <span className="icon">🔓</span>
                  Unlock Article
                </>
              )}
            </button>

            {!userAddress && (
              <div className="wallet-prompt">
                <p>Please connect your wallet to continue</p>
                <button className="connect-wallet-btn">
                  Connect Wallet
                </button>
              </div>
            )}

            {error && (
              <div className="error-message">
                <span className="icon">⚠️</span>
                {error.message}
              </div>
            )}
          </div>

          <div className="trust-badges">
            <div className="badge">
              <span className="icon">🔒</span>
              Secure Payment
            </div>
            <div className="badge">
              <span className="icon">⚡</span>
              Instant Access
            </div>
            <div className="badge">
              <span className="icon">🌐</span>
              Multi-Chain
            </div>
          </div>
        </div>
      </div>

      {showPaymentModal && (
        <PaymentModal
          isOpen={showPaymentModal}
          onClose={() => setShowPaymentModal(false)}
          processing={processing}
          error={error}
          transactionHash={transactionHash}
        />
      )}
    </div>
  );
};

interface PaymentModalProps {
  isOpen: boolean;
  onClose: () => void;
  processing: boolean;
  error: Error | null;
  transactionHash: string | null;
}

const PaymentModal: React.FC<PaymentModalProps> = ({
  isOpen,
  onClose,
  processing,
  error,
  transactionHash,
}) => {
  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        {processing && (
          <div className="payment-processing">
            <div className="processing-animation">
              <div className="spinner-large">⏳</div>
            </div>
            <h3>Processing Payment</h3>
            <p>Please wait while we confirm your transaction...</p>
          </div>
        )}

        {transactionHash && (
          <div className="payment-success">
            <div className="success-icon">✓</div>
            <h3>Payment Successful!</h3>
            <p>Your access has been granted.</p>
            <a
              href={`https://etherscan.io/tx/${transactionHash}`}
              target="_blank"
              rel="noopener noreferrer"
            >
              View Transaction
            </a>
          </div>
        )}

        {error && (
          <div className="payment-error">
            <div className="error-icon">⚠️</div>
            <h3>Payment Failed</h3>
            <p>{error.message}</p>
            <button onClick={onClose}>Close</button>
          </div>
        )}
      </div>
    </div>
  );
};

export default PremiumArticle;

