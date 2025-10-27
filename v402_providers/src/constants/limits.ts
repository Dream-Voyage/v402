/**
 * V402 Providers SDK - Limits and Constraints
 * 
 * This file contains all limits, constraints, and boundaries
 * used throughout the V402 ecosystem including API limits,
 * data limits, performance constraints, and business rules.
 * 
 * @author V402 Team
 * @version 1.0.0
 * @since 2024-01-01
 */

/**
 * Rate limiting configurations
 */
export const RATE_LIMITS = {
  // API rate limits
  API: {
    FREE_TIER: {
      REQUESTS_PER_MINUTE: 60,
      REQUESTS_PER_HOUR: 1000,
      REQUESTS_PER_DAY: 10000,
      BURST_LIMIT: 10,
    },
    BASIC_TIER: {
      REQUESTS_PER_MINUTE: 300,
      REQUESTS_PER_HOUR: 5000,
      REQUESTS_PER_DAY: 50000,
      BURST_LIMIT: 50,
    },
    PROFESSIONAL_TIER: {
      REQUESTS_PER_MINUTE: 1000,
      REQUESTS_PER_HOUR: 20000,
      REQUESTS_PER_DAY: 200000,
      BURST_LIMIT: 200,
    },
    ENTERPRISE_TIER: {
      REQUESTS_PER_MINUTE: 5000,
      REQUESTS_PER_HOUR: 100000,
      REQUESTS_PER_DAY: 1000000,
      BURST_LIMIT: 1000,
    },
  },
  
  // Webhook rate limits
  WEBHOOK: {
    REQUESTS_PER_MINUTE: 10,
    REQUESTS_PER_HOUR: 100,
    RETRY_MAX_ATTEMPTS: 5,
    RETRY_DELAY_SECONDS: 5,
  },
  
  // Payment rate limits
  PAYMENT: {
    MIN_AMOUNT: '0.000001', // Minimum payment amount
    MAX_AMOUNT: '1000000000', // Maximum payment amount
    DAILY_LIMIT: '1000000', // Daily limit per user
    MONTHLY_LIMIT: '10000000', // Monthly limit per user
    MAX_PAYMENTS_PER_HOUR: 10,
    MAX_PAYMENTS_PER_DAY: 100,
  },
  
  // File upload limits
  FILE_UPLOAD: {
    MAX_FILE_SIZE: 100 * 1024 * 1024, // 100 MB
    MAX_FILES_PER_REQUEST: 10,
    MAX_TOTAL_SIZE: 1024 * 1024 * 1024, // 1 GB
    ALLOWED_TYPES: [
      'image/jpeg',
      'image/png',
      'image/gif',
      'image/webp',
      'image/svg+xml',
      'video/mp4',
      'video/webm',
      'audio/mpeg',
      'audio/wav',
      'application/pdf',
      'application/zip',
      'application/json',
      'text/markdown',
      'text/plain',
    ],
    MAX_DIMENSIONS: {
      width: 7680,
      height: 4320,
    },
  },
  
  // Cache limits
  CACHE: {
    MAX_ENTRY_SIZE: 10 * 1024 * 1024, // 10 MB
    MAX_CACHE_SIZE: 500 * 1024 * 1024, // 500 MB
    DEFAULT_TTL: 300, // 5 minutes
    MAX_TTL: 86400, // 24 hours
    CLEANUP_INTERVAL: 60000, // 1 minute
  },
  
  // Search limits
  SEARCH: {
    MAX_QUERY_LENGTH: 500,
    MAX_RESULTS: 1000,
    DEFAULT_RESULTS: 20,
    MIN_QUERY_LENGTH: 1,
    MAX_FILTERS: 20,
    MAX_SORT_FIELDS: 5,
  },
  
  // Batch operation limits
  BATCH: {
    MAX_ITEMS_PER_REQUEST: 100,
    MAX_CONCURRENT_OPERATIONS: 10,
    MAX_RETRY_ATTEMPTS: 3,
    MAX_TIMEOUT_MS: 30000, // 30 seconds
  },
  
  // Content limits
  CONTENT: {
    MAX_TITLE_LENGTH: 200,
    MAX_DESCRIPTION_LENGTH: 5000,
    MAX_SHORT_DESCRIPTION_LENGTH: 500,
    MAX_TAGS: 20,
    MAX_TAG_LENGTH: 50,
    MAX_CATEGORIES: 5,
    MAX_METADATA_KEYS: 100,
    MAX_METADATA_VALUE_LENGTH: 5000,
  },
  
  // Product limits
  PRODUCT: {
    MAX_PRODUCTS_PER_PROVIDER: 10000,
    MAX_VERSIONS_PER_PRODUCT: 100,
    MAX_PRICE_PRECISION: 18,
    MAX_DISCOUNT_PERCENTAGE: 100,
    MIN_PRICE: '0.000000000000000001',
    MAX_PRICE: '1000000000000000000000000',
  },
  
  // User limits
  USER: {
    MAX_PRODUCT_VIEWS_PER_DAY: 1000,
    MAX_DOWNLOADS_PER_DAY: 100,
    MAX_PURCHASES_PER_DAY: 50,
    MAX_CONCURRENT_SESSIONS: 5,
    MAX_FAVORITES: 1000,
    MAX_CART_ITEMS: 50,
  },
  
  // Blockchain limits
  BLOCKCHAIN: {
    MIN_CONFIRMATIONS: 1,
    MAX_CONFIRMATIONS: 100,
    DEFAULT_CONFIRMATIONS: 12,
    MAX_GAS_LIMIT: '100000000',
    MAX_GAS_PRICE: '100000000000000', // 1000 gwei
    MAX_TRANSACTION_SIZE: 1024 * 1024, // 1 MB
    MAX_TRANSACTION_DELAY: 300000, // 5 minutes
    POLLING_INTERVAL: 3000, // 3 seconds
    MAX_POLLING_ATTEMPTS: 100,
  },
  
  // Security limits
  SECURITY: {
    MAX_LOGIN_ATTEMPTS: 5,
    LOCKOUT_DURATION_MS: 15 * 60 * 1000, // 15 minutes
    MAX_PASSWORD_LENGTH: 128,
    MIN_PASSWORD_LENGTH: 8,
    SESSION_DURATION_MS: 24 * 60 * 60 * 1000, // 24 hours
    MAX_SESSION_IDLE_TIME_MS: 30 * 60 * 1000, // 30 minutes
    MAX_API_KEY_LENGTH: 256,
    MAX_IP_WHITELIST: 100,
  },
  
  // Analytics limits
  ANALYTICS: {
    MAX_DATE_RANGE_DAYS: 365,
    MAX_METRICS_PER_QUERY: 50,
    MAX_DIMENSIONS_PER_QUERY: 10,
    MAX_FILTERS_PER_QUERY: 20,
    MAX_REPORT_ROWS: 10000,
    CACHE_DURATION_MS: 3600000, // 1 hour
  },
  
  // Export limits
  EXPORT: {
    MAX_ROWS: 100000,
    MAX_FILE_SIZE: 500 * 1024 * 1024, // 500 MB
    MAX_FORMATS: ['csv', 'json', 'xlsx', 'pdf'],
    DEFAULT_FORMAT: 'csv',
    MAX_EXPORTS_PER_DAY: 10,
  },
  
  // Webhook limits
  WEBHOOK_LIMITS: {
    MAX_WEBHOOKS_PER_PROVIDER: 50,
    MAX_PAYLOAD_SIZE: 1024 * 1024, // 1 MB
    MAX_RETRY_ATTEMPTS: 5,
    MAX_RETRY_DELAY_MS: 300000, // 5 minutes
    TIMEOUT_MS: 30000, // 30 seconds
  },
  
  // Notification limits
  NOTIFICATION: {
    MAX_NOTIFICATIONS_PER_USER: 1000,
    MAX_NOTIFICATION_LENGTH: 1000,
    MAX_CHANNELS_PER_USER: 10,
    DEFAULT_RETENTION_DAYS: 90,
    MAX_RETENTION_DAYS: 365,
  },
  
  // Subscription limits
  SUBSCRIPTION: {
    MAX_SUBSCRIPTIONS_PER_USER: 50,
    MAX_SIMULTANEOUS_TRIALS: 3,
    MAX_CANCELLATION_WAITING_PERIOD_DAYS: 30,
    MIN_BILLING_CYCLE_DAYS: 1,
    MAX_BILLING_CYCLE_DAYS: 365,
  },
  
  // Commission limits
  COMMISSION: {
    MIN_PERCENTAGE: 0,
    MAX_PERCENTAGE: 100,
    DEFAULT_PERCENTAGE: 10,
    MIN_FLAT_AMOUNT: '0',
    MAX_FLAT_AMOUNT: '1000000',
  },
  
  // Refund limits
  REFUND: {
    MAX_REFUND_PERIOD_DAYS: 90,
    MIN_REFUND_PERIOD_HOURS: 0,
    MAX_REFUND_AMOUNT_PERCENTAGE: 100,
    MAX_AUTOMATIC_REFUND_AMOUNT: '100',
    MAX_REFUNDS_PER_TRANSACTION: 10,
  },
} as const;

