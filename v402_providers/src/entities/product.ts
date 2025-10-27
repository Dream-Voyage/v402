/**
 * V402 Providers SDK - Product Entity Definitions
 *
 * This file contains all product-related entity interfaces and types
 * for managing content products in the V402 ecosystem including
 * product creation, pricing, categories, and metadata.
 *
 * @author V402 Team
 * @version 1.0.0
 * @since 2024-01-01
 */

import {z} from 'zod';
import {AuditableEntity, BaseEntitySchema, FileAttachment, Money, MoneySchema,} from './base';

/**
 * Product entity representing a content product
 */
export interface Product extends AuditableEntity {
  readonly providerId: string;
  readonly title: string;
  readonly description: string;
  readonly shortDescription?: string;
  readonly slug: string;
  readonly category: ProductCategory;
  readonly subcategory?: string;
  readonly tags: string[];
  readonly pricing: ProductPricing;
  readonly content: ProductContent;
  readonly access: ProductAccess;
  readonly visibility: ProductVisibility;
  readonly metadata: ProductMetadata;
  readonly stats: ProductStats;
  readonly seo: ProductSEO;
  readonly localization: ProductLocalization;
}

/**
 * Product category enumeration
 */
export enum ProductCategory {
  ARTICLE = 'article',
  BLOG_POST = 'blog_post',
  NEWS = 'news',
  RESEARCH = 'research',
  TUTORIAL = 'tutorial',
  GUIDE = 'guide',
  DOCUMENTATION = 'documentation',
  EBOOK = 'ebook',
  WHITEPAPER = 'whitepaper',
  REPORT = 'report',
  ANALYSIS = 'analysis',
  INTERVIEW = 'interview',
  PODCAST = 'podcast',
  VIDEO = 'video',
  COURSE = 'course',
  WEBINAR = 'webinar',
  TEMPLATE = 'template',
  CODE = 'code',
  DATASET = 'dataset',
  API_ACCESS = 'api_access',
  SOFTWARE = 'software',
  PLUGIN = 'plugin',
  THEME = 'theme',
  IMAGE = 'image',
  GRAPHIC = 'graphic',
  DESIGN = 'design',
  MUSIC = 'music',
  AUDIO = 'audio',
  OTHER = 'other',
}

/**
 * Product pricing configuration
 */
export interface ProductPricing {
  readonly model: PricingModel;
  readonly basePrice: Money;
  readonly discountedPrice?: Money;
  readonly bulkPricing?: BulkPricing[];
  readonly subscriptionPlans?: SubscriptionPlan[];
  readonly dynamicPricing?: DynamicPricing;
  readonly freeTierLimits?: FreeTierLimits;
  readonly paymentMethods: PaymentMethod[];
  readonly refundPolicy: RefundPolicy;
}

/**
 * Pricing model types
 */
export enum PricingModel {
  ONE_TIME = 'one_time',
  SUBSCRIPTION = 'subscription',
  PAY_PER_USE = 'pay_per_use',
  PAY_PER_ACCESS = 'pay_per_access',
  TIERED = 'tiered',
  FREEMIUM = 'freemium',
  FREE = 'free',
  AUCTION = 'auction',
  NAME_YOUR_PRICE = 'name_your_price',
  DYNAMIC = 'dynamic',
}

/**
 * Bulk pricing tiers
 */
export interface BulkPricing {
  readonly minQuantity: number;
  readonly maxQuantity?: number;
  readonly price: Money;
  readonly discount?: number;
}

/**
 * Subscription plan configuration
 */
export interface SubscriptionPlan {
  readonly id: string;
  readonly name: string;
  readonly description: string;
  readonly price: Money;
  readonly billingCycle: BillingCycle;
  readonly features: PlanFeature[];
  readonly limits: PlanLimits;
  readonly trial?: TrialPeriod;
}

/**
 * Billing cycle enumeration
 */
export enum BillingCycle {
  DAILY = 'daily',
  WEEKLY = 'weekly',
  MONTHLY = 'monthly',
  QUARTERLY = 'quarterly',
  ANNUALLY = 'annually',
  CUSTOM = 'custom',
}

