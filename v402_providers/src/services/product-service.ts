/**
 * V402 Providers SDK - Product Service
 *
 * This service handles all product-related operations including CRUD operations,
 * product queries, analytics, and management. It provides a comprehensive
 * interface for managing content products in the V402 ecosystem.
 *
 * @author V402 Team
 * @version 1.0.0
 * @since 2024-01-01
 */

import {BaseService, ErrorType, ServiceContext, ServiceError,} from './base';
import {
  ApiResponse,
  CreateProductRequest,
  PaginatedResponse,
  Product,
  QueryOptions,
  UpdateProductRequest,
} from '../entities';
import {PROVIDER_ENDPOINTS} from '../constants/api';

/**
 * Product service for managing content products
 */
export class ProductService extends BaseService {
  /**
   * Service name
   */
  get name(): string {
    return 'ProductService';
  }

  /**
   * Create a new product
   */
  async createProduct(
    request: CreateProductRequest,
    context?: ServiceContext
  ): Promise<ApiResponse<Product>> {
    this.logger.debug('Creating product:', request);

    // Validate request
    this.validateCreateRequest(request);

    // Make API request
    const response = await this.request<Product>(
      {
        url: PROVIDER_ENDPOINTS.PRODUCTS,
        method: 'POST',
        data: request,
        timeout: 30000, // 30 seconds
        cache: { enabled: false },
      },
      context
    );

    if (!response.success) {
      this.logger.error('Failed to create product:', response.error);
      throw this.handleError(response.error, 'createProduct');
    }

    this.logger.info('Product created successfully:', response.data?.id);
    return response;
  }

  /**
   * Get product by ID
   */
  async getProduct(
    productId: string,
    options?: QueryOptions,
    context?: ServiceContext
  ): Promise<ApiResponse<Product>> {
    this.logger.debug('Getting product:', productId);

    // Validate product ID
    this.validateProductId(productId);

    // Build URL with query parameters
    const url = PROVIDER_ENDPOINTS.PRODUCT_BY_ID.replace(':id', productId);
    const params = this.buildQueryParams(undefined, options);

    // Make API request
    const response = await this.request<Product>(
      {
        url,
        method: 'GET',
        params,
        timeout: 10000,
        cache: {
          enabled: true,
          key: `product:${productId}`,
          ttl: 300, // 5 minutes
          tags: [`product:${productId}`],
        },
      },
      context
    );

    if (!response.success) {
      this.logger.error('Failed to get product:', response.error);
      throw this.handleError(response.error, 'getProduct');
    }

    this.logger.debug('Product retrieved successfully:', productId);
    return response;
  }

  /**
   * Update product
   */
  async updateProduct(
    productId: string,
    request: UpdateProductRequest,
    context?: ServiceContext
  ): Promise<ApiResponse<Product>> {
    this.logger.debug('Updating product:', productId, request);

    // Validate inputs
    this.validateProductId(productId);
    this.validateUpdateRequest(request);

    // Build URL
    const url = PROVIDER_ENDPOINTS.PRODUCT_BY_ID.replace(':id', productId);

    // Make API request
    const response = await this.request<Product>(
      {
        url,
        method: 'PUT',
        data: request,
        timeout: 30000,
        cache: { enabled: false }, // Don't cache updates
      },
      context
    );

    if (!response.success) {
      this.logger.error('Failed to update product:', response.error);
      throw this.handleError(response.error, 'updateProduct');
    }

    // Invalidate cache
    await this.cache.delete(`product:${productId}`);
    await this.cache.deleteTag(`product:${productId}`);

    this.logger.info('Product updated successfully:', productId);
    return response;
  }

  /**
   * Delete product
   */
  async deleteProduct(
    productId: string,
    context?: ServiceContext
  ): Promise<ApiResponse<void>> {
    this.logger.debug('Deleting product:', productId);

    // Validate product ID
    this.validateProductId(productId);

    // Build URL
    const url = PROVIDER_ENDPOINTS.PRODUCT_BY_ID.replace(':id', productId);

    // Make API request
    const response = await this.request<void>(
      {
        url,
        method: 'DELETE',
        timeout: 15000,
        cache: { enabled: false },
      },
      context
    );

    if (!response.success) {
      this.logger.error('Failed to delete product:', response.error);
      throw this.handleError(response.error, 'deleteProduct');
    }

    // Invalidate cache
    await this.cache.delete(`product:${productId}`);
    await this.cache.deleteTag(`product:${productId}`);

    this.logger.info('Product deleted successfully:', productId);
    return response;
  }

