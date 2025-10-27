/**
 * V402 Providers SDK - Event Constants
 * 
 * This file contains all event types, event names, and event-related
 * constants used throughout the V402 ecosystem including provider events,
 * payment events, analytics events, and system events.
 * 
 * @author V402 Team
 * @version 1.0.0
 * @since 2024-01-01
 */

/**
 * Event namespaces
 */
export const EVENT_NAMESPACES = {
  PROVIDER: 'v402.provider',
  PAYMENT: 'v402.payment',
  PRODUCT: 'v402.product',
  CLIENT: 'v402.client',
  ANALYTICS: 'v402.analytics',
  SYSTEM: 'v402.system',
  CACHE: 'v402.cache',
  NETWORK: 'v402.network',
  BLOCKCHAIN: 'v402.blockchain',
  SECURITY: 'v402.security',
  COMPLIANCE: 'v402.compliance',
} as const;

/**
 * Provider events
 */
export const PROVIDER_EVENTS = {
  CREATED: 'provider.created',
  UPDATED: 'provider.updated',
  DELETED: 'provider.deleted',
  ACTIVATED: 'provider.activated',
  DEACTIVATED: 'provider.deactivated',
  SUSPENDED: 'provider.suspended',
  UNSUSPENDED: 'provider.unsuspended',
  VERIFIED: 'provider.verified',
  UNVERIFIED: 'provider.unverified',
  KYC_COMPLETED: 'provider.kyc.completed',
  KYC_FAILED: 'provider.kyc.failed',
  BANK_ACCOUNT_ADDED: 'provider.bank.account.added',
  BANK_ACCOUNT_VERIFIED: 'provider.bank.account.verified',
  BANK_ACCOUNT_DELETED: 'provider.bank.account.deleted',
  SETTINGS_UPDATED: 'provider.settings.updated',
  PERMISSIONS_CHANGED: 'provider.permissions.changed',
  QUOTA_EXCEEDED: 'provider.quota.exceeded',
  REVENUE_THRESHOLD_REACHED: 'provider.revenue.threshold.reached',
} as const;

/**
 * Product events
 */
export const PRODUCT_EVENTS = {
  CREATED: 'product.created',
  UPDATED: 'product.updated',
  DELETED: 'product.deleted',
  PUBLISHED: 'product.published',
  UNPUBLISHED: 'product.unpublished',
  ARCHIVED: 'product.archived',
  RESTORED: 'product.restored',
  PRICING_CHANGED: 'product.pricing.changed',
  CATEGORY_CHANGED: 'product.category.changed',
  THUMBNAIL_UPDATED: 'product.thumbnail.updated',
  CONTENT_UPDATED: 'product.content.updated',
  METADATA_UPDATED: 'product.metadata.updated',
  SEO_UPDATED: 'product.seo.updated',
  VIEWED: 'product.viewed',
  PURCHASED: 'product.purchased',
  DOWNLOADED: 'product.downloaded',
  REVIEWED: 'product.reviewed',
  RATED: 'product.rated',
  SHARED: 'product.shared',
  FAVORITED: 'product.favorited',
  UNFAVORITED: 'product.unfavorited',
  CART_ADDED: 'product.cart.added',
  CART_REMOVED: 'product.cart.removed',
} as const;

/**
 * Payment events
 */
export const PAYMENT_EVENTS = {
  INITIATED: 'payment.initiated',
  AUTHORIZED: 'payment.authorized',
  CAPTURED: 'payment.captured',
  CONFIRMED: 'payment.confirmed',
  SETTLED: 'payment.settled',
  PARTIALLY_SETTLED: 'payment.partially_settled',
  FAILED: 'payment.failed',
  CANCELLED: 'payment.cancelled',
  REFUNDED: 'payment.refunded',
  PARTIALLY_REFUNDED: 'payment.partially_refunded',
  REVERSED: 'payment.reversed',
  DISPUTED: 'payment.disputed',
  EXPIRED: 'payment.expired',
  ABANDONED: 'payment.abandoned',
  PENDING_CONFIRMATION: 'payment.pending.confirmation',
  CONFIRMING: 'payment.confirming',
  REQUESTED: 'payment.requested',
  PROCESSING: 'payment.processing',
  VERIFIED: 'payment.verified',
  FRAUD_DETECTED: 'payment.fraud.detected',
  FRAUD_CLEARED: 'payment.fraud.cleared',
  CHARGEBACK: 'payment.chargeback',
  REPRESENTMENT: 'payment.representment',
} as const;

/**
 * Transaction events
 */