/**
 * Plan feature definition
 */
export interface PlanFeature {
  readonly id: string;
  readonly name: string;
  readonly description?: string;
  readonly included: boolean;
  readonly limit?: number;
}

/**
 * Plan usage limits
 */
export interface PlanLimits {
  readonly maxAccess?: number;
  readonly maxDownloads?: number;
  readonly maxApiCalls?: number;
  readonly maxStorage?: number;
  readonly maxBandwidth?: number;
  readonly concurrentUsers?: number;
}

/**
 * Trial period configuration
 */
export interface TrialPeriod {
  readonly duration: number;
  readonly unit: TimeUnit;
  readonly features: PlanFeature[];
  readonly autoConvert: boolean;
  readonly price?: Money;
}

/**
 * Time unit enumeration
 */
export enum TimeUnit {
  SECONDS = 'seconds',
  MINUTES = 'minutes',
  HOURS = 'hours',
  DAYS = 'days',
  WEEKS = 'weeks',
  MONTHS = 'months',
  YEARS = 'years',
}

/**
 * Dynamic pricing configuration
 */
export interface DynamicPricing {
  readonly enabled: boolean;
  readonly factors: PricingFactor[];
  readonly algorithm: PricingAlgorithm;
  readonly constraints: PricingConstraints;
}

/**
 * Pricing factors for dynamic pricing
 */
export interface PricingFactor {
  readonly type: PricingFactorType;
  readonly weight: number;
  readonly threshold?: number;
  readonly adjustment: number;
}

/**
 * Pricing factor types
 */
export enum PricingFactorType {
  DEMAND = 'demand',
  SUPPLY = 'supply',
  TIME_OF_DAY = 'time_of_day',
  DAY_OF_WEEK = 'day_of_week',
  SEASON = 'season',
  USER_LOCATION = 'user_location',
  USER_TIER = 'user_tier',
  POPULARITY = 'popularity',
  QUALITY_SCORE = 'quality_score',
  FRESHNESS = 'freshness',
  COMPETITION = 'competition',
}

/**
 * Pricing algorithm types
 */
export enum PricingAlgorithm {
  LINEAR = 'linear',
  EXPONENTIAL = 'exponential',
  LOGARITHMIC = 'logarithmic',
  SIGMOID = 'sigmoid',
  STEP = 'step',
  CUSTOM = 'custom',
}

/**
 * Pricing constraints
 */
export interface PricingConstraints {
  readonly minPrice: Money;
  readonly maxPrice: Money;
  readonly maxAdjustment: number;
  readonly updateFrequency: number;
}

/**
 * Free tier limitations
 */
export interface FreeTierLimits {
  readonly maxAccess: number;
  readonly timeWindow: number;
  readonly restrictions: AccessRestriction[];
}

/**
 * Access restrictions
 */
export interface AccessRestriction {
  readonly type: RestrictionType;
  readonly value: any;
  readonly message: string;
}

/**
 * Restriction types
 */
export enum RestrictionType {
  GEOGRAPHIC = 'geographic',
  TEMPORAL = 'temporal',
  USER_TYPE = 'user_type',
  DEVICE_TYPE = 'device_type',
  REFERRER = 'referrer',
  IP_RANGE = 'ip_range',
  USER_AGENT = 'user_agent',
  CUSTOM = 'custom',
}

/**
 * Payment methods
 */
export enum PaymentMethod {
  ETHEREUM = 'ethereum',
  BITCOIN = 'bitcoin',
  POLYGON = 'polygon',
  BSC = 'bsc',
  ARBITRUM = 'arbitrum',
  OPTIMISM = 'optimism',
  BASE = 'base',
  SOLANA = 'solana',
  CREDIT_CARD = 'credit_card',
  PAYPAL = 'paypal',
  BANK_TRANSFER = 'bank_transfer',
  APPLE_PAY = 'apple_pay',
  GOOGLE_PAY = 'google_pay',
  STRIPE = 'stripe',
  LIGHTNING = 'lightning',
}

/**
 * Refund policy
 */
