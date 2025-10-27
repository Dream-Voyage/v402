/**
 * V402 Providers SDK - API Constants
 * 
 * This file contains all API-related constants including endpoints,
 * headers, methods, and API configuration parameters used for
 * communication with the V402 facilitator backend.
 * 
 * @author V402 Team
 * @version 1.0.0
 * @since 2024-01-01
 */

/**
 * API Version constants
 */
export const API_VERSION = {
  V1: 'v1',
  V2: 'v2', // Future version
  CURRENT: 'v1',
  SUPPORTED: ['v1'],
  DEPRECATED: [],
} as const;

/**
 * Base API paths for different environments
 */
export const API_BASE_PATHS = {
  PRODUCTION: 'https://api.v402.network',
  STAGING: 'https://staging-api.v402.network',
  DEVELOPMENT: 'https://dev-api.v402.network',
  LOCAL: 'http://localhost:8000',
  TESTNET: 'https://testnet-api.v402.network',
} as const;

/**
 * API endpoint paths for providers
 */
export const PROVIDER_ENDPOINTS = {
  // Product Management
  PRODUCTS: '/api/v1/providers/products',
  PRODUCT_BY_ID: '/api/v1/providers/products/:id',
  PRODUCT_SEARCH: '/api/v1/providers/products/search',
  PRODUCT_BATCH: '/api/v1/providers/products/batch',
  PRODUCT_CATEGORIES: '/api/v1/providers/products/categories',
  PRODUCT_ANALYTICS: '/api/v1/providers/products/:id/analytics',
  PRODUCT_VERSIONS: '/api/v1/providers/products/:id/versions',
  
  // Access Logs
  ACCESS_LOGS: '/api/v1/providers/products/:id/access-logs',
  ACCESS_LOGS_SUMMARY: '/api/v1/providers/access-logs/summary',
  UNPAID_ACCESS: '/api/v1/providers/unpaid-access',
  RECENT_ACCESS: '/api/v1/providers/recent-access',
  
  // Provider Management
  PROFILE: '/api/v1/providers/profile',
  SETTINGS: '/api/v1/providers/settings',
  STATISTICS: '/api/v1/providers/statistics',
  REVENUE: '/api/v1/providers/revenue',
  PAYOUTS: '/api/v1/providers/payouts',
  
  // Webhooks
  WEBHOOKS: '/api/v1/providers/webhooks',
  WEBHOOK_BY_ID: '/api/v1/providers/webhooks/:id',
  WEBHOOK_TEST: '/api/v1/providers/webhooks/:id/test',
  WEBHOOK_LOGS: '/api/v1/providers/webhooks/:id/logs',
  
  // Authentication
  AUTH_LOGIN: '/api/v1/providers/auth/login',
  AUTH_LOGOUT: '/api/v1/providers/auth/logout',
  AUTH_REFRESH: '/api/v1/providers/auth/refresh',
  AUTH_VERIFY: '/api/v1/providers/auth/verify',
  
  // API Keys
  API_KEYS: '/api/v1/providers/api-keys',
  API_KEY_BY_ID: '/api/v1/providers/api-keys/:id',
  API_KEY_ROTATE: '/api/v1/providers/api-keys/:id/rotate',
} as const;

/**
 * API endpoint paths for clients
 */
export const CLIENT_ENDPOINTS = {
  // Payment Management
  PAYMENT_REQUEST: '/api/v1/clients/payment-request',
  PAYMENT_STATUS: '/api/v1/clients/payment-status',
  PAYMENT_HISTORY: '/api/v1/clients/payment-history/:id',
  PAYMENT_CANCEL: '/api/v1/clients/payment-cancel',
  PAYMENT_REFUND: '/api/v1/clients/payment-refund',
  
  // Content Access
  CONTENT_ACCESS: '/api/v1/clients/content-access',
  CONTENT_PREVIEW: '/api/v1/clients/content-preview',
  CONTENT_UNLOCK: '/api/v1/clients/content-unlock',
  
  // Client Management
  PROFILE: '/api/v1/clients/profile',
  BALANCE: '/api/v1/clients/balance',
  TRANSACTIONS: '/api/v1/clients/transactions',
} as const;

/**
 * HTTP Methods used by the API
 */
export const HTTP_METHODS = {
  GET: 'GET',
  POST: 'POST',
  PUT: 'PUT',
  PATCH: 'PATCH',
  DELETE: 'DELETE',
  OPTIONS: 'OPTIONS',
  HEAD: 'HEAD',
} as const;

/**
 * HTTP Headers constants
 */