export const TRANSACTION_EVENTS = {
  SUBMITTED: 'transaction.submitted',
  PENDING: 'transaction.pending',
  CONFIRMING: 'transaction.confirming',
  CONFIRMED: 'transaction.confirmed',
  FAILED: 'transaction.failed',
  REVERTED: 'transaction.reverted',
  DROPPED: 'transaction.dropped',
  REPLACED: 'transaction.replaced',
  SPEED_UP: 'transaction.speed_up',
  CANCEL_REQUESTED: 'transaction.cancel.requested',
  EXPIRED: 'transaction.expired',
} as const;

/**
 * Client events
 */
export const CLIENT_EVENTS = {
  CREATED: 'client.created',
  UPDATED: 'client.updated',
  DELETED: 'client.deleted',
  ACTIVATED: 'client.activated',
  DEACTIVATED: 'client.deactivated',
  VERIFIED: 'client.verified',
  UNVERIFIED: 'client.unverified',
  API_KEY_CREATED: 'client.api.key.created',
  API_KEY_REVOKED: 'client.api.key.revoked',
  API_KEY_ROTATED: 'client.api.key.rotated',
  QUOTA_EXCEEDED: 'client.quota.exceeded',
  QUOTA_RESET: 'client.quota.reset',
} as const;

/**
 * Analytics events
 */
export const ANALYTICS_EVENTS = {
  TRACKED: 'analytics.tracked',
  VIEW_TRACKED: 'analytics.view.tracked',
  CONVERSION_TRACKED: 'analytics.conversion.tracked',
  REVENUE_TRACKED: 'analytics.revenue.tracked',
  EVENT_RECORDED: 'analytics.event.recorded',
  METRIC_UPDATED: 'analytics.metric.updated',
  SEGMENT_CREATED: 'analytics.segment.created',
  SEGMENT_UPDATED: 'analytics.segment.updated',
  REPORT_GENERATED: 'analytics.report.generated',
  DASHBOARD_UPDATED: 'analytics.dashboard.updated',
  ALERT_TRIGGERED: 'analytics.alert.triggered',
  TREND_DETECTED: 'analytics.trend.detected',
  ANOMALY_DETECTED: 'analytics.anomaly.detected',
} as const;

/**
 * Cache events
 */
export const CACHE_EVENTS = {
  HIT: 'cache.hit',
  MISS: 'cache.miss',
  SET: 'cache.set',
  GET: 'cache.get',
  DELETE: 'cache.delete',
  CLEAR: 'cache.clear',
  EXPIRED: 'cache.expired',
  OVERFLOW: 'cache.overflow',
  EVICTED: 'cache.evicted',
  STALE: 'cache.stale',
  REFRESHED: 'cache.refreshed',
  INVALIDATED: 'cache.invalidated',
} as const;

/**
 * Network events
 */
export const NETWORK_EVENTS = {
  CONNECTED: 'network.connected',
  DISCONNECTED: 'network.disconnected',
  RECONNECTING: 'network.reconnecting',
  CONNECTION_FAILED: 'network.connection.failed',
  REQUEST_STARTED: 'network.request.started',
  REQUEST_COMPLETED: 'network.request.completed',
  REQUEST_FAILED: 'network.request.failed',
  RESPONSE_RECEIVED: 'network.response.received',
  TIMEOUT: 'network.timeout',
  RATE_LIMITED: 'network.rate.limited',
  CIRCUIT_BREAKER_OPENED: 'network.circuit.breaker.opened',
  CIRCUIT_BREAKER_CLOSED: 'network.circuit.breaker.closed',
  RETRY_ATTEMPTED: 'network.retry.attempted',
} as const;

/**
 * Blockchain events
 */
export const BLOCKCHAIN_EVENTS = {
  WALLET_CONNECTED: 'blockchain.wallet.connected',
  WALLET_DISCONNECTED: 'blockchain.wallet.disconnected',
  WALLET_CHAIN_CHANGED: 'blockchain.wallet.chain.changed',
  WALLET_ACCOUNT_CHANGED: 'blockchain.wallet.account.changed',
  CONTRACT_INTERACTED: 'blockchain.contract.interacted',
  BLOCK_CONFIRMED: 'blockchain.block.confirmed',
  BLOCK_MINED: 'blockchain.block.mined',
  GAS_PRICE_UPDATED: 'blockchain.gas.price.updated',
  NETWORK_CHANGED: 'blockchain.network.changed',
  BLOCK_EXPLORER_OPENED: 'blockchain.block.explorer.opened',
} as const;

/**
 * Security events
 */
