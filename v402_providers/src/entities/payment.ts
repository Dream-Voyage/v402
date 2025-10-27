/**
 * V402 Providers SDK - Payment Entity Definitions
 *
 * This file contains all payment-related entity interfaces and types
 * for handling transactions, payments, refunds, and settlements in the V402 ecosystem.
 *
 * @author V402 Team
 * @version 1.0.0
 * @since 2024-01-01
 */

import {z} from 'zod';
import {BaseEntity, BaseEntitySchema, Money, MoneySchema} from './base';

/**
 * Payment entity representing a transaction
 */
export interface Payment extends BaseEntity {
  readonly paymentId: string;
  readonly productId: string;
  readonly providerId: string;
  readonly clientId?: string;
  readonly userId?: string;
  readonly amount: Money;
  readonly fee: Money;
  readonly totalAmount: Money;
  readonly status: PaymentStatus;
  readonly method: PaymentMethod;
  readonly type: PaymentType;
  readonly currency: string;
  readonly blockchain: BlockchainInfo;
  readonly transaction: TransactionInfo;
  readonly authorization: AuthorizationInfo;
  readonly settlement: SettlementInfo;
  readonly refund?: RefundInfo;
  readonly metadata: PaymentMetadata;
  readonly timestamps: PaymentTimestamps;
  readonly fraud: FraudDetection;
  readonly compliance: ComplianceInfo;
}

/**
 * Payment status enumeration
 */
export enum PaymentStatus {
  PENDING = 'pending',
  AUTHORIZED = 'authorized',
  PROCESSING = 'processing',
  CONFIRMING = 'confirming',
  CONFIRMED = 'confirmed',
  SETTLED = 'settled',
  PARTIALLY_SETTLED = 'partially_settled',
  FAILED = 'failed',
  CANCELLED = 'cancelled',
  REFUNDED = 'refunded',
  PARTIALLY_REFUNDED = 'partially_refunded',
  DISPUTED = 'disputed',
  REVERSED = 'reversed',
  EXPIRED = 'expired',
  ABANDONED = 'abandoned',
}

/**
 * Payment method types
 */
export enum PaymentMethod {
  // Blockchain payments
  ETHEREUM = 'ethereum',
  BITCOIN = 'bitcoin',
  POLYGON = 'polygon',
  BSC = 'bsc',
  ARBITRUM = 'arbitrum',
  OPTIMISM = 'optimism',
  BASE = 'base',
  SOLANA = 'solana',

  // Traditional payments
  CREDIT_CARD = 'credit_card',
  DEBIT_CARD = 'debit_card',
  BANK_TRANSFER = 'bank_transfer',
  WIRE_TRANSFER = 'wire_transfer',
  ACH = 'ach',
  SEPA = 'sepa',

  // Digital wallets
  PAYPAL = 'paypal',
  STRIPE = 'stripe',
  APPLE_PAY = 'apple_pay',
  GOOGLE_PAY = 'google_pay',
  SAMSUNG_PAY = 'samsung_pay',
  ALIPAY = 'alipay',
  WECHAT_PAY = 'wechat_pay',

  // Cryptocurrency payment gateways
  COINBASE = 'coinbase',
  BITPAY = 'bitpay',
  CRYPTOCOM = 'cryptocom',

  // Others
  SUBSCRIPTION = 'subscription',
  CREDIT = 'credit',
  GIFT_CARD = 'gift_card',
  LAYAWAY = 'layaway',
  INVOICE = 'invoice',
  OFFLINE = 'offline',
}

/**
 * Payment type classification
 */
export enum PaymentType {
  PURCHASE = 'purchase',
  SUBSCRIPTION = 'subscription',
  RENTAL = 'rental',
  ACCESS = 'access',
  LICENSE = 'license',
  DONATION = 'donation',
  REFUND = 'refund',
  CHARGEBACK = 'chargeback',
  REVERSAL = 'reversal',
  ADJUSTMENT = 'adjustment',
  FEE = 'fee',
  COMMISSION = 'commission',
  ROYALTY = 'royalty',
  AUTHORIZATION = 'authorization',
  CAPTURE = 'capture',
  VOID = 'void',
}

/**
 * Blockchain information
 */
export interface BlockchainInfo {
  readonly network: string;
  readonly chainId: number;
  readonly currency: string;
  readonly nativeToken: string;
  readonly rpcUrl?: string;
  readonly explorerUrl?: string;
  readonly supportedStandards: string[]; // e.g., ERC20, ERC721
  readonly gasConfig?: GasConfig;
}