/**
 * Pagination limits
 */
export const PAGINATION_LIMITS = {
  MIN_PAGE: 1,
  MAX_PAGE: 10000,
  DEFAULT_PAGE: 1,
  MIN_LIMIT: 1,
  MAX_LIMIT: 1000,
  DEFAULT_LIMIT: 20,
  MAX_CURSOR_LENGTH: 1000,
} as const;

/**
 * Retry limits
 */
export const RETRY_LIMITS = {
  MAX_ATTEMPTS: 5,
  MIN_DELAY_MS: 100,
  MAX_DELAY_MS: 30000,
  DEFAULT_DELAY_MS: 1000,
  MULTIPLIER: 2,
  JITTER: 0.1,
} as const;

/**
 * Timeout limits
 */
export const TIMEOUT_LIMITS = {
  CONNECTION: 30000, // 30 seconds
  RESPONSE: 60000, // 1 minute
  UPLOAD: 300000, // 5 minutes
  DOWNLOAD: 300000, // 5 minutes
  PROCESSING: 120000, // 2 minutes
  LONG_RUNNING: 600000, // 10 minutes
  WEBSOCKET: 30000, // 30 seconds
  HEALTH_CHECK: 5000, // 5 seconds
} as const;

/**
 * Concurrency limits
 */