export const SECURITY_EVENTS = {
  LOGIN_ATTEMPT: 'security.login.attempt',
  LOGIN_SUCCESS: 'security.login.success',
  LOGIN_FAILED: 'security.login.failed',
  LOGOUT: 'security.logout',
  TWO_FACTOR_REQUIRED: 'security.two_factor.required',
  TWO_FACTOR_SUCCESS: 'security.two_factor.success',
  TWO_FACTOR_FAILED: 'security.two_factor.failed',
  PASSWORD_CHANGED: 'security.password.changed',
  PASSWORD_RESET_REQUESTED: 'security.password.reset.requested',
  PASSWORD_RESET_COMPLETED: 'security.password.reset.completed',
  ACCOUNT_LOCKED: 'security.account.locked',
  ACCOUNT_UNLOCKED: 'security.account.unlocked',
  ACCOUNT_SUSPENDED: 'security.account.suspended',
  ACCOUNT_UNSUSPENDED: 'security.account.unsuspended',
  SUSPICIOUS_ACTIVITY: 'security.suspicious.activity',
  FRAUD_DETECTED: 'security.fraud.detected',
  IP_BLOCKED: 'security.ip.blocked',
  IP_WHITELISTED: 'security.ip.whitelisted',
  CSRF_DETECTED: 'security.csrf.detected',
  XSS_DETECTED: 'security.xss.detected',
  SQL_INJECTION_DETECTED: 'security.sql.injection.detected',
  PHISHING_DETECTED: 'security.phishing.detected',
  MALWARE_DETECTED: 'security.malware.detected',
} as const;

/**
 * Compliance events
 */
export const COMPLIANCE_EVENTS = {
  KYC_STARTED: 'compliance.kyc.started',
  KYC_COMPLETED: 'compliance.kyc.completed',
  KYC_FAILED: 'compliance.kyc.failed',
  KYC_EXPIRED: 'compliance.kyc.expired',
  AML_CHECK_STARTED: 'compliance.aml.check.started',
  AML_CHECK_COMPLETED: 'compliance.aml.check.completed',
  AML_CHECK_FAILED: 'compliance.aml.check.failed',
  SANCTIONS_CHECK_STARTED: 'compliance.sanctions.check.started',
  SANCTIONS_CHECK_COMPLETED: 'compliance.sanctions.check.completed',
  SANCTIONS_CHECK_FAILED: 'compliance.sanctions.check.failed',
  GDPR_CONSENT_GIVEN: 'compliance.gdpr.consent.given',
  GDPR_CONSENT_REVOKED: 'compliance.gdpr.consent.revoked',
  GDPR_DATA_REQUESTED: 'compliance.gdpr.data.requested',
  GDPR_DATA_EXPORTED: 'compliance.gdpr.data.exported',
  GDPR_DATA_DELETED: 'compliance.gdpr.data.deleted',
  REGULATORY_VIOLATION: 'compliance.regulatory.violation',
  AUDIT_LOG_CREATED: 'compliance.audit.log.created',
} as const;

/**
 * System events
 */
export const SYSTEM_EVENTS = {
  STARTED: 'system.started',
  STOPPED: 'system.stopped',
  HEALTH_CHECK: 'system.health.check',
  HEALTH_DEGRADED: 'system.health.degraded',
  HEALTH_RECOVERED: 'system.health.recovered',
  CONFIGURATION_CHANGED: 'system.configuration.changed',
  ERROR_OCCURRED: 'system.error.occurred',
  WARNING_ISSUED: 'system.warning.issued',
  PERFORMANCE_DEGRADED: 'system.performance.degraded',
  PERFORMANCE_RECOVERED: 'system.performance.recovered',
  MEMORY_HIGH: 'system.memory.high',
  MEMORY_CRITICAL: 'system.memory.critical',
  CPU_HIGH: 'system.cpu.high',
  CPU_CRITICAL: 'system.cpu.critical',
  DISK_SPACE_LOW: 'system.disk.space.low',
  DISK_SPACE_CRITICAL: 'system.disk.space.critical',
  DATABASE_CONNECTION_FAILED: 'system.database.connection.failed',
  DATABASE_CONNECTION_RECOVERED: 'system.database.connection.recovered',
  BACKUP_STARTED: 'system.backup.started',
  BACKUP_COMPLETED: 'system.backup.completed',
  BACKUP_FAILED: 'system.backup.failed',
  UPGRADE_STARTED: 'system.upgrade.started',
  UPGRADE_COMPLETED: 'system.upgrade.completed',
  UPGRADE_FAILED: 'system.upgrade.failed',
  MAINTENANCE_MODE_ENABLED: 'system.maintenance.enabled',
  MAINTENANCE_MODE_DISABLED: 'system.maintenance.disabled',
} as const;

/**
 * Webhook events
 */
export const WEBHOOK_EVENTS = {
  CREATED: 'webhook.created',
  UPDATED: 'webhook.updated',
  DELETED: 'webhook.deleted',
  DELIVERED: 'webhook.delivered',
  FAILED: 'webhook.failed',
  RETRY_SCHEDULED: 'webhook.retry.scheduled',
  RETRY_EXHAUSTED: 'webhook.retry.exhausted',
  VERIFIED: 'webhook.verified',
  REVOKED: 'webhook.revoked',
} as const;

