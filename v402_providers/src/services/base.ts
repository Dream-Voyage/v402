/**
 * V402 Providers SDK - Base Service
 *
 * This file contains the base service class and interfaces that all
 * other services extend. It provides common functionality including
 * HTTP client configuration, error handling, logging, and caching.
 *
 * @author V402 Team
 * @version 1.0.0
 * @since 2024-01-01
 */

import {EventEmitter} from 'eventemitter3';
import {ApiError, ApiResponse, BaseFilters, ErrorType, QueryOptions,} from '../entities/base';
import {V402Config} from '../config/base';
import {Logger} from '../utils/logger';
import {CacheManager} from '../cache/manager';
import {RetryManager} from '../utils/retry';
import {RateLimiter} from '../utils/rate-limiter';
import {MetricsCollector} from '../monitoring/metrics';
import {CircuitBreaker} from '../utils/circuit-breaker';

/**
 * Base service interface
 */
export interface IBaseService {
  readonly name: string;
  readonly version: string;
  initialize(): Promise<void>;
  destroy(): Promise<void>;
  healthCheck(): Promise<ServiceHealth>;
}

/**
 * Service health information
 */
export interface ServiceHealth {
  readonly status: HealthStatus;
  readonly message?: string;
  readonly details?: Record<string, any>;
  readonly timestamp: Date;
  readonly checks: HealthCheck[];
}

/**
 * Health status enumeration
 */
export enum HealthStatus {
  HEALTHY = 'healthy',
  DEGRADED = 'degraded',
  UNHEALTHY = 'unhealthy',
  UNKNOWN = 'unknown',
}

/**
 * Individual health check
 */
export interface HealthCheck {
  readonly name: string;
  readonly status: HealthStatus;
  readonly message?: string;
  readonly duration: number;
  readonly metadata?: Record<string, any>;
}

/**
 * HTTP request configuration
 */
export interface RequestConfig {
  readonly url: string;
  readonly method: HttpMethod;
  readonly headers?: Record<string, string>;
  readonly params?: Record<string, any>;
  readonly data?: any;
  readonly timeout?: number;
  readonly retries?: number;
  readonly cache?: CacheConfig;
  readonly rateLimit?: RateLimitConfig;
  readonly circuitBreaker?: CircuitBreakerConfig;
}

/**
 * HTTP methods
 */
export enum HttpMethod {
  GET = 'GET',
  POST = 'POST',
  PUT = 'PUT',
  PATCH = 'PATCH',
  DELETE = 'DELETE',
  HEAD = 'HEAD',
  OPTIONS = 'OPTIONS',
}

/**
 * Cache configuration
 */
export interface CacheConfig {
  readonly enabled: boolean;
  readonly key?: string;
  readonly ttl?: number;
  readonly refresh?: boolean;
  readonly tags?: string[];
}

/**
 * Rate limit configuration
 */
export interface RateLimitConfig {
  readonly enabled: boolean;
  readonly requests: number;
  readonly window: number;
  readonly strategy: RateLimitStrategy;
}

/**
 * Rate limiting strategies
 */
export enum RateLimitStrategy {
  FIXED_WINDOW = 'fixed_window',
  SLIDING_WINDOW = 'sliding_window',
  TOKEN_BUCKET = 'token_bucket',
  LEAKY_BUCKET = 'leaky_bucket',
}

/**
 * Circuit breaker configuration
 */
export interface CircuitBreakerConfig {
  readonly enabled: boolean;
  readonly threshold: number;
  readonly timeout: number;
  readonly monitor: boolean;
}

/**
 * Service events
 */
export enum ServiceEvent {
  INITIALIZED = 'initialized',
  DESTROYED = 'destroyed',
  REQUEST_STARTED = 'request_started',
  REQUEST_COMPLETED = 'request_completed',
  REQUEST_FAILED = 'request_failed',
  CACHE_HIT = 'cache_hit',
  CACHE_MISS = 'cache_miss',
  RATE_LIMITED = 'rate_limited',
  CIRCUIT_OPENED = 'circuit_opened',
  CIRCUIT_CLOSED = 'circuit_closed',
  ERROR_OCCURRED = 'error_occurred',
  WARNING_ISSUED = 'warning_issued',
  METRICS_COLLECTED = 'metrics_collected',
}

/**
 * Service context for request handling
 */
export interface ServiceContext {
  readonly requestId: string;
  readonly userId?: string;
  readonly sessionId?: string;
  readonly apiKey?: string;
  readonly userAgent?: string;
  readonly ipAddress?: string;
  readonly timestamp: Date;
  readonly metadata?: Record<string, any>;
}

/**
 * Base service implementation
 */
