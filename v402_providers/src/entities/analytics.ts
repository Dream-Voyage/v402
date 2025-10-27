/**
 * V402 Providers SDK - Analytics Entity Definitions
 *
 * This file contains all analytics-related entity interfaces and types
 * for tracking metrics, generating reports, and analyzing performance in the V402 ecosystem.
 *
 * @author V402 Team
 * @version 1.0.0
 * @since 2024-01-01
 */

import {Money} from './base';

/**
 * Analytics dashboard data
 */
export interface AnalyticsDashboard {
  readonly overview: OverviewMetrics;
  readonly products: ProductMetrics[];
  readonly revenue: RevenueMetrics;
  readonly traffic: TrafficMetrics;
  readonly conversions: ConversionMetrics;
  readonly customers: CustomerMetrics;
  readonly geographic: GeographicMetrics;
  readonly temporal: TemporalMetrics;
  readonly realTime: RealTimeMetrics;
  readonly recommendations: AnalyticsRecommendation[];
}

/**
 * Overview metrics
 */
export interface OverviewMetrics {
  readonly totalRevenue: Money;
  readonly totalSales: number;
  readonly totalViews: number;
  readonly totalDownloads: number;
  readonly activeProducts: number;
  readonly totalCustomers: number;
  readonly conversionRate: number;
  readonly averageOrderValue: Money;
  readonly revenueGrowth: GrowthMetrics;
  readonly salesGrowth: GrowthMetrics;
  readonly trafficGrowth: GrowthMetrics;
}

/**
 * Growth metrics
 */
export interface GrowthMetrics {
  readonly value: number;
  readonly percentage: number;
  readonly direction: GrowthDirection;
  readonly period: string;
  readonly comparison: number;
}

/**
 * Growth direction
 */
export enum GrowthDirection {
  UP = 'up',
  DOWN = 'down',
  STABLE = 'stable',
  UNKNOWN = 'unknown',
}

/**
 * Product metrics
 */
export interface ProductMetrics {
  readonly productId: string;
  readonly title: string;
  readonly category: string;
  readonly views: number;
  readonly sales: number;
  readonly revenue: Money;
  readonly conversionRate: number;
  readonly averagePrice: Money;
  readonly rating: number;
  readonly reviews: number;
  readonly growth: GrowthMetrics;
  readonly trends: TrendData;
  readonly topReferrers: ReferrerMetrics[];
  readonly userSegments: SegmentMetrics[];
}

/**
 * Trend data
 */
export interface TrendData {
  readonly direction: TrendDirection;
  readonly strength: TrendStrength;
  readonly dataPoints: DataPoint[];
  readonly forecast?: ForecastData;
}

/**
 * Trend directions
 */
export enum TrendDirection {
  UPWARD = 'upward',
  DOWNWARD = 'downward',
  FLAT = 'flat',
  VOLATILE = 'volatile',
}

/**
 * Trend strength
 */
export enum TrendStrength {
  WEAK = 'weak',
  MODERATE = 'moderate',
  STRONG = 'strong',
}

/**
 * Data point
 */
export interface DataPoint {
  readonly timestamp: Date;
  readonly value: number;
  readonly metadata?: Record<string, any>;
}

/**
 * Forecast data
 */
export interface ForecastData {
  readonly predictedValues: DataPoint[];
  readonly confidence: number;
  readonly methodology: ForecastingMethod;
  readonly nextPeriod: number;
}

/**
 * Forecasting methods
 */
export enum ForecastingMethod {
  LINEAR = 'linear',
  EXPONENTIAL = 'exponential',
  MOVING_AVERAGE = 'moving_average',
  ARIMA = 'arima',
  MACHINE_LEARNING = 'machine_learning',
  ENSEMBLE = 'ensemble',
}

/**
 * Revenue metrics
 */
export interface RevenueMetrics {
  readonly total: Money;
  readonly byPeriod: RevenueByPeriod;
  readonly byProduct: RevenueByProduct[];
  readonly byMethod: RevenueByMethod[];
  readonly byCurrency: RevenueByCurrency[];
  readonly projections: RevenueProjection[];
  readonly breakdown: RevenueBreakdown;
}

/**
 * Revenue by time period
 */
export interface RevenueByPeriod {
  readonly today: Money;
  readonly yesterday: Money;
  readonly thisWeek: Money;
  readonly lastWeek: Money;
  readonly thisMonth: Money;
  readonly lastMonth: Money;
  readonly thisQuarter: Money;
  readonly lastQuarter: Money;
  readonly thisYear: Money;
  readonly lastYear: Money;
  readonly allTime: Money;
}