export interface RefundPolicy {
  readonly enabled: boolean;
  readonly period: number;
  readonly unit: TimeUnit;
  readonly conditions: RefundCondition[];
  readonly percentage: number;
  readonly processing: RefundProcessing;
}

/**
 * Refund conditions
 */
export interface RefundCondition {
  readonly type: RefundConditionType;
  readonly description: string;
  readonly automated: boolean;
}

/**
 * Refund condition types
 */
export enum RefundConditionType {
  QUALITY_ISSUE = 'quality_issue',
  TECHNICAL_ISSUE = 'technical_issue',
  MISDESCRIPTION = 'misdescription',
  DUPLICATE_PURCHASE = 'duplicate_purchase',
  ACCIDENTAL_PURCHASE = 'accidental_purchase',
  UNSATISFACTORY = 'unsatisfactory',
  FRAUD = 'fraud',
  CHARGEBACK = 'chargeback',
  CUSTOM = 'custom',
}

/**
 * Refund processing configuration
 */
export interface RefundProcessing {
  readonly automatic: boolean;
  readonly approvalRequired: boolean;
  readonly processingTime: number;
  readonly method: RefundMethod;
}

/**
 * Refund methods
 */
export enum RefundMethod {
  ORIGINAL_PAYMENT = 'original_payment',
  STORE_CREDIT = 'store_credit',
  BANK_TRANSFER = 'bank_transfer',
  CHECK = 'check',
  CRYPTO = 'crypto',
}

/**
 * Product content configuration
 */
export interface ProductContent {
  readonly type: ContentType;
  readonly format: ContentFormat;
  readonly size: number;
  readonly duration?: number;
  readonly quality: ContentQuality;
  readonly files: ProductFile[];
  readonly preview: ContentPreview;
  readonly protection: ContentProtection;
  readonly delivery: ContentDelivery;
  readonly versioning: ContentVersioning;
}

/**
 * Content types
 */
export enum ContentType {
  TEXT = 'text',
  MARKDOWN = 'markdown',
  HTML = 'html',
  PDF = 'pdf',
  DOC = 'doc',
  IMAGE = 'image',
  VIDEO = 'video',
  AUDIO = 'audio',
  ARCHIVE = 'archive',
  EXECUTABLE = 'executable',
  DATA = 'data',
  CODE = 'code',
  API = 'api',
  STREAM = 'stream',
  INTERACTIVE = 'interactive',
}

/**
 * Content formats
 */
export enum ContentFormat {
  // Text formats
  PLAIN_TEXT = 'plain_text',
  MARKDOWN = 'markdown',
  HTML = 'html',
  RTF = 'rtf',

  // Document formats
  PDF = 'pdf',
  DOC = 'doc',
  DOCX = 'docx',
  ODT = 'odt',

  // Image formats
  JPEG = 'jpeg',
  PNG = 'png',
  GIF = 'gif',
  SVG = 'svg',
  WEBP = 'webp',

  // Video formats
  MP4 = 'mp4',
  WEBM = 'webm',
  AVI = 'avi',
  MOV = 'mov',

  // Audio formats
  MP3 = 'mp3',
  WAV = 'wav',
  FLAC = 'flac',
  OGG = 'ogg',

  // Archive formats
  ZIP = 'zip',
  RAR = 'rar',
  TAR = 'tar',
  GZIP = 'gzip',

  // Data formats
  JSON = 'json',
  XML = 'xml',
  CSV = 'csv',
  YAML = 'yaml',

  // Code formats
  JAVASCRIPT = 'javascript',
  PYTHON = 'python',
  JAVA = 'java',
  CPP = 'cpp',
  RUST = 'rust',
  GO = 'go',
}

/**
 * Content quality levels
 */
export enum ContentQuality {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  PREMIUM = 'premium',
  ULTRA = 'ultra',
  LOSSLESS = 'lossless',
}

/**
 * Product file information
 */
export interface ProductFile extends FileAttachment {
  readonly role: FileRole;
  readonly priority: number;
  readonly protected: boolean;
  readonly downloadLimit?: number;
  readonly expiresAt?: Date;
  readonly dependencies?: string[];
}

/**
 * File roles in product
 */