export abstract class BaseService extends EventEmitter implements IBaseService {
  protected readonly config: V402Config;
  protected readonly logger: Logger;
  protected readonly cache: CacheManager;
  protected readonly retry: RetryManager;
  protected readonly rateLimiter: RateLimiter;
  protected readonly metrics: MetricsCollector;
  protected readonly circuitBreaker: CircuitBreaker;

  private _initialized: boolean = false;
  private _destroyed: boolean = false;

  constructor(
    config: V402Config,
    logger: Logger,
    cache: CacheManager,
    retry: RetryManager,
    rateLimiter: RateLimiter,
    metrics: MetricsCollector,
    circuitBreaker: CircuitBreaker
  ) {
    super();
    this.config = config;
    this.logger = logger;
    this.cache = cache;
    this.retry = retry;
    this.rateLimiter = rateLimiter;
    this.metrics = metrics;
    this.circuitBreaker = circuitBreaker;
  }

  /**
   * Service name (must be implemented by subclasses)
   */
  abstract get name(): string;

  /**
   * Service version
   */
  get version(): string {
    return '1.0.0';
  }

  /**
   * Check if service is initialized
   */
  get initialized(): boolean {
    return this._initialized;
  }

  /**
   * Check if service is destroyed
   */
  get destroyed(): boolean {
    return this._destroyed;
  }

  /**
   * Initialize the service
   */
  async initialize(): Promise<void> {
    if (this._initialized) {
      this.logger.warn(`Service ${this.name} is already initialized`);
      return;
    }

    try {
      this.logger.info(`Initializing service: ${this.name}`);

      // Perform service-specific initialization
      await this.onInitialize();

      this._initialized = true;
      this.emit(ServiceEvent.INITIALIZED, { service: this.name });

      this.logger.info(`Service ${this.name} initialized successfully`);
    } catch (error) {
      this.logger.error(`Failed to initialize service ${this.name}:`, error);
      throw new ServiceError(
        `SERVICE_INIT_FAILED`,
        `Failed to initialize service ${this.name}`,
        ErrorType.SERVER_ERROR,
        { service: this.name, error }
      );
    }
  }

  /**
   * Destroy the service
   */
  async destroy(): Promise<void> {
    if (this._destroyed) {
      this.logger.warn(`Service ${this.name} is already destroyed`);
      return;
    }

    try {
      this.logger.info(`Destroying service: ${this.name}`);

      // Perform service-specific cleanup
      await this.onDestroy();

      this._destroyed = true;
      this.emit(ServiceEvent.DESTROYED, { service: this.name });

      // Remove all listeners
      this.removeAllListeners();

      this.logger.info(`Service ${this.name} destroyed successfully`);
    } catch (error) {
      this.logger.error(`Failed to destroy service ${this.name}:`, error);
      throw new ServiceError(
        `SERVICE_DESTROY_FAILED`,
        `Failed to destroy service ${this.name}`,
        ErrorType.SERVER_ERROR,
        { service: this.name, error }
      );
    }
  }

  /**
   * Perform health check
   */
  async healthCheck(): Promise<ServiceHealth> {
    const startTime = Date.now();
    const checks: HealthCheck[] = [];

    try {
      // Perform service-specific health checks
      const serviceChecks = await this.performHealthChecks();
      checks.push(...serviceChecks);

      // Determine overall health status
      const hasUnhealthy = checks.some(check => check.status === HealthStatus.UNHEALTHY);
      const hasDegraded = checks.some(check => check.status === HealthStatus.DEGRADED);

      let status: HealthStatus;
      if (hasUnhealthy) {
        status = HealthStatus.UNHEALTHY;
      } else if (hasDegraded) {
        status = HealthStatus.DEGRADED;
      } else {
        status = HealthStatus.HEALTHY;
      }

      return {
        status,
        message: `Service ${this.name} health check completed`,
        details: {
          service: this.name,
          version: this.version,
          initialized: this.initialized,
          destroyed: this.destroyed,
        },
        timestamp: new Date(),
        checks,
      };
    } catch (error) {
      this.logger.error(`Health check failed for service ${this.name}:`, error);

      return {
        status: HealthStatus.UNHEALTHY,
        message: `Health check failed: ${error.message}`,
        details: {
          service: this.name,
          error: error.message,
        },
        timestamp: new Date(),
        checks,
      };
    }
  }

