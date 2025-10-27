package network.v402.client.model;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.Instant;
import java.time.Duration;
import java.util.Map;

/**
 * Represents the response from an HTTP request processed through the v402 protocol.
 * 
 * This class encapsulates both the HTTP response data and payment-related information
 * when a payment was made to access the resource.
 * 
 * @author v402 Team
 * @version 1.0.0
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@JsonIgnoreProperties(ignoreUnknown = true)
public class PaymentResponse {
    
    /**
     * HTTP status code of the response.
     */
    @JsonProperty("status_code")
    private int statusCode;
    
    /**
     * Response body as byte array.
     */
    @JsonProperty("body")
    private byte[] body;
    
    /**
     * HTTP headers from the response.
     */
    @JsonProperty("headers")
    private Map<String, String> headers;
    
    /**
     * Original URL that was requested.
     */
    @JsonProperty("url")
    private String url;
    
    /**
     * Whether a payment was made for this request.
     */
    @JsonProperty("payment_made")
    private boolean paymentMade;
    
    /**
     * Amount paid in wei/lamports (if payment was made).
     */
    @JsonProperty("payment_amount")
    private String paymentAmount;
    
    /**
     * Transaction hash of the payment (if payment was made).
     */
    @JsonProperty("transaction_hash")
    private String transactionHash;
    
    /**
     * Network where payment was made (ethereum, base, polygon, etc.).
     */
    @JsonProperty("network")
    private String network;
    
    /**
     * Address of the payer (if payment was made).
     */
    @JsonProperty("payer")
    private String payer;
    
    /**
     * Timestamp when the response was received.
     */
    @JsonProperty("timestamp")
    private Instant timestamp;
    
    /**
     * Total time taken for the request.
     */
    @JsonProperty("total_time")
    private Duration totalTime;
    
    /**
     * DNS resolution time.
     */
    @JsonProperty("dns_time")
    private Duration dnsTime;
    
    /**
     * Connection establishment time.
     */
    @JsonProperty("connect_time")
    private Duration connectTime;
    
    /**
     * Returns the response body as a UTF-8 string.
     * 
     * @return Response body as string
     */
    public String getBodyAsString() {
        if (body == null) {
            return null;
        }
        return new String(body, java.nio.charset.StandardCharsets.UTF_8);
    }
    
    /**
     * Checks if the response indicates success (status code 200-299).
     * 
     * @return true if successful, false otherwise
     */
    public boolean isSuccessful() {
        return statusCode >= 200 && statusCode < 300;
    }
    
    /**
     * Gets a specific header value.
     * 
     * @param name Header name (case-insensitive)
     * @return Header value or null if not found
     */
    public String getHeader(String name) {
        if (headers == null || name == null) {
            return null;
        }
        
        // Case-insensitive lookup
        return headers.entrySet().stream()
                .filter(entry -> entry.getKey().equalsIgnoreCase(name))
                .map(Map.Entry::getValue)
                .findFirst()
                .orElse(null);
    }
    
    /**
     * Gets the Content-Type header value.
     * 
     * @return Content-Type value or null if not present
     */
    public String getContentType() {
        return getHeader("Content-Type");
    }
    
    /**
     * Gets the Content-Length header value.
     * 
     * @return Content-Length value or -1 if not present or invalid
     */
    public long getContentLength() {
        String contentLength = getHeader("Content-Length");
        if (contentLength != null) {
            try {
                return Long.parseLong(contentLength);
            } catch (NumberFormatException e) {
                return -1;
            }
        }
        return body != null ? body.length : -1;
    }
}
