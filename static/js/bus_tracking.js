// static/js/bus_tracking.js
document.addEventListener('DOMContentLoaded', function() {
    // Initialize the map
    var map = L.map('map').setView([25.2048, 55.2708], 10); // Default UAE coordinates

    // Add a tile layer (e.g., OpenStreetMap)
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    // Example: Add a marker for a bus location
    var busMarker = L.marker([25.2048, 55.2708]).addTo(map);
    busMarker.bindPopup("Bus Location");
    
    // Function to fetch and update bus locations
    const updateBusLocations = async () => {
        try {
            const response = await fetch(`${API_CONFIG.baseUrl}/api/locations/current/`);
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            const locations = await response.json();
            
            // Clear existing markers
            busMarkers.clearLayers();
            
            // Add new markers
            locations.forEach(location => {
                const marker = L.marker([location.latitude, location.longitude], {
                    icon: L.divIcon({
                        className: 'bus-marker',
                        html: `<i class="fas fa-bus" style="color: white; font-size: 1.5rem;"></i>`,
                        iconSize: [30, 30]
                    })
                });
                
                const popupContent = `
                    <div class="bus-info-window">
                        <h6>Bus ${location.bus_number}</h6>
                        <p>Status: <span class="badge bg-success">Active</span></p>
                        <p>Speed: ${location.speed} km/h</p>
                        <p>Last update: ${new Date(location.timestamp).toLocaleTimeString()}</p>
                        <a href="/admin/core/bus/${location.bus_id}/change/" class="btn btn-sm btn-primary mt-1">
                            View Details
                        </a>
                    </div>
                `;
                
                marker.bindPopup(popupContent).addTo(busMarkers);
            });
            
            // Update last updated time
            document.getElementById('lastUpdated').textContent = new Date().toLocaleTimeString();
            
            // Fit map to markers if there are any
            if (locations.length > 0) {
                const bounds = busMarkers.getBounds();
                if (bounds.isValid()) {
                    map.fitBounds(bounds, { padding: [50, 50] });
                }
            }
        } catch (error) {
            console.error('Error fetching bus locations:', error);
        }
    };
    
    // Initial load
    updateBusLocations();
    
    // Set up periodic updates
    const startLiveUpdates = () => {
        updateInterval = setInterval(updateBusLocations, API_CONFIG.updateInterval);
    };
    
    // Toggle live updates
    document.getElementById('liveTrackingToggle').addEventListener('change', function(e) {
        if (e.target.checked) {
            startLiveUpdates();
        } else {
            clearInterval(updateInterval);
        }
    });
    
    // Start updates
    startLiveUpdates();
});