/**
 * Gas configuration for EVM chains
 */
export interface GasConfig {
  readonly gasPrice?: string;
  readonly maxFeePerGas?: string;
  readonly maxPriorityFeePerGas?: string;
  readonly gasLimit?: string;
  readonly estimatedCost?: Money;
}

/**
 * Transaction information
 */
export interface TransactionInfo {
  readonly transactionHash?: string;
  readonly blockNumber?: number;
  readonly blockHash?: string;
  readonly confirmations: number;
  readonly requiredConfirmations: number;
  readonly receipt?: TransactionReceipt;
  readonly status: TransactionStatus;
  readonly nonce?: number;
  readonly from: string;
  readonly to: string;
  readonly input?: string;
  readonly events?: TransactionEvent[];
}

/**
 * Transaction status
 */
export enum TransactionStatus {
  PENDING = 'pending',
  CONFIRMING = 'confirming',
  CONFIRMED = 'confirmed',
  FAILED = 'failed',
  REVERTED = 'reverted',
  DROPPED = 'dropped',
}

/**
 * Transaction receipt
 */
export interface TransactionReceipt {
  readonly transactionHash: string;
  readonly transactionIndex: number;
  readonly blockHash: string;
  readonly blockNumber: number;
  readonly from: string;
  readonly to: string | null;
  readonly cumulativeGasUsed: string;
  readonly effectiveGasPrice?: string;
  readonly gasUsed: string;
  readonly contractAddress: string | null;
  readonly logs: TransactionLog[];
  readonly status: number; // 1 = success, 0 = failure
  readonly logsBloom: string;
  readonly root?: string;
  readonly type?: number;
}

/**
 * Transaction log entry
 */
export interface TransactionLog {
  readonly address: string;
  readonly topics: string[];
  readonly data: string;
  readonly logIndex: number;
  readonly transactionHash: string;
  readonly transactionIndex: number;
  readonly blockHash: string;
  readonly blockNumber: number;
  readonly removed: boolean;
}

/**
 * Transaction event
 */
export interface TransactionEvent {
  readonly address: string;
  readonly name: string;
  readonly signature: string;
  readonly decodedData?: Record<string, any>;
  readonly logs: TransactionLog[];
}

/**
 * Authorization information
 */
export interface AuthorizationInfo {
  readonly authorized: boolean;
  readonly authorizationId?: string;
  readonly authorizationType: AuthorizationType;
  readonly authorizedAmount: Money;
  readonly authorizedAt?: Date;
  readonly expiresAt?: Date;
  readonly capturedAmount?: Money;
  readonly remainingAmount?: Money;
  readonly authorizationCode?: string;
  readonly avsResult?: string;
  readonly cvvResult?: string;
}

/**
 * Authorization types
 */
export enum AuthorizationType {
  EIP_3009 = 'eip3009',
  ERC_2612 = 'erc2612',
  PERMIT = 'permit',
  SIGNATURE = 'signature',
  PIN = 'pin',
  BIOMETRIC = 'biometric',
  OTP = 'otp',
  MAGIC_LINK = 'magic_link',
  OAUTH = 'oauth',
}

/**
 * Settlement information
 */
export interface SettlementInfo {
  readonly settled: boolean;
  readonly settlementId?: string;
  readonly settlementDate?: Date;
  readonly settledAmount: Money;
  readonly settlementFee: Money;
  readonly netAmount: Money;
  readonly settlementStatus: SettlementStatus;
  readonly settlementType: SettlementType;
  readonly paymentSplit?: PaymentSplit[];
  readonly receipts?: SettlementReceipt[];
}

/**
 * Settlement status
 */
export enum SettlementStatus {
  PENDING = 'pending',
  PROCESSING = 'processing',
  SETTLED = 'settled',
  FAILED = 'failed',
  REVERSED = 'reversed',
  PARTIAL = 'partial',
}

/**
 * Settlement types
 */
export enum SettlementType {
  INSTANT = 'instant',
  SCHEDULED = 'scheduled',
  MANUAL = 'manual',
  AUTOMATIC = 'automatic',
}

/**
 * Payment split for multiple recipients
 */
export interface PaymentSplit {
  readonly recipientId: string;
  readonly recipientType: RecipientType;
  readonly amount: Money;
  readonly percentage: number;
  readonly reference?: string;
  readonly settled: boolean;
  readonly settlementDate?: Date;
}

/**
 * Recipient types
 */
export enum RecipientType {
  PROVIDER = 'provider',
  CREATOR = 'creator',
  AFFILIATE = 'affiliate',
  PLATFORM = 'platform',
  TAX = 'tax',
  FEE = 'fee',
  CHARITY = 'charity',
  LEGACY = 'legacy',
}