export enum FileRole {
  PRIMARY = 'primary',
  SECONDARY = 'secondary',
  PREVIEW = 'preview',
  THUMBNAIL = 'thumbnail',
  COVER = 'cover',
  SAMPLE = 'sample',
  SUPPLEMENT = 'supplement',
  DOCUMENTATION = 'documentation',
  LICENSE = 'license',
  CHANGELOG = 'changelog',
}

/**
 * Content preview configuration
 */
export interface ContentPreview {
  readonly enabled: boolean;
  readonly type: PreviewType;
  readonly duration?: number;
  readonly size?: number;
  readonly quality?: ContentQuality;
  readonly watermark?: WatermarkConfig;
  readonly restrictions?: AccessRestriction[];
}

/**
 * Preview types
 */
export enum PreviewType {
  NONE = 'none',
  THUMBNAIL = 'thumbnail',
  EXCERPT = 'excerpt',
  FIRST_PAGE = 'first_page',
  TIME_LIMITED = 'time_limited',
  QUALITY_LIMITED = 'quality_limited',
  WATERMARKED = 'watermarked',
  BLURRED = 'blurred',
  PIXELATED = 'pixelated',
}

/**
 * Watermark configuration
 */
export interface WatermarkConfig {
  readonly type: WatermarkType;
  readonly content: string;
  readonly position: WatermarkPosition;
  readonly opacity: number;
  readonly size: number;
  readonly color?: string;
  readonly font?: string;
}

/**
 * Watermark types
 */
export enum WatermarkType {
  TEXT = 'text',
  IMAGE = 'image',
  LOGO = 'logo',
  QR_CODE = 'qr_code',
  INVISIBLE = 'invisible',
}

/**
 * Watermark positions
 */
export enum WatermarkPosition {
  TOP_LEFT = 'top_left',
  TOP_RIGHT = 'top_right',
  TOP_CENTER = 'top_center',
  CENTER_LEFT = 'center_left',
  CENTER = 'center',
  CENTER_RIGHT = 'center_right',
  BOTTOM_LEFT = 'bottom_left',
  BOTTOM_RIGHT = 'bottom_right',
  BOTTOM_CENTER = 'bottom_center',
  TILED = 'tiled',
}

/**
 * Content protection measures
 */
export interface ContentProtection {
  readonly encryption: EncryptionConfig;
  readonly drm: DRMConfig;
  readonly antiPiracy: AntiPiracyConfig;
  readonly accessControl: AccessControlConfig;
}

/**
 * Encryption configuration
 */
export interface EncryptionConfig {
  readonly enabled: boolean;
  readonly algorithm: EncryptionAlgorithm;
  readonly keyRotation: boolean;
  readonly rotationInterval: number;
}

/**
 * Encryption algorithms
 */
export enum EncryptionAlgorithm {
  AES256 = 'aes256',
  AES192 = 'aes192',
  AES128 = 'aes128',
  CHACHA20 = 'chacha20',
  BLOWFISH = 'blowfish',
}

/**
 * DRM configuration
 */
export interface DRMConfig {
  readonly enabled: boolean;
  readonly provider: DRMProvider;
  readonly rules: DRMRule[];
}

/**
 * DRM providers
 */
export enum DRMProvider {
  WIDEVINE = 'widevine',
  FAIRPLAY = 'fairplay',
  PLAYREADY = 'playready',
  CLEARKEY = 'clearkey',
  CUSTOM = 'custom',
}

/**
 * DRM rules
 */
export interface DRMRule {
  readonly type: DRMRuleType;
  readonly value: any;
  readonly expires?: Date;
}

/**
 * DRM rule types
 */
export enum DRMRuleType {
  NO_COPY = 'no_copy',
  NO_SAVE = 'no_save',
  NO_PRINT = 'no_print',
  NO_SCREENSHOT = 'no_screenshot',
  TIME_LIMITED = 'time_limited',
  DEVICE_LIMITED = 'device_limited',
  LOCATION_LIMITED = 'location_limited',
}

/**
 * Anti-piracy configuration
 */