/**
 * Revenue by product
 */
export interface RevenueByProduct {
  readonly productId: string;
  readonly title: string;
  readonly revenue: Money;
  readonly percentage: number;
  readonly sales: number;
  readonly trend: TrendData;
}

/**
 * Revenue by payment method
 */
export interface RevenueByMethod {
  readonly method: string;
  readonly revenue: Money;
  readonly percentage: number;
  readonly transactionCount: number;
  readonly averageTransaction: Money;
}

/**
 * Revenue by currency
 */
export interface RevenueByCurrency {
  readonly currency: string;
  readonly revenue: Money;
  readonly percentage: number;
  readonly exchangeRate?: number;
}

/**
 * Revenue projection
 */
export interface RevenueProjection {
  readonly period: string;
  readonly projected: Money;
  readonly confidence: number;
  readonly basedOn: ProjectionBasis;
  readonly scenarios: ProjectionScenario[];
}

/**
 * Projection basis
 */
export enum ProjectionBasis {
  HISTORICAL = 'historical',
  SEASONAL = 'seasonal',
  GROWTH = 'growth',
  MARKET = 'market',
  COMBINED = 'combined',
}

/**
 * Projection scenario
 */
export interface ProjectionScenario {
  readonly name: string;
  readonly probability: number;
  readonly value: Money;
  readonly assumptions: string[];
}

/**
 * Revenue breakdown
 */
export interface RevenueBreakdown {
  readonly gross: Money;
  readonly fees: Money;
  readonly refunds: Money;
  readonly net: Money;
  readonly feesPercentage: number;
  readonly refundsPercentage: number;
  readonly netPercentage: number;
}

/**
 * Traffic metrics
 */
export interface TrafficMetrics {
  readonly total: number;
  readonly unique: number;
  readonly returning: number;
  readonly new: number;
  readonly bySource: TrafficBySource[];
  readonly byDevice: TrafficByDevice[];
  readonly byBrowser: TrafficByBrowser[];
  readonly byOS: TrafficByOS[];
  readonly byCountry: TrafficByCountry[];
  readonly topPages: PageMetrics[];
  readonly bounceRate: number;
  readonly averageSessionDuration: number;
  readonly pagesPerSession: number;
}

/**
 * Traffic by source
 */
export interface TrafficBySource {
  readonly source: string;
  readonly medium: string;
  readonly campaign?: string;
  readonly sessions: number;
  readonly percentage: number;
  readonly conversions: number;
  readonly conversionRate: number;
}

/**
 * Traffic by device
 */
export interface TrafficByDevice {
  readonly device: string;
  readonly sessions: number;
  readonly percentage: number;
  readonly averageSessionDuration: number;
  readonly bounceRate: number;
}

/**
 * Traffic by browser
 */
export interface TrafficByBrowser {
  readonly browser: string;
  readonly sessions: number;
  readonly percentage: number;
  readonly versions: BrowserVersion[];
}

/**
 * Browser version
 */
export interface BrowserVersion {
  readonly version: string;
  readonly sessions: number;
  readonly percentage: number;
}

/**
 * Traffic by OS
 */
export interface TrafficByOS {
  readonly os: string;
  readonly sessions: number;
  readonly percentage: number;
}

/**
 * Traffic by country
 */
export interface TrafficByCountry {
  readonly country: string;
  readonly countryCode: string;
  readonly sessions: number;
  readonly percentage: number;
  readonly revenue: Money;
  readonly conversions: number;
}

/**
 * Page metrics
 */
export interface PageMetrics {
  readonly url: string;
  readonly title: string;
  readonly views: number;
  readonly uniqueViews: number;
  readonly averageTimeOnPage: number;
  readonly bounceRate: number;
  readonly revenue: Money;
  readonly conversions: number;
  readonly exitRate: number;
}

/**
 * Conversion metrics
 */
export interface ConversionMetrics {
  readonly overallRate: number;
  readonly bySource: ConversionBySource[];
  readonly byProduct: ConversionByProduct[];
  readonly byDevice: ConversionByDevice[];
  readonly byGeography: ConversionByGeography[];
  readonly funnel: FunnelMetrics;
  readonly attribution: AttributionMetrics;
}

/**
 * Conversion by source
 */
export interface ConversionBySource {
  readonly source: string;
  readonly conversions: number;
  readonly conversionRate: number;
  readonly averageOrderValue: Money;
  readonly lifetimeValue: Money;
}

/**
 * Conversion by product
 */
export interface ConversionByProduct {
  readonly productId: string;
  readonly title: string;
  readonly views: number;
  readonly conversions: number;
  readonly conversionRate: number;
  readonly averageOrderValue: Money;
}