  /**
   * Make HTTP request with comprehensive error handling
   */
  protected async request<T = any>(
    config: RequestConfig,
    context?: ServiceContext
  ): Promise<ApiResponse<T>> {
    const requestId = context?.requestId || this.generateRequestId();
    const startTime = Date.now();

    try {
      // Emit request started event
      this.emit(ServiceEvent.REQUEST_STARTED, {
        service: this.name,
        requestId,
        url: config.url,
        method: config.method,
      });

      // Check rate limits
      if (config.rateLimit?.enabled) {
        await this.checkRateLimit(config.rateLimit, context);
      }

      // Check circuit breaker
      if (config.circuitBreaker?.enabled) {
        await this.checkCircuitBreaker(config.circuitBreaker);
      }

      // Check cache first
      let response: ApiResponse<T>;
      if (config.cache?.enabled && config.method === HttpMethod.GET) {
        const cached = await this.getCachedResponse<T>(config.cache, config.url);
        if (cached) {
          this.emit(ServiceEvent.CACHE_HIT, {
            service: this.name,
            requestId,
            cacheKey: config.cache.key || config.url,
          });
          return cached;
        }

        this.emit(ServiceEvent.CACHE_MISS, {
          service: this.name,
          requestId,
          cacheKey: config.cache.key || config.url,
        });
      }

      // Execute request with retry logic
      response = await this.executeRequest<T>(config, context);

      // Cache the response
      if (config.cache?.enabled && response.success) {
        await this.cacheResponse(config.cache, config.url, response);
      }

      // Record metrics
      const duration = Date.now() - startTime;
      this.metrics.recordRequest({
        service: this.name,
        method: config.method,
        status: response.success ? 'success' : 'error',
        duration,
      });

      // Emit request completed event
      this.emit(ServiceEvent.REQUEST_COMPLETED, {
        service: this.name,
        requestId,
        duration,
        success: response.success,
      });

      return response;
    } catch (error) {
      const duration = Date.now() - startTime;

      // Record error metrics
      this.metrics.recordError({
        service: this.name,
        method: config.method,
        error: error.constructor.name,
        duration,
      });

      // Emit request failed event
      this.emit(ServiceEvent.REQUEST_FAILED, {
        service: this.name,
        requestId,
        duration,
        error: error.message,
      });

      // Handle circuit breaker
      if (config.circuitBreaker?.enabled) {
        this.circuitBreaker.recordFailure();
      }

      throw error;
    }
  }

  /**
   * Build query string from filters and options
   */
  protected buildQueryParams(
    filters?: BaseFilters,
    options?: QueryOptions
  ): Record<string, any> {
    const params: Record<string, any> = {};

    if (filters) {
      if (filters.status) {
        params.status = filters.status.join(',');
      }
      if (filters.createdAfter) {
        params.createdAfter = filters.createdAfter.toISOString();
      }
      if (filters.createdBefore) {
        params.createdBefore = filters.createdBefore.toISOString();
      }
      if (filters.updatedAfter) {
        params.updatedAfter = filters.updatedAfter.toISOString();
      }
      if (filters.updatedBefore) {
        params.updatedBefore = filters.updatedBefore.toISOString();
      }
      if (filters.search) {
        params.search = filters.search;
      }
      if (filters.tags && filters.tags.length > 0) {
        params.tags = filters.tags.join(',');
      }
    }

    if (options) {
      if (options.include && options.include.length > 0) {
        params.include = options.include.join(',');
      }
      if (options.exclude && options.exclude.length > 0) {
        params.exclude = options.exclude.join(',');
      }
      if (options.sort && options.sort.length > 0) {
        params.sort = options.sort
          .map(s => `${s.field}:${s.direction}`)
          .join(',');
      }
      if (options.pagination) {
        if (options.pagination.page) {
          params.page = options.pagination.page;
        }
        if (options.pagination.limit) {
          params.limit = options.pagination.limit;
        }
        if (options.pagination.offset) {
          params.offset = options.pagination.offset;
        }
        if (options.pagination.cursor) {
          params.cursor = options.pagination.cursor;
        }
      }
    }

    return params;
  }

  /**
   * Handle API errors and convert to ServiceError
   */
  protected handleError(error: any, context?: string): ServiceError {
    if (error instanceof ServiceError) {
      return error;
    }

    if (error.response) {
      // HTTP error response
      const { status, data } = error.response;
      return new ServiceError(
        data?.error?.code || `HTTP_${status}`,
        data?.error?.message || error.message,
        this.getErrorTypeFromStatus(status),
        {
          status,
          data,
          context,
        }
      );
    }

    if (error.request) {
      // Network error
      return new ServiceError(
        'NETWORK_ERROR',
        'Network request failed',
        ErrorType.NETWORK_ERROR,
        { context }
      );
    }

    // Generic error
    return new ServiceError(
      'UNKNOWN_ERROR',
      error.message || 'An unknown error occurred',
      ErrorType.SERVER_ERROR,
      { context }
    );
  }

