import React from 'react';
import Head from 'next/head';
import V402PaymentButton from '../components/V402PaymentButton';

const PaymentPage: React.FC = () => {
  const handlePaymentSuccess = (data: any) => {
    console.log('Payment successful:', data);
    // Handle successful payment
    alert(`Payment successful! Transaction: ${data.payment.transaction_hash}`);
  };

  const handlePaymentError = (error: string) => {
    console.error('Payment failed:', error);
    // Handle payment error
    alert(`Payment failed: ${error}`);
  };

  return (
    <>
      <Head>
        <title>V402 Payment Button - Next.js Example</title>
        <meta name="description" content="V402 Payment Button integration example with Next.js" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>

      <div className="container">
        <div className="header">
          <h1>V402 Payment Button</h1>
          <p>Next.js Integration Example</p>
        </div>

        <div className="example-section">
          <h2>Live Example</h2>
          <p>
            This is a working example of the V402 Payment Button component integrated with Next.js.
            The component handles product loading, payment processing, and access management.
          </p>

          <V402PaymentButton
            productId="product-123"
            apiUrl="https://api.v402.network"
            publicKey="0x1234567890abcdef1234567890abcdef12345678"
            privateKey="0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"
            onPaymentSuccess={handlePaymentSuccess}
            onPaymentError={handlePaymentError}
          />
        </div>

        <div className="example-section">
          <h2>Code Example</h2>
          <p>Here's how to use the V402 Payment Button in your Next.js application:</p>
          
          <div className="code-example">
            <pre>{`import V402PaymentButton from '../components/V402PaymentButton';

const PaymentPage = () => {
  const handlePaymentSuccess = (data) => {
    console.log('Payment successful:', data);
    // Handle successful payment
  };

  const handlePaymentError = (error) => {
    console.error('Payment failed:', error);
    // Handle payment error
  };

  return (
    <V402PaymentButton
      productId="product-123"
      apiUrl="https://api.v402.network"
      publicKey="0x1234567890abcdef1234567890abcdef12345678"
      privateKey="0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"
      onPaymentSuccess={handlePaymentSuccess}
      onPaymentError={handlePaymentError}
    />
  );
};`}</pre>
          </div>
        </div>

        <div className="example-section">
          <h2>Features</h2>
          <ul>
            <li>Product loading and display</li>
            <li>Payment processing with blockchain integration</li>
            <li>Access control and verification</li>
            <li>Real-time status updates</li>
            <li>Error handling and retry functionality</li>
            <li>Responsive design</li>
            <li>TypeScript support</li>
            <li>Event callbacks for integration</li>
          </ul>
        </div>

        <div className="example-section">
          <h2>Props</h2>
          <div className="props-table">
            <table>
              <thead>
                <tr>
                  <th>Prop</th>
                  <th>Type</th>
                  <th>Required</th>
                  <th>Description</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>productId</td>
                  <td>string</td>
                  <td>Yes</td>
                  <td>The ID of the product to display</td>
                </tr>
                <tr>
                  <td>apiUrl</td>
                  <td>string</td>
                  <td>No</td>
                  <td>The base URL for the v402 API (default: https://api.v402.network)</td>
                </tr>
                <tr>
                  <td>publicKey</td>
                  <td>string</td>
                  <td>Yes</td>
                  <td>The public key for authentication</td>
                </tr>
                <tr>
                  <td>privateKey</td>
                  <td>string</td>
                  <td>Yes</td>
                  <td>The private key for authentication</td>
                </tr>
                <tr>
                  <td>onPaymentSuccess</td>
                  <td>function</td>
                  <td>No</td>
                  <td>Callback function called when payment is successful</td>
                </tr>
                <tr>
                  <td>onPaymentError</td>
                  <td>function</td>
                  <td>No</td>
                  <td>Callback function called when payment fails</td>
                </tr>
                <tr>
                  <td>className</td>
                  <td>string</td>
                  <td>No</td>
                  <td>Additional CSS class for styling</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <style jsx>{`
        .container {
          max-width: 800px;
          margin: 0 auto;
          padding: 20px;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }

        .header {
          text-align: center;
          margin-bottom: 40px;
        }

        .header h1 {
          color: #333;
          margin-bottom: 10px;
        }

        .header p {
          color: #666;
          font-size: 18px;
        }

        .example-section {
          background: white;
          border-radius: 12px;
          padding: 30px;
          margin-bottom: 30px;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }

        .example-section h2 {
          font-size: 24px;
          color: #333;
          margin-bottom: 20px;
          border-bottom: 2px solid #667eea;
          padding-bottom: 10px;
        }

        .example-section p {
          color: #666;
          margin-bottom: 20px;
          line-height: 1.6;
        }

        .code-example {
          background: #f8f9fa;
          border: 1px solid #e9ecef;
          border-radius: 8px;
          padding: 20px;
          margin: 20px 0;
          font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
          font-size: 14px;
          overflow-x: auto;
        }

        .code-example pre {
          margin: 0;
          white-space: pre-wrap;
        }

        .props-table {
          overflow-x: auto;
        }

        .props-table table {
          width: 100%;
          border-collapse: collapse;
          margin-top: 20px;
        }

        .props-table th,
        .props-table td {
          border: 1px solid #e9ecef;
          padding: 12px;
          text-align: left;
        }

        .props-table th {
          background: #f8f9fa;
          font-weight: 600;
          color: #333;
        }

        .props-table td {
          color: #666;
        }

        .props-table tr:nth-child(even) {
          background: #f8f9fa;
        }

        ul {
          color: #666;
          line-height: 1.6;
        }

        li {
          margin-bottom: 8px;
        }
      `}</style>
    </>
  );
};

export default PaymentPage;