export const HTTP_HEADERS = {
  // Standard headers
  CONTENT_TYPE: 'Content-Type',
  AUTHORIZATION: 'Authorization',
  USER_AGENT: 'User-Agent',
  ACCEPT: 'Accept',
  CACHE_CONTROL: 'Cache-Control',
  
  // Custom V402 headers
  X_V402_API_KEY: 'X-V402-API-Key',
  X_V402_VERSION: 'X-V402-Version',
  X_V402_TIMESTAMP: 'X-V402-Timestamp',
  X_V402_SIGNATURE: 'X-V402-Signature',
  X_V402_NONCE: 'X-V402-Nonce',
  X_V402_CHAIN_ID: 'X-V402-Chain-ID',
  X_V402_REQUEST_ID: 'X-V402-Request-ID',
  X_V402_CLIENT_TYPE: 'X-V402-Client-Type',
  X_V402_SDK_VERSION: 'X-V402-SDK-Version',
  
  // Rate limiting
  X_RATELIMIT_LIMIT: 'X-RateLimit-Limit',
  X_RATELIMIT_REMAINING: 'X-RateLimit-Remaining',
  X_RATELIMIT_RESET: 'X-RateLimit-Reset',
} as const;

/**
 * Content Types
 */
export const CONTENT_TYPES = {
  JSON: 'application/json',
  FORM_URL_ENCODED: 'application/x-www-form-urlencoded',
  FORM_DATA: 'multipart/form-data',
  TEXT_PLAIN: 'text/plain',
  XML: 'application/xml',
  BINARY: 'application/octet-stream',
} as const;

/**
 * HTTP Status Codes
 */
export const HTTP_STATUS = {
  // Success
  OK: 200,
  CREATED: 201,
  ACCEPTED: 202,
  NO_CONTENT: 204,
  
  // Redirection
  MOVED_PERMANENTLY: 301,
  FOUND: 302,
  NOT_MODIFIED: 304,
  
  // Client Errors
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  METHOD_NOT_ALLOWED: 405,
  NOT_ACCEPTABLE: 406,
  CONFLICT: 409,
  GONE: 410,
  UNPROCESSABLE_ENTITY: 422,
  TOO_MANY_REQUESTS: 429,
  
  // Server Errors
  INTERNAL_SERVER_ERROR: 500,
  NOT_IMPLEMENTED: 501,
  BAD_GATEWAY: 502,
  SERVICE_UNAVAILABLE: 503,
  GATEWAY_TIMEOUT: 504,
} as const;

/**
 * API Rate Limits
 */
export const RATE_LIMITS = {
  DEFAULT: {
    REQUESTS_PER_MINUTE: 100,
    REQUESTS_PER_HOUR: 1000,
    REQUESTS_PER_DAY: 10000,
  },
  PREMIUM: {
    REQUESTS_PER_MINUTE: 500,
    REQUESTS_PER_HOUR: 5000,
    REQUESTS_PER_DAY: 50000,
  },
  ENTERPRISE: {
    REQUESTS_PER_MINUTE: 1000,
    REQUESTS_PER_HOUR: 10000,
    REQUESTS_PER_DAY: 100000,
  },
} as const;

/**
 * Request/Response format constants
 */
export const REQUEST_FORMATS = {
  JSON: 'json',
  XML: 'xml',
  FORM: 'form',
  QUERY: 'query',
} as const;

/**
 * Pagination constants
 */
export const PAGINATION = {
  DEFAULT_PAGE_SIZE: 20,
  MAX_PAGE_SIZE: 100,
  MIN_PAGE_SIZE: 1,
  DEFAULT_PAGE: 1,
} as const;

/**
 * Query parameter names
 */
export const QUERY_PARAMS = {
  PAGE: 'page',
  LIMIT: 'limit',
  OFFSET: 'offset',
  SORT: 'sort',
  ORDER: 'order',
  FILTER: 'filter',
  SEARCH: 'search',
  INCLUDE: 'include',
  FIELDS: 'fields',
  FORMAT: 'format',
} as const;

/**
 * Sort orders
 */
export const SORT_ORDER = {
  ASC: 'asc',
  DESC: 'desc',
  ASCENDING: 'ascending',
  DESCENDING: 'descending',
} as const;

export type ApiVersion = typeof API_VERSION[keyof typeof API_VERSION];
export type ApiBasePath = typeof API_BASE_PATHS[keyof typeof API_BASE_PATHS];
export type HttpMethod = typeof HTTP_METHODS[keyof typeof HTTP_METHODS];
export type HttpHeader = typeof HTTP_HEADERS[keyof typeof HTTP_HEADERS];
export type ContentType = typeof CONTENT_TYPES[keyof typeof CONTENT_TYPES];
export type HttpStatus = typeof HTTP_STATUS[keyof typeof HTTP_STATUS];
export type RequestFormat = typeof REQUEST_FORMATS[keyof typeof REQUEST_FORMATS];
export type SortOrder = typeof SORT_ORDER[keyof typeof SORT_ORDER];