/**
 * Settlement receipt
 */
export interface SettlementReceipt {
  readonly receiptId: string;
  readonly receiptUrl: string;
  readonly receiptFormat: ReceiptFormat;
  readonly issuedAt: Date;
  readonly downloadUrl?: string;
  readonly emailSent: boolean;
}

/**
 * Receipt formats
 */
export enum ReceiptFormat {
  PDF = 'pdf',
  PNG = 'png',
  HTML = 'html',
  JSON = 'json',
  EMAIL = 'email',
}

/**
 * Refund information
 */
export interface RefundInfo {
  readonly refundId: string;
  readonly refunded: boolean;
  readonly refundType: RefundType;
  readonly refundAmount: Money;
  readonly refundFee: Money;
  readonly refundReason?: string;
  readonly refundInitiatedAt?: Date;
  readonly refundCompletedAt?: Date;
  readonly refundStatus: RefundStatus;
  readonly originalPaymentId: string;
  readonly refundTransaction?: TransactionInfo;
}

/**
 * Refund types
 */
export enum RefundType {
  FULL = 'full',
  PARTIAL = 'partial',
  REVERSAL = 'reversal',
  CHARGEBACK = 'chargeback',
  ADMIN = 'admin',
  AUTOMATIC = 'automatic',
}

/**
 * Refund status
 */
export enum RefundStatus {
  PENDING = 'pending',
  PROCESSING = 'processing',
  PROCESSED = 'processed',
  COMPLETED = 'completed',
  FAILED = 'failed',
  CANCELLED = 'cancelled',
}

/**
 * Payment metadata
 */
export interface PaymentMetadata {
  readonly ipAddress?: string;
  readonly userAgent?: string;
  readonly deviceType?: DeviceType;
  readonly platform?: string;
  readonly sessionId?: string;
  readonly referrer?: string;
  readonly utm?: UTMParameters;
  readonly customFields?: Record<string, any>;
  readonly tags?: string[];
  readonly notes?: string;
}

/**
 * Device types
 */
export enum DeviceType {
  DESKTOP = 'desktop',
  MOBILE = 'mobile',
  TABLET = 'tablet',
  SMART_TV = 'smart_tv',
  GAME_CONSOLE = 'game_console',
  SMART_SPEAKER = 'smart_speaker',
  IOT_DEVICE = 'iot_device',
  UNKNOWN = 'unknown',
}

/**
 * UTM parameters
 */
export interface UTMParameters {
  readonly utmSource?: string;
  readonly utmMedium?: string;
  readonly utmCampaign?: string;
  readonly utmTerm?: string;
  readonly utmContent?: string;
}

/**
 * Payment timestamps
 */
export interface PaymentTimestamps {
  readonly createdAt: Date;
  readonly updatedAt: Date;
  readonly initiatedAt?: Date;
  readonly authorizedAt?: Date;
  readonly confirmedAt?: Date;
  readonly settledAt?: Date;
  readonly refundedAt?: Date;
  readonly cancelledAt?: Date;
  readonly expiredAt?: Date;
}

/**
 * Fraud detection information
 */
export interface FraudDetection {
  readonly enabled: boolean;
  readonly score?: number;
  readonly risk: RiskLevel;
  readonly reasons?: string[];
  readonly flagged: boolean;
  readonly reviewed: boolean;
  readonly decision?: FraudDecision;
  readonly confidence: number;
}

/**
 * Risk levels
 */
export enum RiskLevel {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  CRITICAL = 'critical',
}

/**
 * Fraud decisions
 */
export enum FraudDecision {
  APPROVE = 'approve',
  REVIEW = 'review',
  BLOCK = 'block',
  CHALLENGE = 'challenge',
}

/**
 * Compliance information
 */
export interface ComplianceInfo {
  readonly kyc: KYCInfo;
  readonly aml: AMLInfo;
  readonly sanctions: SanctionsInfo;
  readonly gdpr: GDPRInfo;
  readonly tax: TaxInfo;
  readonly legal: LegalInfo;
}

/**
 * KYC (Know Your Customer) information
 */
export interface KYCInfo {
  readonly required: boolean;
  readonly verified: boolean;
  readonly level: KYCLevel;
  readonly verifiedAt?: Date;
  readonly expiresAt?: Date;
  readonly provider?: string;
}

/**
 * KYC levels
 */
export enum KYCLevel {
  NONE = 'none',
  BASIC = 'basic',
  STANDARD = 'standard',
  ENHANCED = 'enhanced',
  FULL = 'full',
}

