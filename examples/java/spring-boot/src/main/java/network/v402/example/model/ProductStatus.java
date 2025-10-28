package network.v402.example.model;

/**
 * Enumeration for product status
 */
public enum ProductStatus {
    ACTIVE("Active"),
    INACTIVE("Inactive"),
    DRAFT("Draft");
    
    private final String displayName;
    
    ProductStatus(String displayName) {
        this.displayName = displayName;
    }
    
    public String getDisplayName() {
        return displayName;
    }
    
    @Override
    public String toString() {
        return displayName;
    }
}