/**
 * Conversion by device
 */
export interface ConversionByDevice {
  readonly device: string;
  readonly sessions: number;
  readonly conversions: number;
  readonly conversionRate: number;
  readonly averageOrderValue: Money;
}

/**
 * Conversion by geography
 */
export interface ConversionByGeography {
  readonly country: string;
  readonly countryCode: string;
  readonly sessions: number;
  readonly conversions: number;
  readonly conversionRate: number;
  readonly revenue: Money;
}

/**
 * Funnel metrics
 */
export interface FunnelMetrics {
  readonly stages: FunnelStage[];
  readonly conversionRates: number[];
  readonly dropOffRates: number[];
  readonly bottlenecks: FunnelBottleneck[];
}

/**
 * Funnel stage
 */
export interface FunnelStage {
  readonly name: string;
  readonly order: number;
  readonly visits: number;
  readonly conversions: number;
  readonly conversionRate: number;
  readonly averageTime: number;
}

/**
 * Funnel bottleneck
 */
export interface FunnelBottleneck {
  readonly stage: string;
  readonly dropOffRate: number;
  readonly impact: BottleneckImpact;
  readonly recommendations: string[];
}

/**
 * Bottleneck impact
 */
export enum BottleneckImpact {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  CRITICAL = 'critical',
}

/**
 * Attribution metrics
 */
export interface AttributionMetrics {
  readonly model: AttributionModel;
  readonly contributions: AttributionContribution[];
  readonly touchpoints: TouchpointMetrics[];
}

/**
 * Attribution models
 */
export enum AttributionModel {
  FIRST_TOUCH = 'first_touch',
  LAST_TOUCH = 'last_touch',
  LINEAR = 'linear',
  TIME_DECAY = 'time_decay',
  POSITION_BASED = 'position_based',
  DATA_DRIVEN = 'data_driven',
  SHAPLEY = 'shapley',
}

/**
 * Attribution contribution
 */
export interface AttributionContribution {
  readonly channel: string;
  readonly contribution: number;
  readonly percentage: number;
  readonly conversions: number;
}

/**
 * Touchpoint metrics
 */
export interface TouchpointMetrics {
  readonly channel: string;
  readonly touchpoint: string;
  readonly frequency: number;
  readonly conversionRate: number;
  readonly averageTimeToConvert: number;
}

/**
 * Customer metrics
 */
export interface CustomerMetrics {
  readonly total: number;
  readonly active: number;
  readonly new: number;
  readonly returning: number;
  readonly churned: number;
  readonly lifetimeValue: Money;
  readonly averageCustomerLifetime: number;
  readonly churnRate: number;
  readonly acquisitionCost: Money;
  readonly segments: CustomerSegment[];
  readonly cohorts: CustomerCohort[];
  readonly retention: RetentionMetrics;
}

/**
 * Customer segment
 */
export interface CustomerSegment {
  readonly segmentId: string;
  readonly name: string;
  readonly size: number;
  readonly percentage: number;
  readonly characteristics: string[];
  readonly lifetimeValue: Money;
  readonly averageOrderValue: Money;
  readonly purchaseFrequency: number;
}

/**
 * Customer cohort
 */
export interface CustomerCohort {
  readonly cohortId: string;
  readonly period: string;
  readonly size: number;
  readonly revenue: Money;
  readonly retention: number;
  readonly trends: CohortTrend[];
}

/**
 * Cohort trend
 */
export interface CohortTrend {
  readonly period: string;
  readonly value: number;
  readonly percentage: number;
}

/**
 * Retention metrics
 */
export interface RetentionMetrics {
  readonly byPeriod: RetentionByPeriod;
  readonly bySegment: RetentionBySegment[];
  readonly trends: RetentionTrend[];
}

/**
 * Retention by period
 */
export interface RetentionByPeriod {
  readonly day1: number;
  readonly day7: number;
  readonly day30: number;
  readonly day60: number;
  readonly day90: number;
  readonly day180: number;
  readonly day365: number;
}

/**
 * Retention by segment
 */
export interface RetentionBySegment {
  readonly segment: string;
  readonly day30: number;
  readonly day60: number;
  readonly day90: number;
}

/**
 * Retention trend
 */
export interface RetentionTrend {
  readonly period: string;
  readonly retention: number;
  readonly cohort: string;
}

/**
 * Geographic metrics
 */
export interface GeographicMetrics {
  readonly byCountry: GeographicByCountry[];
  readonly byRegion: GeographicByRegion[];
  readonly byCity: GeographicByCity[];
  readonly heatmap: HeatmapData;
  readonly trends: GeographicTrend[];
}