  /**
   * Generate unique request ID
   */
  protected generateRequestId(): string {
    return `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Service-specific initialization (override in subclasses)
   */
  protected async onInitialize(): Promise<void> {
    // Default implementation - no additional initialization needed
  }

  /**
   * Service-specific cleanup (override in subclasses)
   */
  protected async onDestroy(): Promise<void> {
    // Default implementation - no additional cleanup needed
  }

  /**
   * Service-specific health checks (override in subclasses)
   */
  protected async performHealthChecks(): Promise<HealthCheck[]> {
    return [
      {
        name: 'service_status',
        status: this.initialized ? HealthStatus.HEALTHY : HealthStatus.UNHEALTHY,
        message: this.initialized ? 'Service is initialized' : 'Service is not initialized',
        duration: 0,
      },
    ];
  }

  /**
   * Execute HTTP request
   */
  private async executeRequest<T>(
    config: RequestConfig,
    context?: ServiceContext
  ): Promise<ApiResponse<T>> {
    // This would be implemented with actual HTTP client (axios, fetch, etc.)
    // For now, returning a mock response
    throw new Error('HTTP client not implemented');
  }

  /**
   * Check rate limits
   */
  private async checkRateLimit(
    config: RateLimitConfig,
    context?: ServiceContext
  ): Promise<void> {
    const key = this.getRateLimitKey(context);
    const allowed = await this.rateLimiter.checkLimit(key, config);

    if (!allowed) {
      this.emit(ServiceEvent.RATE_LIMITED, {
        service: this.name,
        key,
        config,
      });

      throw new ServiceError(
        'RATE_LIMIT_EXCEEDED',
        'Rate limit exceeded',
        ErrorType.RATE_LIMIT,
        { config }
      );
    }
  }

  /**
   * Check circuit breaker
   */
  private async checkCircuitBreaker(
    config: CircuitBreakerConfig
  ): Promise<void> {
    if (this.circuitBreaker.isOpen()) {
      this.emit(ServiceEvent.CIRCUIT_OPENED, {
        service: this.name,
        config,
      });

      throw new ServiceError(
        'CIRCUIT_BREAKER_OPEN',
        'Circuit breaker is open',
        ErrorType.SERVER_ERROR,
        { config }
      );
    }
  }

  /**
   * Get cached response
   */
  private async getCachedResponse<T>(
    config: CacheConfig,
    url: string
  ): Promise<ApiResponse<T> | null> {
    const key = config.key || url;
    return await this.cache.get<ApiResponse<T>>(key);
  }

  /**
   * Cache response
   */
  private async cacheResponse<T>(
    config: CacheConfig,
    url: string,
    response: ApiResponse<T>
  ): Promise<void> {
    const key = config.key || url;
    const ttl = config.ttl || 300; // 5 minutes default
    await this.cache.set(key, response, ttl, config.tags);
  }

  /**
   * Get rate limit key
   */
  private getRateLimitKey(context?: ServiceContext): string {
    if (context?.apiKey) {
      return `api_key:${context.apiKey}`;
    }
    if (context?.userId) {
      return `user:${context.userId}`;
    }
    if (context?.ipAddress) {
      return `ip:${context.ipAddress}`;
    }
    return 'anonymous';
  }

  /**
   * Convert HTTP status to error type
   */
  private getErrorTypeFromStatus(status: number): ErrorType {
    if (status >= 400 && status < 500) {
      switch (status) {
        case 401:
          return ErrorType.AUTHENTICATION;
        case 403:
          return ErrorType.AUTHORIZATION;
        case 404:
          return ErrorType.NOT_FOUND;
        case 409:
          return ErrorType.CONFLICT;
        case 422:
          return ErrorType.VALIDATION;
        case 429:
          return ErrorType.RATE_LIMIT;
        default:
          return ErrorType.VALIDATION;
      }
    }

    if (status >= 500) {
      return ErrorType.SERVER_ERROR;
    }

    return ErrorType.NETWORK_ERROR;
  }
}

/**
 * Service-specific error class
 */
export class ServiceError extends Error implements ApiError {
  public readonly code: string;
  public readonly type: ErrorType;
  public readonly details?: Record<string, any>;
  public readonly field?: string;
  public readonly cause?: ApiError;

  constructor(
    code: string,
    message: string,
    type: ErrorType,
    details?: Record<string, any>,
    field?: string,
    cause?: ApiError
  ) {
    super(message);
    this.name = 'ServiceError';
    this.code = code;
    this.type = type;
    this.details = details;
    this.field = field;
    this.cause = cause;

    // Maintain proper stack trace
    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, ServiceError);
    }
  }
}

/**
 * Service registry interface
 */
export interface ServiceRegistry {
  register<T extends IBaseService>(name: string, service: T): void;
  get<T extends IBaseService>(name: string): T;
  has(name: string): boolean;
  remove(name: string): boolean;
  getAll(): Map<string, IBaseService>;
  clear(): void;
}

/**
 * Service factory interface
 */
export interface ServiceFactory {
  create<T extends IBaseService>(type: string, config: any): Promise<T>;
  createAll(configs: Record<string, any>): Promise<Map<string, IBaseService>>;
}