/**
 * Notification events
 */
export const NOTIFICATION_EVENTS = {
  CREATED: 'notification.created',
  SENT: 'notification.sent',
  DELIVERED: 'notification.delivered',
  READ: 'notification.read',
  FAILED: 'notification.failed',
  FAILED_TO_DELIVER: 'notification.failed_to_deliver',
  CLICKED: 'notification.clicked',
  UNSUBSCRIBED: 'notification.unsubscribed',
  RESUBSCRIBED: 'notification.resubscribed',
} as const;

/**
 * Subscription events
 */
export const SUBSCRIPTION_EVENTS = {
  CREATED: 'subscription.created',
  ACTIVATED: 'subscription.activated',
  RENEWED: 'subscription.renewed',
  CANCELLED: 'subscription.cancelled',
  EXPIRED: 'subscription.expired',
  UPGRADED: 'subscription.upgraded',
  DOWNGRADED: 'subscription.downgraded',
  PAUSED: 'subscription.paused',
  RESUMED: 'subscription.resumed',
  PAYMENT_FAILED: 'subscription.payment.failed',
  PAYMENT_RECOVERED: 'subscription.payment.recovered',
  TRIAL_STARTED: 'subscription.trial.started',
  TRIAL_ENDED: 'subscription.trial.ended',
  UPGRADE_AVAILABLE: 'subscription.upgrade.available',
  DOWNGRADE_REQUIRED: 'subscription.downgrade.required',
} as const;

/**
 * Refund events
 */
export const REFUND_EVENTS = {
  REQUESTED: 'refund.requested',
  APPROVED: 'refund.approved',
  REJECTED: 'refund.rejected',
  PROCESSING: 'refund.processing',
  COMPLETED: 'refund.completed',
  FAILED: 'refund.failed',
  PARTIALLY_COMPLETED: 'refund.partially.completed',
  CANCELLED: 'refund.cancelled',
} as const;

/**
 * Access log events
 */
export const ACCESS_LOG_EVENTS = {
  CREATED: 'access_log.created',
  VIEWED: 'access_log.viewed',
  BLOCKED: 'access_log.blocked',
  UNPAID_ACCESS: 'access_log.unpaid.access',
  CONVERTED_TO_PAYMENT: 'access_log.converted_to.payment',
} as const;

/**
 * Event priorities
 */
export enum EventPriority {
  CRITICAL = 'critical',
  HIGH = 'high',
  MEDIUM = 'medium',
  LOW = 'low',
  INFO = 'info',
}

/**
 * Event categories
 */
export enum EventCategory {
  SYSTEM = 'system',
  SECURITY = 'security',
  PAYMENT = 'payment',
  PRODUCT = 'product',
  USER = 'user',
  ANALYTICS = 'analytics',
  COMPLIANCE = 'compliance',
  PERFORMANCE = 'performance',
  ERROR = 'error',
  WARNING = 'warning',
  INFO = 'info',
}

/**
 * Event sources
 */
export enum EventSource {
  PROVIDER = 'provider',
  CLIENT = 'client',
  SYSTEM = 'system',
  ADMIN = 'admin',
  API = 'api',
  WEBHOOK = 'webhook',
  BLOCKCHAIN = 'blockchain',
  ANALYTICS = 'analytics',
  SECURITY = 'security',
  COMPLIANCE = 'compliance',
}

export type EventName = 
  | typeof PROVIDER_EVENTS[keyof typeof PROVIDER_EVENTS]
  | typeof PRODUCT_EVENTS[keyof typeof PRODUCT_EVENTS]
  | typeof PAYMENT_EVENTS[keyof typeof PAYMENT_EVENTS]
  | typeof TRANSACTION_EVENTS[keyof typeof TRANSACTION_EVENTS]
  | typeof CLIENT_EVENTS[keyof typeof CLIENT_EVENTS]
  | typeof ANALYTICS_EVENTS[keyof typeof ANALYTICS_EVENTS]
  | typeof CACHE_EVENTS[keyof typeof CACHE_EVENTS]
  | typeof NETWORK_EVENTS[keyof typeof NETWORK_EVENTS]
  | typeof BLOCKCHAIN_EVENTS[keyof typeof BLOCKCHAIN_EVENTS]
  | typeof SECURITY_EVENTS[keyof typeof SECURITY_EVENTS]
  | typeof COMPLIANCE_EVENTS[keyof typeof COMPLIANCE_EVENTS]
  | typeof SYSTEM_EVENTS[keyof typeof SYSTEM_EVENTS];

export type EventNamespace = typeof EVENT_NAMESPACES[keyof typeof EVENT_NAMESPACES];