/**
 * Geographic data by country
 */
export interface GeographicByCountry {
  readonly country: string;
  readonly countryCode: string;
  readonly sessions: number;
  readonly revenue: Money;
  readonly conversions: number;
  readonly averageOrderValue: Money;
  readonly conversionRate: number;
}

/**
 * Geographic data by region
 */
export interface GeographicByRegion {
  readonly region: string;
  readonly sessions: number;
  readonly revenue: Money;
  readonly conversions: number;
}

/**
 * Geographic data by city
 */
export interface GeographicByCity {
  readonly city: string;
  readonly country: string;
  readonly sessions: number;
  readonly revenue: Money;
  readonly conversions: number;
}

/**
 * Heatmap data
 */
export interface HeatmapData {
  readonly coordinates: HeatmapCoordinate[];
  readonly intensity: number;
  readonly colorScale: ColorScale;
}

/**
 * Heatmap coordinate
 */
export interface HeatmapCoordinate {
  readonly latitude: number;
  readonly longitude: number;
  readonly value: number;
  readonly metadata?: Record<string, any>;
}

/**
 * Color scale
 */
export interface ColorScale {
  readonly min: string;
  readonly max: string;
  readonly steps: ColorScaleStep[];
}

/**
 * Color scale step
 */
export interface ColorScaleStep {
  readonly value: number;
  readonly color: string;
}

/**
 * Geographic trend
 */
export interface GeographicTrend {
  readonly location: string;
  readonly trend: TrendData;
  readonly period: string;
}

/**
 * Temporal metrics
 */
export interface TemporalMetrics {
  readonly byHour: TemporalByHour[];
  readonly byDay: TemporalByDay[];
  readonly byWeek: TemporalByWeek[];
  readonly byMonth: TemporalByMonth[];
  readonly byDayOfWeek: TemporalByDayOfWeek[];
  readonly byMonthOfYear: TemporalByMonthOfYear[];
  readonly seasonal: SeasonalPatterns;
  readonly peaks: PeakPeriod[];
}

/**
 * Temporal data by hour
 */
export interface TemporalByHour {
  readonly hour: number;
  readonly sessions: number;
  readonly revenue: Money;
  readonly conversions: number;
}

/**
 * Temporal data by day
 */
export interface TemporalByDay {
  readonly day: Date;
  readonly sessions: number;
  readonly revenue: Money;
  readonly conversions: number;
}

/**
 * Temporal data by week
 */
export interface TemporalByWeek {
  readonly week: string;
  readonly sessions: number;
  readonly revenue: Money;
  readonly conversions: number;
}

/**
 * Temporal data by month
 */
export interface TemporalByMonth {
  readonly month: string;
  readonly sessions: number;
  readonly revenue: Money;
  readonly conversions: number;
}

/**
 * Temporal data by day of week
 */
export interface TemporalByDayOfWeek {
  readonly day: string;
  readonly sessions: number;
  readonly revenue: Money;
  readonly conversionRate: number;
}

/**
 * Temporal data by month of year
 */
export interface TemporalByMonthOfYear {
  readonly month: string;
  readonly sessions: number;
  readonly revenue: Money;
  readonly conversionRate: number;
}

/**
 * Seasonal patterns
 */
export interface SeasonalPatterns {
  readonly detected: boolean;
  readonly patterns: Pattern[];
  readonly seasonality: Seasonality[];
}

/**
 * Pattern
 */
export interface Pattern {
  readonly type: PatternType;
  readonly strength: number;
  readonly period: number;
  readonly description: string;
}

/**
 * Pattern types
 */
export enum PatternType {
  SEASONAL = 'seasonal',
  CYCLICAL = 'cyclical',
  TREND = 'trend',
  IRREGULAR = 'irregular',
  WEEKLY = 'weekly',
  MONTHLY = 'monthly',
  YEARLY = 'yearly',
}

/**
 * Seasonality
 */
export interface Seasonality {
  readonly period: string;
  readonly effect: number;
  readonly confidence: number;
}

/**
 * Peak period
 */
export interface PeakPeriod {
  readonly start: Date;
  readonly end: Date;
  readonly duration: number;
  readonly intensity: number;
  readonly type: PeakType;
}

/**
 * Peak types
 */
export enum PeakType {
  TRAFFIC = 'traffic',
  SALES = 'sales',
  REVENUE = 'revenue',
  ENGAGEMENT = 'engagement',
  CONVERSION = 'conversion',
}

/**
 * Real-time metrics
 */