/**
 * AML (Anti-Money Laundering) information
 */
export interface AMLInfo {
  readonly screening: boolean;
  readonly passed: boolean;
  readonly flaggedAt?: Date;
  readonly reviewedAt?: Date;
}

/**
 * Sanctions information
 */
export interface SanctionsInfo {
  readonly screened: boolean;
  readonly passed: boolean;
  readonly lists?: string[];
  readonly checkedAt?: Date;
}

/**
 * GDPR information
 */
export interface GDPRInfo {
  readonly consentGiven: boolean;
  readonly consentDate?: Date;
  readonly dataRetentionConsent: boolean;
  readonly marketingConsent: boolean;
  readonly processingConsent: boolean;
}

/**
 * Tax information
 */
export interface TaxInfo {
  readonly required: boolean;
  readonly calculated: boolean;
  readonly taxAmount?: Money;
  readonly taxRate?: number;
  readonly taxId?: string;
  readonly jurisdiction?: string;
  readonly exempt?: boolean;
}

/**
 * Legal information
 */
export interface LegalInfo {
  readonly termsAccepted: boolean;
  readonly termsVersion?: string;
  readonly privacyAccepted: boolean;
  readonly privacyVersion?: string;
  readonly jurisdiction?: string;
  readonly regulated?: boolean;
}

// Additional payment types

/**
 * Payment request
 */
export interface PaymentRequest {
  readonly productId: string;
  readonly amount: Money;
  readonly paymentMethod?: PaymentMethod;
  readonly blockchain?: BlockchainInfo;
  readonly metadata?: PaymentMetadata;
  readonly authorizeOnly?: boolean;
  readonly expiry?: Date;
}

/**
 * Payment response
 */
export interface PaymentResponse {
  readonly payment: Payment;
  readonly authorizationUrl?: string;
  readonly qrCode?: string;
  readonly deepLink?: string;
  readonly instructions?: string;
  readonly nextSteps?: string[];
}

/**
 * Payment history filters
 */
export interface PaymentHistoryFilters {
  readonly productId?: string;
  readonly status?: PaymentStatus[];
  readonly method?: PaymentMethod[];
  readonly blockchain?: string[];
  readonly from?: Date;
  readonly to?: Date;
  readonly amountMin?: string;
  readonly amountMax?: string;
  readonly currency?: string;
}

// Zod schemas

export const PaymentStatusSchema = z.nativeEnum(PaymentStatus);
export const PaymentMethodSchema = z.nativeEnum(PaymentMethod);
export const PaymentTypeSchema = z.nativeEnum(PaymentType);

export const MoneyWithCurrencySchema = MoneySchema.extend({
  currency: z.string().length(3).toUpperCase(),
});

export const GasConfigSchema = z.object({
  gasPrice: z.string().optional(),
  maxFeePerGas: z.string().optional(),
  maxPriorityFeePerGas: z.string().optional(),
  gasLimit: z.string().optional(),
});

export const BlockchainInfoSchema = z.object({
  network: z.string(),
  chainId: z.number(),
  currency: z.string(),
  nativeToken: z.string(),
  rpcUrl: z.string().url().optional(),
  explorerUrl: z.string().url().optional(),
  supportedStandards: z.array(z.string()),
  gasConfig: GasConfigSchema.optional(),
});

export const RiskLevelSchema = z.nativeEnum(RiskLevel);
export const FraudDecisionSchema = z.nativeEnum(FraudDecision);
export const KYCLevelSchema = z.nativeEnum(KYCLevel);
export const DeviceTypeSchema = z.nativeEnum(DeviceType);

export const PaymentSchema = BaseEntitySchema.extend({
  paymentId: z.string().uuid(),
  productId: z.string().uuid(),
  providerId: z.string().uuid(),
  clientId: z.string().uuid().optional(),
  userId: z.string().uuid().optional(),
  amount: MoneyWithCurrencySchema,
  fee: MoneyWithCurrencySchema,
  totalAmount: MoneyWithCurrencySchema,
  status: PaymentStatusSchema,
  method: PaymentMethodSchema,
  type: PaymentTypeSchema,
  currency: z.string().length(3).toUpperCase(),
});

export type PaymentType = z.infer<typeof PaymentSchema>;
export type FraudDetectionType = {
  enabled: boolean;
  score?: number;
  risk: RiskLevel;
  reasons?: string[];
  flagged: boolean;
  reviewed: boolean;
  decision?: FraudDecision;
  confidence: number;
};
