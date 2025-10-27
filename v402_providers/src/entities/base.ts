/**
 * V402 Providers SDK - Base Entity Definitions
 *
 * This file contains base entity interfaces and types that are extended
 * by all other entities in the system. These provide common fields
 * and behaviors for all data models.
 *
 * @author V402 Team
 * @version 1.0.0
 * @since 2024-01-01
 */

import {z} from 'zod';

/**
 * Base timestamp fields for all entities
 */
export interface BaseTimestamps {
  readonly createdAt: Date;
  readonly updatedAt: Date;
  readonly deletedAt?: Date | null;
}

/**
 * Base entity interface with common fields
 */
export interface BaseEntity extends BaseTimestamps {
  readonly id: string;
  readonly version: number;
  readonly status: EntityStatus;
}

/**
 * Base entity with audit information
 */
export interface AuditableEntity extends BaseEntity {
  readonly createdBy?: string;
  readonly updatedBy?: string;
  readonly deletedBy?: string;
  readonly auditTrail: AuditEntry[];
}

/**
 * Entity status enumeration
 */
export enum EntityStatus {
  ACTIVE = 'active',
  INACTIVE = 'inactive',
  PENDING = 'pending',
  SUSPENDED = 'suspended',
  DELETED = 'deleted',
  ARCHIVED = 'archived',
}

/**
 * Audit entry for tracking changes
 */
export interface AuditEntry {
  readonly id: string;
  readonly entityId: string;
  readonly entityType: string;
  readonly action: AuditAction;
  readonly userId?: string;
  readonly timestamp: Date;
  readonly changes: Record<string, AuditChange>;
  readonly metadata?: Record<string, any>;
  readonly ipAddress?: string;
  readonly userAgent?: string;
}

/**
 * Audit action types
 */
export enum AuditAction {
  CREATE = 'create',
  UPDATE = 'update',
  DELETE = 'delete',
  RESTORE = 'restore',
  ARCHIVE = 'archive',
  ACTIVATE = 'activate',
  DEACTIVATE = 'deactivate',
  SUSPEND = 'suspend',
  UNSUSPEND = 'unsuspend',
}

/**
 * Individual field change in audit
 */
export interface AuditChange {
  readonly field: string;
  readonly oldValue: any;
  readonly newValue: any;
  readonly dataType: string;
}

/**
 * Base pagination metadata
 */
export interface PaginationMeta {
  readonly page: number;
  readonly limit: number;
  readonly totalItems: number;
  readonly totalPages: number;
  readonly hasNext: boolean;
  readonly hasPrevious: boolean;
}

/**
 * Paginated response wrapper
 */
export interface PaginatedResponse<T> {
  readonly data: T[];
  readonly meta: PaginationMeta;
  readonly links?: PaginationLinks;
}

/**
 * Pagination links for navigation
 */
export interface PaginationLinks {
  readonly first?: string;
  readonly previous?: string;
  readonly next?: string;
  readonly last?: string;
  readonly self: string;
}

/**
 * Base API response wrapper
 */
export interface ApiResponse<T = any> {
  readonly success: boolean;
  readonly data?: T;
  readonly error?: ApiError;
  readonly meta?: ResponseMeta;
  readonly timestamp: Date;
  readonly requestId: string;
}

/**
 * API Error structure
 */
export interface ApiError {
  readonly code: string;
  readonly message: string;
  readonly details?: Record<string, any>;
  readonly field?: string;
  readonly type: ErrorType;
  readonly stack?: string;
  readonly cause?: ApiError;
}

/**
 * Error types
 */
export enum ErrorType {
  VALIDATION = 'validation',
  AUTHENTICATION = 'authentication',
  AUTHORIZATION = 'authorization',
  NOT_FOUND = 'not_found',
  CONFLICT = 'conflict',
  RATE_LIMIT = 'rate_limit',
  SERVER_ERROR = 'server_error',
  NETWORK_ERROR = 'network_error',
  TIMEOUT = 'timeout',
  PAYMENT_ERROR = 'payment_error',
  BLOCKCHAIN_ERROR = 'blockchain_error',
}

/**
 * Response metadata
 */
export interface ResponseMeta {
  readonly version: string;
  readonly environment: string;
  readonly region?: string;
  readonly processingTime?: number;
  readonly cacheHit?: boolean;
  readonly warnings?: string[];
}

/**
 * Base filters for querying entities
 */
export interface BaseFilters {
  readonly status?: EntityStatus[];
  readonly createdAfter?: Date;
  readonly createdBefore?: Date;
  readonly updatedAfter?: Date;
  readonly updatedBefore?: Date;
  readonly search?: string;
  readonly tags?: string[];
}