export interface RealTimeMetrics {
  readonly activeUsers: number;
  readonly sessions: number;
  readonly revenue: Money;
  readonly conversions: number;
  readonly topProducts: RealTimeProduct[];
  readonly topPages: RealTimePage[];
  readonly activity: ActivityStream;
}

/**
 * Real-time product data
 */
export interface RealTimeProduct {
  readonly productId: string;
  readonly title: string;
  readonly views: number;
  readonly revenue: Money;
  readonly trend: TrendDirection;
}

/**
 * Real-time page data
 */
export interface RealTimePage {
  readonly url: string;
  readonly activeUsers: number;
  readonly trend: TrendDirection;
}

/**
 * Activity stream
 */
export interface ActivityStream {
  readonly events: ActivityEvent[];
  readonly totalEvents: number;
  readonly eventRate: number;
}

/**
 * Activity event
 */
export interface ActivityEvent {
  readonly timestamp: Date;
  readonly type: ActivityType;
  readonly description: string;
  readonly metadata?: Record<string, any>;
}

/**
 * Activity types
 */
export enum ActivityType {
  VIEW = 'view',
  PURCHASE = 'purchase',
  DOWNLOAD = 'download',
  SHARE = 'share',
  COMMENT = 'comment',
  LIKE = 'like',
  SUBSCRIPTION = 'subscription',
  REFUND = 'refund',
}

/**
 * Analytics recommendation
 */
export interface AnalyticsRecommendation {
  readonly id: string;
  readonly type: RecommendationType;
  readonly priority: RecommendationPriority;
  readonly title: string;
  readonly description: string;
  readonly impact: RecommendationImpact;
  readonly effort: RecommendationEffort;
  readonly actionItems: string[];
  readonly estimatedBenefit: string;
  readonly confidence: number;
}

/**
 * Recommendation types
 */
export enum RecommendationType {
  OPTIMIZATION = 'optimization',
  PRICING = 'pricing',
  PROMOTION = 'promotion',
  CONTENT = 'content',
  MARKETING = 'marketing',
  CONVERSION = 'conversion',
  RETENTION = 'retention',
  SEGMENTATION = 'segmentation',
}

/**
 * Recommendation priority
 */
export enum RecommendationPriority {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  CRITICAL = 'critical',
}

/**
 * Recommendation impact
 */
export enum RecommendationImpact {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  TRANSFORMATIONAL = 'transformational',
}

/**
 * Recommendation effort
 */
export enum RecommendationEffort {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  VERY_HIGH = 'very_high',
}

// Analytics query options

/**
 * Analytics query options
 */
export interface AnalyticsQueryOptions {
  readonly dateRange: DateRange;
  readonly granularity?: Granularity;
  readonly dimensions?: string[];
  readonly metrics?: string[];
  readonly filters?: AnalyticsFilter[];
  readonly sorting?: AnalyticsSort[];
  readonly limit?: number;
  readonly offset?: number;
}

/**
 * Date range
 */
export interface DateRange {
  readonly start: Date;
  readonly end: Date;
}

/**
 * Granularity
 */
export enum Granularity {
  HOURLY = 'hourly',
  DAILY = 'daily',
  WEEKLY = 'weekly',
  MONTHLY = 'monthly',
  QUARTERLY = 'quarterly',
  YEARLY = 'yearly',
}

/**
 * Analytics filter
 */
export interface AnalyticsFilter {
  readonly field: string;
  readonly operator: FilterOperator;
  readonly value: any;
}

/**
 * Filter operators
 */
export enum FilterOperator {
  EQUALS = 'equals',
  NOT_EQUALS = 'not_equals',
  GREATER_THAN = 'greater_than',
  LESS_THAN = 'less_than',
  GREATER_THAN_OR_EQUAL = 'greater_than_or_equal',
  LESS_THAN_OR_EQUAL = 'less_than_or_equal',
  CONTAINS = 'contains',
  NOT_CONTAINS = 'not_contains',
  STARTS_WITH = 'starts_with',
  ENDS_WITH = 'ends_with',
  IN = 'in',
  NOT_IN = 'not_in',
  BETWEEN = 'between',
  IS_NULL = 'is_null',
  IS_NOT_NULL = 'is_not_null',
}

/**
 * Analytics sort
 */
export interface AnalyticsSort {
  readonly field: string;
  readonly direction: SortDirection;
}

/**
 * Sort direction
 */
export enum SortDirection {
  ASC = 'asc',
  DESC = 'desc',
}

export type DashboardType = AnalyticsDashboard;
export type MetricsType = OverviewMetrics;