  /**
   * List products with pagination and filters
   */
  async listProducts(
    options?: QueryOptions,
    context?: ServiceContext
  ): Promise<ApiResponse<PaginatedResponse<Product>>> {
    this.logger.debug('Listing products with options:', options);

    // Build query parameters
    const params = this.buildQueryParams(options?.filters, options);

    // Make API request
    const response = await this.request<PaginatedResponse<Product>>(
      {
        url: PROVIDER_ENDPOINTS.PRODUCTS,
        method: 'GET',
        params,
        timeout: 15000,
        cache: {
          enabled: true,
          key: this.buildCacheKey('products', params),
          ttl: 60, // 1 minute
          tags: ['products'],
        },
      },
      context
    );

    if (!response.success) {
      this.logger.error('Failed to list products:', response.error);
      throw this.handleError(response.error, 'listProducts');
    }

    this.logger.debug('Products listed successfully. Count:', response.data?.data.length);
    return response;
  }

  /**
   * Search products
   */
  async searchProducts(
    query: string,
    options?: QueryOptions,
    context?: ServiceContext
  ): Promise<ApiResponse<PaginatedResponse<Product>>> {
    this.logger.debug('Searching products with query:', query);

    if (!query || query.trim().length === 0) {
      throw new ServiceError(
        'INVALID_SEARCH_QUERY',
        'Search query cannot be empty',
        ErrorType.VALIDATION
      );
    }

    // Build query parameters
    const params = {
      ...this.buildQueryParams(options?.filters, options),
      q: query,
    };

    // Make API request
    const response = await this.request<PaginatedResponse<Product>>(
      {
        url: PROVIDER_ENDPOINTS.PRODUCT_SEARCH,
        method: 'GET',
        params,
        timeout: 15000,
        cache: {
          enabled: true,
          key: this.buildCacheKey('products:search', { query, ...params }),
          ttl: 60,
          tags: ['products', 'search'],
        },
      },
      context
    );

    if (!response.success) {
      this.logger.error('Failed to search products:', response.error);
      throw this.handleError(response.error, 'searchProducts');
    }

    this.logger.debug('Products searched successfully. Count:', response.data?.data.length);
    return response;
  }

  /**
   * Get product analytics
   */
  async getProductAnalytics(
    productId: string,
    timeRange?: TimeRange,
    context?: ServiceContext
  ): Promise<ApiResponse<ProductAnalytics>> {
    this.logger.debug('Getting product analytics:', productId);

    // Validate product ID
    this.validateProductId(productId);

    // Build URL with optional time range
    const url = PROVIDER_ENDPOINTS.PRODUCT_ANALYTICS.replace(':id', productId);
    const params: Record<string, any> = {};
    if (timeRange) {
      params.from = timeRange.from.toISOString();
      params.to = timeRange.to.toISOString();
    }

    // Make API request
    const response = await this.request<ProductAnalytics>(
      {
        url,
        method: 'GET',
        params,
        timeout: 15000,
        cache: {
          enabled: true,
          key: `product:${productId}:analytics`,
          ttl: 300,
          tags: [`product:${productId}`, 'analytics'],
        },
      },
      context
    );

    if (!response.success) {
      this.logger.error('Failed to get product analytics:', response.error);
      throw this.handleError(response.error, 'getProductAnalytics');
    }

    this.logger.debug('Product analytics retrieved successfully');
    return response;
  }

  /**
   * Get product access logs
   */
  async getAccessLogs(
    productId: string,
    options?: AccessLogOptions,
    context?: ServiceContext
  ): Promise<ApiResponse<PaginatedResponse<AccessLog>>> {
    this.logger.debug('Getting access logs for product:', productId);

    // Validate product ID
    this.validateProductId(productId);

    // Build URL with query parameters
    const url = PROVIDER_ENDPOINTS.ACCESS_LOGS.replace(':id', productId);
    const params: Record<string, any> = {};

    if (options) {
      if (options.paid !== undefined) {
        params.paid = options.paid;
      }
      if (options.from) {
        params.from = options.from.toISOString();
      }
      if (options.to) {
        params.to = options.to.toISOString();
      }
    }

    // Make API request
    const response = await this.request<PaginatedResponse<AccessLog>>(
      {
        url,
        method: 'GET',
        params,
        timeout: 15000,
        cache: {
          enabled: true,
          key: `product:${productId}:access-logs`,
          ttl: 60,
          tags: [`product:${productId}`, 'access-logs'],
        },
      },
      context
    );

    if (!response.success) {
      this.logger.error('Failed to get access logs:', response.error);
      throw this.handleError(response.error, 'getAccessLogs');
    }

    this.logger.debug('Access logs retrieved successfully');
    return response;
  }