/**
 * Sort configuration
 */
export interface SortConfig {
  readonly field: string;
  readonly direction: SortDirection;
}

/**
 * Sort direction enumeration
 */
export enum SortDirection {
  ASC = 'asc',
  DESC = 'desc',
}

/**
 * Query options for entity operations
 */
export interface QueryOptions {
  readonly include?: string[];
  readonly exclude?: string[];
  readonly sort?: SortConfig[];
  readonly filters?: BaseFilters;
  readonly pagination?: PaginationOptions;
}

/**
 * Pagination options
 */
export interface PaginationOptions {
  readonly page?: number;
  readonly limit?: number;
  readonly offset?: number;
  readonly cursor?: string;
}

/**
 * Money/Currency representation
 */
export interface Money {
  readonly amount: string; // Using string to avoid floating point issues
  readonly currency: string;
  readonly decimals: number;
}

/**
 * Geographic location
 */
export interface Location {
  readonly country?: string;
  readonly region?: string;
  readonly city?: string;
  readonly coordinates?: Coordinates;
  readonly timezone?: string;
}

/**
 * Geographic coordinates
 */
export interface Coordinates {
  readonly latitude: number;
  readonly longitude: number;
  readonly accuracy?: number;
}

/**
 * Contact information
 */
export interface ContactInfo {
  readonly email?: string;
  readonly phone?: string;
  readonly website?: string;
  readonly address?: Address;
  readonly socialLinks?: SocialLinks;
}

/**
 * Physical address
 */
export interface Address {
  readonly street?: string;
  readonly city?: string;
  readonly state?: string;
  readonly postalCode?: string;
  readonly country?: string;
}

/**
 * Social media links
 */
export interface SocialLinks {
  readonly twitter?: string;
  readonly linkedin?: string;
  readonly github?: string;
  readonly discord?: string;
  readonly telegram?: string;
  readonly website?: string;
}

/**
 * File attachment information
 */
export interface FileAttachment {
  readonly id: string;
  readonly filename: string;
  readonly originalName: string;
  readonly mimeType: string;
  readonly size: number;
  readonly url: string;
  readonly thumbnailUrl?: string;
  readonly metadata?: FileMetadata;
  readonly uploadedAt: Date;
  readonly uploadedBy?: string;
}

/**
 * File metadata
 */
export interface FileMetadata {
  readonly width?: number;
  readonly height?: number;
  readonly duration?: number;
  readonly bitrate?: number;
  readonly format?: string;
  readonly codec?: string;
  readonly checksum?: string;
}

// Zod schemas for runtime validation

export const BaseTimestampsSchema = z.object({
  createdAt: z.date(),
  updatedAt: z.date(),
  deletedAt: z.date().nullable().optional(),
});

export const BaseEntitySchema = BaseTimestampsSchema.extend({
  id: z.string().uuid(),
  version: z.number().int().min(1),
  status: z.nativeEnum(EntityStatus),
});

export const MoneySchema = z.object({
  amount: z.string().regex(/^\d+(\.\d+)?$/),
  currency: z.string().length(3),
  decimals: z.number().int().min(0).max(18),
});

export const CoordinatesSchema = z.object({
  latitude: z.number().min(-90).max(90),
  longitude: z.number().min(-180).max(180),
  accuracy: z.number().positive().optional(),
});

export const LocationSchema = z.object({
  country: z.string().optional(),
  region: z.string().optional(),
  city: z.string().optional(),
  coordinates: CoordinatesSchema.optional(),
  timezone: z.string().optional(),
});

export const PaginationOptionsSchema = z.object({
  page: z.number().int().min(1).optional(),
  limit: z.number().int().min(1).max(100).optional(),
  offset: z.number().int().min(0).optional(),
  cursor: z.string().optional(),
});

export const SortConfigSchema = z.object({
  field: z.string().min(1),
  direction: z.nativeEnum(SortDirection),
});

export type BaseTimestampsType = z.infer<typeof BaseTimestampsSchema>;
export type BaseEntityType = z.infer<typeof BaseEntitySchema>;
export type MoneyType = z.infer<typeof MoneySchema>;
export type CoordinatesType = z.infer<typeof CoordinatesSchema>;
export type LocationType = z.infer<typeof LocationSchema>;
export type PaginationOptionsType = z.infer<typeof PaginationOptionsSchema>;
export type SortConfigType = z.infer<typeof SortConfigSchema>;