export interface AntiPiracyConfig {
  readonly monitoring: boolean;
  readonly takedownRequests: boolean;
  readonly fingerprinting: boolean;
  readonly blockchain: boolean;
}

/**
 * Access control configuration
 */
export interface AccessControlConfig {
  readonly authentication: boolean;
  readonly authorization: boolean;
  readonly sessionManagement: boolean;
  readonly ipRestrictions: string[];
  readonly deviceRestrictions: DeviceRestriction[];
}

/**
 * Device restrictions
 */
export interface DeviceRestriction {
  readonly type: DeviceType;
  readonly allowed: boolean;
  readonly maxConcurrent?: number;
}

/**
 * Device types
 */
export enum DeviceType {
  DESKTOP = 'desktop',
  MOBILE = 'mobile',
  TABLET = 'tablet',
  TV = 'tv',
  GAME_CONSOLE = 'game_console',
  VR_HEADSET = 'vr_headset',
  SMART_SPEAKER = 'smart_speaker',
  IOT_DEVICE = 'iot_device',
}

/**
 * Content delivery configuration
 */
export interface ContentDelivery {
  readonly method: DeliveryMethod;
  readonly cdn: CDNConfig;
  readonly streaming: StreamingConfig;
  readonly download: DownloadConfig;
  readonly caching: CachingConfig;
}

/**
 * Delivery methods
 */
export enum DeliveryMethod {
  DIRECT_DOWNLOAD = 'direct_download',
  STREAMING = 'streaming',
  PROGRESSIVE_DOWNLOAD = 'progressive_download',
  ADAPTIVE_STREAMING = 'adaptive_streaming',
  P2P = 'p2p',
  HYBRID = 'hybrid',
}

/**
 * CDN configuration
 */
export interface CDNConfig {
  readonly enabled: boolean;
  readonly provider: CDNProvider;
  readonly regions: string[];
  readonly cacheTTL: number;
  readonly compression: boolean;
}

/**
 * CDN providers
 */
export enum CDNProvider {
  CLOUDFLARE = 'cloudflare',
  FASTLY = 'fastly',
  AMAZON_CLOUDFRONT = 'amazon_cloudfront',
  GOOGLE_CLOUD_CDN = 'google_cloud_cdn',
  AZURE_CDN = 'azure_cdn',
  BUNNY_CDN = 'bunny_cdn',
  KEYCDN = 'keycdn',
}

/**
 * Streaming configuration
 */
export interface StreamingConfig {
  readonly enabled: boolean;
  readonly protocol: StreamingProtocol;
  readonly quality: StreamingQuality[];
  readonly bitrates: number[];
  readonly adaptive: boolean;
}

/**
 * Streaming protocols
 */
export enum StreamingProtocol {
  HLS = 'hls',
  DASH = 'dash',
  RTMP = 'rtmp',
  WEBRTC = 'webrtc',
  PROGRESSIVE = 'progressive',
}

/**
 * Streaming quality options
 */
export enum StreamingQuality {
  AUDIO_ONLY = 'audio_only',
  LOW = '240p',
  MEDIUM = '480p',
  HIGH = '720p',
  FULL_HD = '1080p',
  QUAD_HD = '1440p',
  ULTRA_HD = '2160p',
  ULTRA_HD_8K = '4320p',
}

/**
 * Download configuration
 */
export interface DownloadConfig {
  readonly enabled: boolean;
  readonly resumable: boolean;
  readonly chunkSize: number;
  readonly maxRetries: number;
  readonly speedLimit?: number;
  readonly concurrentConnections: number;
}

/**
 * Caching configuration
 */
export interface CachingConfig {
  readonly browser: CacheSettings;
  readonly proxy: CacheSettings;
  readonly cdn: CacheSettings;
}

/**
 * Cache settings
 */
export interface CacheSettings {
  readonly enabled: boolean;
  readonly ttl: number;
  readonly maxAge: number;
  readonly revalidate: boolean;
  readonly etag: boolean;
}

/**
 * Content versioning
 */
export interface ContentVersioning {
  readonly enabled: boolean;
  readonly strategy: VersioningStrategy;
  readonly maxVersions: number;
  readonly autoCleanup: boolean;
  readonly retentionPeriod: number;
}