  /**
   * Get unpaid access records
   */
  async getUnpaidAccess(
    options?: QueryOptions,
    context?: ServiceContext
  ): Promise<ApiResponse<PaginatedResponse<UnpaidAccessRecord>>> {
    this.logger.debug('Getting unpaid access records');

    // Build query parameters
    const params = this.buildQueryParams(options?.filters, options);

    // Make API request
    const response = await this.request<PaginatedResponse<UnpaidAccessRecord>>(
      {
        url: PROVIDER_ENDPOINTS.UNPAID_ACCESS,
        method: 'GET',
        params,
        timeout: 15000,
        cache: {
          enabled: true,
          key: this.buildCacheKey('unpaid-access', params),
          ttl: 300,
          tags: ['unpaid-access'],
        },
      },
      context
    );

    if (!response.success) {
      this.logger.error('Failed to get unpaid access:', response.error);
      throw this.handleError(response.error, 'getUnpaidAccess');
    }

    this.logger.debug('Unpaid access records retrieved successfully');
    return response;
  }

  // Helper methods

  /**
   * Validate product ID
   */
  private validateProductId(productId: string): void {
    if (!productId || productId.trim().length === 0) {
      throw new ServiceError(
        'INVALID_PRODUCT_ID',
        'Product ID cannot be empty',
        ErrorType.VALIDATION
      );
    }
  }

  /**
   * Validate create product request
   */
  private validateCreateRequest(request: CreateProductRequest): void {
    if (!request.title || request.title.trim().length === 0) {
      throw new ServiceError(
        'INVALID_TITLE',
        'Product title cannot be empty',
        ErrorType.VALIDATION,
        { field: 'title' }
      );
    }

    if (!request.description || request.description.trim().length === 0) {
      throw new ServiceError(
        'INVALID_DESCRIPTION',
        'Product description cannot be empty',
        ErrorType.VALIDATION,
        { field: 'description' }
      );
    }

    if (!request.category) {
      throw new ServiceError(
        'INVALID_CATEGORY',
        'Product category is required',
        ErrorType.VALIDATION,
        { field: 'category' }
      );
    }

    if (!request.pricing || !request.pricing.basePrice) {
      throw new ServiceError(
        'INVALID_PRICING',
        'Product pricing is required',
        ErrorType.VALIDATION,
        { field: 'pricing' }
      );
    }
  }

  /**
   * Validate update product request
   */
  private validateUpdateRequest(request: UpdateProductRequest): void {
    if (request.title !== undefined && request.title.trim().length === 0) {
      throw new ServiceError(
        'INVALID_TITLE',
        'Product title cannot be empty',
        ErrorType.VALIDATION,
        { field: 'title' }
      );
    }
  }

  /**
   * Build cache key from parameters
   */
  private buildCacheKey(prefix: string, params: Record<string, any>): string {
    const parts = Object.entries(params)
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([key, value]) => `${key}:${value}`)
      .join('|');
    return `${prefix}:${parts}`;
  }
}

// Additional types

export interface TimeRange {
  readonly from: Date;
  readonly to: Date;
}

export interface ProductAnalytics {
  readonly productId: string;
  readonly views: number;
  readonly downloads: number;
  readonly purchases: number;
  readonly revenue: RevenueMetrics;
  readonly engagement: EngagementMetrics;
  readonly conversion: ConversionMetrics;
}

export interface RevenueMetrics {
  readonly total: string;
  readonly average: string;
  readonly currency: string;
  readonly trend: TrendData;
}

export interface TrendData {
  readonly direction: 'up' | 'down' | 'stable';
  readonly percentage: number;
  readonly period: string;
}

export interface EngagementMetrics {
  readonly totalTime: number;
  readonly avgSession: number;
  readonly bounceRate: number;
  readonly returnRate: number;
}

export interface ConversionMetrics {
  readonly viewToCart: number;
  readonly cartToPurchase: number;
  readonly abandonmentRate: number;
}

export interface AccessLog {
  readonly id: string;
  readonly productId: string;
  readonly userId?: string;
  readonly clientId?: string;
  readonly timestamp: Date;
  readonly paid: boolean;
  readonly paymentAmount?: string;
  readonly paymentMethod?: string;
  readonly accessType: AccessType;
  readonly ipAddress?: string;
  readonly userAgent?: string;
  readonly metadata?: Record<string, any>;
}

export enum AccessType {
  VIEW = 'view',
  DOWNLOAD = 'download',
  STREAM = 'stream',
  PREVIEW = 'preview',
  PREVIEW_TO_PURCHASE = 'preview_to_purchase',
}

export interface AccessLogOptions {
  readonly paid?: boolean;
  readonly from?: Date;
  readonly to?: Date;
  readonly limit?: number;
}

export interface UnpaidAccessRecord {
  readonly id: string;
  readonly productId: string;
  readonly productTitle: string;
  readonly userId?: string;
  readonly clientId?: string;
  readonly ipAddress?: string;
  readonly userAgent?: string;
  readonly timestamp: Date;
  readonly accessType: AccessType;
  readonly metadata?: Record<string, any>;
}
