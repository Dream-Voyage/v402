/**
 * @v402/provider - JavaScript/TypeScript Provider for v402 Protocol
 * 
 * Main entry point for the v402 provider library, supporting multiple
 * frontend frameworks and vanilla JavaScript integration.
 * 
 * @author v402 Team
 * @version 1.0.0
 */

// Core exports
export { 
  V402Provider, 
  PaymentError,
  type V402ProviderConfig,
  type ChainConfig,
  type ThemeConfig,
  type WalletConfig,
  type AnalyticsConfig,
  type PaymentButtonConfig,
  type PaymentResult,
  type PaymentStatus,
  type PaymentRequirements,
} from './core/V402Provider';

// Utility exports
export { createPaymentButton } from './utils/createPaymentButton';
export { detectWallet } from './utils/walletDetection';
export { formatAmount, parseAmount } from './utils/formatters';
export { validateChainConfig } from './utils/validators';

// Constants
export const VERSION = '__VERSION__';
export const SUPPORTED_CHAINS = [
  'ethereum',
  'base', 
  'polygon',
  'arbitrum',
  'optimism',
  'bsc',
  'solana',
] as const;

export const DEFAULT_THEME = {
  primaryColor: '#3B82F6',
  secondaryColor: '#64748B',
  backgroundColor: '#FFFFFF',
  textColor: '#1F2937',
  borderRadius: '8px',
  fontFamily: 'system-ui, -apple-system, sans-serif',
} as const;

/**
 * Quick setup function for easy integration
 * 
 * @example
 * ```typescript
 * import { quickSetup } from '@v402/provider';
 * 
 * const { provider, createButton } = await quickSetup({
 *   chains: ['ethereum', 'base'],
 *   theme: { primaryColor: '#FF6B35' }
 * });
 * 
 * const button = createButton({
 *   resourceId: 'premium-content',
 *   description: 'Unlock premium features',
 *   amount: '1000000000000000000', // 1 ETH
 * });
 * 
 * document.body.appendChild(button);
 * ```
 */
export async function quickSetup(config?: V402ProviderConfig) {
  const { V402Provider } = await import('./core/V402Provider');
  const { createPaymentButton } = await import('./utils/createPaymentButton');
  
  const provider = new V402Provider(config);
  await provider.initialize();
  
  return {
    provider,
    createButton: (buttonConfig: PaymentButtonConfig) => {
      return createPaymentButton(buttonConfig, provider);
    },
  };
}

/**
 * Framework-specific exports (these will be tree-shaken if not used)
 */

// React (will be excluded if React is not available)
export type { V402PaymentButtonProps, V402PaymentButtonHandle } from './react/V402PaymentButton';

// Vue (will be excluded if Vue is not available) 
export type { V402PaymentButtonVueProps } from './vue/V402PaymentButton.vue';

// Web Components
export type { V402PaymentElement } from './web-components/V402PaymentElement';

// Lazy load framework components
export const loadReactComponent = () => import('./react/V402PaymentButton');
export const loadVueComponent = () => import('./vue/V402PaymentButton.vue');
export const loadWebComponent = () => import('./web-components/V402PaymentElement');