/**
 * Versioning strategies
 */
export enum VersioningStrategy {
  SEMANTIC = 'semantic',
  TIMESTAMP = 'timestamp',
  SEQUENTIAL = 'sequential',
  HASH = 'hash',
  CUSTOM = 'custom',
}

/**
 * Product access configuration
 */
export interface ProductAccess {
  readonly type: AccessType;
  readonly duration?: number;
  readonly unit?: TimeUnit;
  readonly maxUses?: number;
  readonly concurrent?: boolean;
  readonly transferable?: boolean;
  readonly resellable?: boolean;
  readonly geographic?: GeographicAccess;
  readonly temporal?: TemporalAccess;
}

/**
 * Access types
 */
export enum AccessType {
  PERMANENT = 'permanent',
  TEMPORARY = 'temporary',
  SUBSCRIPTION = 'subscription',
  PAY_PER_VIEW = 'pay_per_view',
  PAY_PER_USE = 'pay_per_use',
  RENTAL = 'rental',
  LEASE = 'lease',
  LICENSE = 'license',
}

/**
 * Geographic access restrictions
 */
export interface GeographicAccess {
  readonly type: GeographicRestriction;
  readonly countries?: string[];
  readonly regions?: string[];
  readonly ipRanges?: string[];
}

/**
 * Geographic restriction types
 */
export enum GeographicRestriction {
  WORLDWIDE = 'worldwide',
  WHITELIST = 'whitelist',
  BLACKLIST = 'blacklist',
  REGIONAL = 'regional',
}

/**
 * Temporal access restrictions
 */
export interface TemporalAccess {
  readonly availableFrom?: Date;
  readonly availableUntil?: Date;
  readonly timezone?: string;
  readonly schedule?: AccessSchedule[];
}

/**
 * Access schedule
 */
export interface AccessSchedule {
  readonly dayOfWeek: DayOfWeek;
  readonly startTime: string;
  readonly endTime: string;
  readonly timezone?: string;
}

/**
 * Days of week
 */
export enum DayOfWeek {
  MONDAY = 'monday',
  TUESDAY = 'tuesday',
  WEDNESDAY = 'wednesday',
  THURSDAY = 'thursday',
  FRIDAY = 'friday',
  SATURDAY = 'saturday',
  SUNDAY = 'sunday',
}

/**
 * Product visibility settings
 */
export interface ProductVisibility {
  readonly status: VisibilityStatus;
  readonly searchable: boolean;
  readonly featured: boolean;
  readonly category: boolean;
  readonly recommendations: boolean;
  readonly public: boolean;
  readonly unlisted: boolean;
}

/**
 * Visibility status
 */
export enum VisibilityStatus {
  PUBLIC = 'public',
  PRIVATE = 'private',
  UNLISTED = 'unlisted',
  DRAFT = 'draft',
  SCHEDULED = 'scheduled',
  ARCHIVED = 'archived',
}

/**
 * Product metadata
 */
export interface ProductMetadata {
  readonly isbn?: string;
  readonly doi?: string;
  readonly license: LicenseInfo;
  readonly copyright: CopyrightInfo;
  readonly language: string;
  readonly alternativeLanguages?: string[];
  readonly difficulty: DifficultyLevel;
  readonly ageRating: AgeRating;
  readonly contentWarnings: ContentWarning[];
  readonly keywords: string[];
  readonly customFields: Record<string, any>;
}

/**
 * License information
 */
export interface LicenseInfo {
  readonly type: LicenseType;
  readonly name: string;
  readonly url?: string;
  readonly text?: string;
  readonly commercial: boolean;
  readonly derivative: boolean;
  readonly attribution: boolean;
}

/**
 * License types
 */
export enum LicenseType {
  CC0 = 'cc0',
  CC_BY = 'cc_by',
  CC_BY_SA = 'cc_by_sa',
  CC_BY_NC = 'cc_by_nc',
  CC_BY_NC_SA = 'cc_by_nc_sa',
  CC_BY_ND = 'cc_by_nd',
  CC_BY_NC_ND = 'cc_by_nc_nd',
  MIT = 'mit',
  GPL_V2 = 'gpl_v2',
  GPL_V3 = 'gpl_v3',
  APACHE = 'apache',
  BSD = 'bsd',
  PROPRIETARY = 'proprietary',
  CUSTOM = 'custom',
}

