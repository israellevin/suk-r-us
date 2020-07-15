/* jshint esversion: 8 */
/* globals google */
(async(exposed) => {'use strict';
const call = async (path, data) => await (await fetch(path, data ? {
    method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data)
} : {
    method: 'GET'
})).json();

const f = async () => {
    console.log('hi');
    console.log(await call('/create_game', {player_id: 'test', game_id: 'test'}));
    console.log(await call('/open_games'));
};
f();

// Initialization callback called from google once the API is done loading, so it has to be exposed.
function initMap() {
    return;
    const map = new google.maps.Map(document.getElementById("map"), {zoom:15});
    navigator.geolocation.getCurrentPosition(function(position){
        let current = {
            lat: position.coords.latitude,
            lng: position.coords.longitude
        };
        map.setCenter(current);
        new google.maps.Marker({position: current, icon: 'sup.png', map: map});
    });
}

exposed.initMap = initMap;
exposed.call = call;
})(this.window);
