// This script handles the Mapbox map initialization, bus tracking, and trip management.
// static/js/bus_tracking.js
document.addEventListener('DOMContentLoaded', function () {
    // Initialize Mapbox
    mapboxgl.accessToken = '{{ mapbox_access_token }}';

    const map = new mapboxgl.Map({
    container: 'mapid',
    style: 'mapbox://styles/mapbox/streets-v11',
    center: [55.9754, 21.4735], // Default center (Oman)
    zoom: 6,
    });

    // Add school locations as markers
    const schoolLocations = {{ school_locations|safe }};
    schoolLocations.forEach((loc) => {
    new mapboxgl.Marker({ color: '#FF5733' })
        .setLngLat([loc.lng, loc.lat])
        .setPopup(new mapboxgl.Popup().setHTML(`<b>${loc.name}</b>`))
        .addTo(map);
    });

    // Fetch live bus locations
    const buses = {{ buses|safe }};
    buses.forEach((bus) => {
    fetch(`/api/live-bus-locations/?bus_id=${bus.id}`)
        .then((response) => response.json())
        .then((data) => {
        if (data.length > 0) {
            const latestLocation = data[0];
            const coords = [latestLocation.longitude, latestLocation.latitude];

            // Update table
            document.getElementById(`last-location-${bus.id}`).innerText =
            `${latestLocation.latitude}, ${latestLocation.longitude}`;

            // Add marker to map
            new mapboxgl.Marker({ color: '#3498DB' })
            .setLngLat(coords)
            .setPopup(
                new mapboxgl.Popup().setHTML(
                `<b>Bus ${bus.bus_number}</b><br>Status: ${bus.status}`
                )
            )
            .addTo(map);
        }
        })
        .catch((error) => console.error('Error fetching bus location:', error));
    });

    // Handle Start Trip Button
    document.querySelectorAll('.start-trip-btn').forEach((button) => {
    button.addEventListener('click', () => {
        const busId = button.dataset.busId;

        fetch(`/api/bus-trips/${busId}/start/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json',
        },
        })
        .then((response) => response.json())
        .then((data) => {
            alert(data.status || 'Trip started successfully');
            button.disabled = true; // Disable the start button
            document
            .querySelector(`button[data-bus-id="${busId}"].stop-trip-btn`)
            .disabled = false; // Enable stop button
        })
        .catch((error) => console.error('Error starting trip:', error));
    });
    });

    // Handle Stop Trip Button
    document.querySelectorAll('.stop-trip-btn').forEach((button) => {
    button.addEventListener('click', () => {
        const busId = button.dataset.busId;

        fetch(`/api/bus-trips/${busId}/stop/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json',
        },
        })
        .then((response) => response.json())
        .then((data) => {
            alert(data.status || 'Trip stopped successfully');
            button.disabled = true; // Disable the stop button
            document
            .querySelector(`button[data-bus-id="${busId}"].start-trip-btn`)
            .disabled = false; // Enable start button
        })
        .catch((error) => console.error('Error stopping trip:', error));
    });
    });

    // Helper function to get CSRF token from cookies
    function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        cookies.forEach((cookie) => {
        const trimmedCookie = cookie.trim();
        if (trimmedCookie.startsWith(`${name}=`)) {
            cookieValue = decodeURIComponent(trimmedCookie.substring(name.length + 1));
        }
        });
    }
    return cookieValue;
    }
});
// Add a resize event listener to adjust the map size  