/**
 * Copyright information
 */
export interface CopyrightInfo {
  readonly owner: string;
  readonly year: number;
  readonly notice: string;
  readonly jurisdiction: string;
}

/**
 * Difficulty levels
 */
export enum DifficultyLevel {
  BEGINNER = 'beginner',
  INTERMEDIATE = 'intermediate',
  ADVANCED = 'advanced',
  EXPERT = 'expert',
  PROFESSIONAL = 'professional',
}

/**
 * Age rating systems
 */
export enum AgeRating {
  G = 'g',           // General Audiences
  PG = 'pg',         // Parental Guidance
  PG_13 = 'pg_13',   // Parents Strongly Cautioned
  R = 'r',           // Restricted
  NC_17 = 'nc_17',   // No One 17 and Under
  E = 'e',           // Everyone
  E10 = 'e10',       // Everyone 10+
  T = 't',           // Teen
  M = 'm',           // Mature 17+
  AO = 'ao',         // Adults Only 18+
}

/**
 * Content warnings
 */
export enum ContentWarning {
  VIOLENCE = 'violence',
  STRONG_LANGUAGE = 'strong_language',
  SEXUAL_CONTENT = 'sexual_content',
  NUDITY = 'nudity',
  DRUG_USE = 'drug_use',
  GAMBLING = 'gambling',
  HORROR = 'horror',
  FLASHING_LIGHTS = 'flashing_lights',
  LOUD_SOUNDS = 'loud_sounds',
  POLITICAL_CONTENT = 'political_content',
  RELIGIOUS_CONTENT = 'religious_content',
  MEDICAL_CONTENT = 'medical_content',
}

/**
 * Product statistics
 */
export interface ProductStats {
  readonly views: number;
  readonly downloads: number;
  readonly purchases: number;
  readonly revenue: Money;
  readonly rating: ProductRating;
  readonly engagement: EngagementMetrics;
  readonly performance: PerformanceMetrics;
  readonly conversion: ConversionMetrics;
}

/**
 * Product rating information
 */
export interface ProductRating {
  readonly average: number;
  readonly count: number;
  readonly distribution: RatingDistribution;
  readonly verified: number;
  readonly recent: number;
}

/**
 * Rating distribution by stars
 */
export interface RatingDistribution {
  readonly oneStar: number;
  readonly twoStar: number;
  readonly threeStar: number;
  readonly fourStar: number;
  readonly fiveStar: number;
}

/**
 * Engagement metrics
 */
export interface EngagementMetrics {
  readonly totalTime: number;
  readonly avgSession: number;
  readonly bounceRate: number;
  readonly returnRate: number;
  readonly shareCount: number;
  readonly commentCount: number;
  readonly favoriteCount: number;
}

/**
 * Performance metrics
 */
export interface PerformanceMetrics {
  readonly loadTime: number;
  readonly errorRate: number;
  readonly bandwidth: number;
  readonly cdn: CDNMetrics;
  readonly availability: number;
}

/**
 * CDN performance metrics
 */
export interface CDNMetrics {
  readonly hitRate: number;
  readonly bandwidth: number;
  readonly requests: number;
  readonly errors: number;
}

/**
 * Conversion metrics
 */
export interface ConversionMetrics {
  readonly viewToCart: number;
  readonly cartToPurchase: number;
  readonly previewToPurchase: number;
  readonly abandonmentRate: number;
  readonly refundRate: number;
}

/**
 * SEO configuration
 */
export interface ProductSEO {
  readonly metaTitle?: string;
  readonly metaDescription?: string;
  readonly metaKeywords?: string[];
  readonly canonicalUrl?: string;
  readonly ogTitle?: string;
  readonly ogDescription?: string;
  readonly ogImage?: string;
  readonly ogType?: string;
  readonly twitterCard?: string;
  readonly twitterTitle?: string;
  readonly twitterDescription?: string;
  readonly twitterImage?: string;
  readonly structuredData?: Record<string, any>;
  readonly robots?: RobotsConfig;
}