export const CONCURRENCY_LIMITS = {
  MAX_CONCURRENT_REQUESTS: 10,
  MAX_CONCURRENT_DOWNLOADS: 5,
  MAX_CONCURRENT_UPLOADS: 5,
  MAX_CONCURRENT_PROCESSORS: 4,
  MAX_CONCURRENT_WEBWORKERS: 8,
  QUEUE_SIZE: 1000,
  QUEUE_FLUSH_INTERVAL: 1000, // 1 second
} as const;

/**
 * Memory limits
 */
export const MEMORY_LIMITS = {
  MAX_BUFFER_SIZE: 100 * 1024 * 1024, // 100 MB
  MAX_STACK_SIZE: 8388608, // 8 MB
  WARN_THRESHOLD: 0.8, // 80% usage
  CRITICAL_THRESHOLD: 0.9, // 90% usage
  CLEANUP_THRESHOLD: 0.7, // 70% usage
} as const;

/**
 * CPU limits
 */
export const CPU_LIMITS = {
  MAX_CPU_TIME_MS: 5000, // 5 seconds
  MAX_IDLE_TIME_MS: 60000, // 1 minute
  WARN_THRESHOLD: 0.8, // 80% usage
  CRITICAL_THRESHOLD: 0.9, // 90% usage
} as const;

/**
 * Storage limits
 */
export const STORAGE_LIMITS = {
  MAX_LOCAL_STORAGE_SIZE: 10 * 1024 * 1024, // 10 MB
  MAX_SESSION_STORAGE_SIZE: 5 * 1024 * 1024, // 5 MB
  MAX_INDEXED_DB_SIZE: 50 * 1024 * 1024, // 50 MB
  MAX_CACHE_STORAGE_SIZE: 100 * 1024 * 1024, // 100 MB
  CLEANUP_THRESHOLD: 0.8, // 80% usage
} as const;

/**
 * Validation limits
 */
export const VALIDATION_LIMITS = {
  MAX_STRING_LENGTH: 100000,
  MIN_STRING_LENGTH: 0,
  MAX_ARRAY_LENGTH: 10000,
  MAX_OBJECT_KEYS: 1000,
  MAX_NESTING_DEPTH: 10,
  MAX_REGEX_LENGTH: 1000,
  MAX_EMAIL_LENGTH: 254,
  MAX_URL_LENGTH: 2048,
} as const;

/**
 * Performance limits
 */
export const PERFORMANCE_LIMITS = {
  MAX_PROCESSING_TIME_MS: 5000,
  WARN_PROCESSING_TIME_MS: 1000,
  MAX_RENDER_TIME_MS: 16, // 60 FPS
  MAX_NETWORK_LATENCY_MS: 5000,
  IDEAL_NETWORK_LATENCY_MS: 100,
  MAX_BANDWIDTH_MBPS: 100,
  MIN_BANDWIDTH_MBPS: 1,
} as const;

/**
 * Feature flags limits
 */
export const FEATURE_FLAG_LIMITS = {
  MAX_FLAGS: 1000,
  MAX_ROLLOUT_PERCENTAGE: 100,
  MIN_ROLLOUT_PERCENTAGE: 0,
  DEFAULT_ROLLOUT_PERCENTAGE: 0,
  MAX_TARGETS: 100,
  MAX_VARIANTS: 10,
} as const;

/**
 * A/B testing limits
 */
export const AB_TESTING_LIMITS = {
  MAX_VARIANTS: 10,
  MIN_PARTICIPANTS: 100,
  MAX_PARTICIPANTS: 1000000,
  MIN_CONFIDENCE_LEVEL: 0.90,
  MIN_EFFECT_SIZE: 0.05,
  MAX_DURATION_DAYS: 90,
  MIN_DURATION_DAYS: 7,
} as const;

/**
 * Reporting limits
 */
export const REPORTING_LIMITS = {
  MAX_REPORT_ROWS: 100000,
  MAX_REPORT_COLUMNS: 100,
  MAX_REPORT_SIZE_BYTES: 100 * 1024 * 1024, // 100 MB
  MAX_SCHEDULED_REPORTS: 50,
  MAX_REPORT_GENERATION_TIME_MS: 300000, // 5 minutes
} as const;

export type RateLimitTier = 'FREE_TIER' | 'BASIC_TIER' | 'PROFESSIONAL_TIER' | 'ENTERPRISE_TIER';
export type LimitType = 
  | 'API' 
  | 'FILE_UPLOAD' 
  | 'CACHE' 
  | 'SEARCH' 
  | 'CONTENT' 
  | 'PRODUCT'
  | 'USER'
  | 'BLOCKCHAIN'
  | 'SECURITY'
  | 'ANALYTICS';
