// jshint esversion: 8
(function(exposed){'use strict';

// Initialization callback called from google once the API is done loading, so it has to be exposed.
function initMap() {
    const map = new google.maps.Map(document.getElementById("map"), {zoom:15});
    navigator.geolocation.getCurrentPosition(function(position){
        map.setCenter({
            lat: position.coords.latitude,
            lng: position.coords.longitude
        });
    });
}

exposed.initMap = initMap;
})((this.window = this.window || {}));