/**
 * Robots configuration
 */
export interface RobotsConfig {
  readonly index: boolean;
  readonly follow: boolean;
  readonly noarchive?: boolean;
  readonly nosnippet?: boolean;
  readonly noimageindex?: boolean;
}

/**
 * Product localization
 */
export interface ProductLocalization {
  readonly defaultLanguage: string;
  readonly translations: ProductTranslation[];
  readonly rtl: boolean;
  readonly currency: string;
  readonly timezone: string;
  readonly dateFormat: string;
  readonly numberFormat: string;
}

/**
 * Product translation
 */
export interface ProductTranslation {
  readonly language: string;
  readonly title: string;
  readonly description: string;
  readonly shortDescription?: string;
  readonly tags: string[];
  readonly seo: ProductSEO;
  readonly completeness: number;
  readonly lastUpdated: Date;
}

// Product creation and update DTOs

/**
 * Product creation request
 */
export interface CreateProductRequest {
  readonly title: string;
  readonly description: string;
  readonly shortDescription?: string;
  readonly category: ProductCategory;
  readonly subcategory?: string;
  readonly tags: string[];
  readonly pricing: Partial<ProductPricing>;
  readonly content: Partial<ProductContent>;
  readonly access?: Partial<ProductAccess>;
  readonly visibility?: Partial<ProductVisibility>;
  readonly metadata?: Partial<ProductMetadata>;
  readonly seo?: Partial<ProductSEO>;
}

/**
 * Product update request
 */
export interface UpdateProductRequest {
  readonly title?: string;
  readonly description?: string;
  readonly shortDescription?: string;
  readonly category?: ProductCategory;
  readonly subcategory?: string;
  readonly tags?: string[];
  readonly pricing?: Partial<ProductPricing>;
  readonly content?: Partial<ProductContent>;
  readonly access?: Partial<ProductAccess>;
  readonly visibility?: Partial<ProductVisibility>;
  readonly metadata?: Partial<ProductMetadata>;
  readonly seo?: Partial<ProductSEO>;
}

// Zod schemas for validation

export const ProductCategorySchema = z.nativeEnum(ProductCategory);

export const MoneyWithCurrencySchema = MoneySchema.extend({
  currency: z.string().length(3).toUpperCase(),
});

export const ProductPricingSchema = z.object({
  model: z.nativeEnum(PricingModel),
  basePrice: MoneyWithCurrencySchema,
  discountedPrice: MoneyWithCurrencySchema.optional(),
  paymentMethods: z.array(z.nativeEnum(PaymentMethod)).min(1),
});

export const ProductContentSchema = z.object({
  type: z.nativeEnum(ContentType),
  format: z.nativeEnum(ContentFormat),
  size: z.number().positive(),
  quality: z.nativeEnum(ContentQuality),
});

export const ProductSchema = BaseEntitySchema.extend({
  providerId: z.string().uuid(),
  title: z.string().min(1).max(200),
  description: z.string().min(1).max(5000),
  shortDescription: z.string().max(500).optional(),
  slug: z.string().min(1).max(100),
  category: ProductCategorySchema,
  subcategory: z.string().max(50).optional(),
  tags: z.array(z.string()).max(20),
  pricing: ProductPricingSchema,
  content: ProductContentSchema,
});

export const CreateProductRequestSchema = z.object({
  title: z.string().min(1).max(200),
  description: z.string().min(1).max(5000),
  shortDescription: z.string().max(500).optional(),
  category: ProductCategorySchema,
  subcategory: z.string().max(50).optional(),
  tags: z.array(z.string()).max(20),
  pricing: ProductPricingSchema.partial(),
  content: ProductContentSchema.partial(),
});

export const UpdateProductRequestSchema = CreateProductRequestSchema.partial();

export type ProductType = z.infer<typeof ProductSchema>;
export type CreateProductRequestType = z.infer<typeof CreateProductRequestSchema>;
export type UpdateProductRequestType = z.infer<typeof UpdateProductRequestSchema>;
