/* jshint esversion: 8 */
/* globals google */
(async(exposed) => {'use strict';

// Helper for calling our server and parsing the response.
const call = async (path, data) => new Promise(async(resolve, reject) => {
    const response = await fetch(path, data ? {
        method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data)
    } : {
        method: 'GET'
    }).then(response => response.json());
    if(!response.success){
        console.error('failed response from server', path, data, response);
        return reject(new Error('failed response from server'));
    }
    console.debug('successful response from server', path, data, response);
    resolve(response);
});

// Helper for creating unique IDs.
const randomString = () => Math.random().toString(16).substring(2, 10);
const playerId = randomString();
let gameId = randomString();

// Control elements.
const gamesList = document.getElementById('games');
const statusline = document.getElementById('statusline');
const playerAvatars = document.querySelectorAll('.player');

const showGames = async () => {
    let gamesListItems = [];
    for(let game of (await call('/open_games')).games){
        const li = document.createElement('li');
        li.textContent = game;
        gamesListItems.push(li);
    }
    console.log('removing');
    gamesList.innerHTML = '';
    gamesListItems.forEach(item => gamesList.appendChild(item));
};

setInterval(showGames, 1000);

// Initialization callback called from google once the API is done loading, so it has to be exposed.
exposed.initMap = () => {
    const map = new google.maps.Map(document.getElementById("map"), {zoom:15});

    // Register player on avatar click.
    const playerAvatarClick = clickEvent => {
        playerAvatars.forEach(playerAvatar => playerAvatar.removeEventListener('click', playerAvatarClick));
        const playerAvatar = clickEvent.target;

        // Get current location.
        navigator.geolocation.getCurrentPosition(async position => {
            let current = {
                lat: position.coords.latitude,
                lng: position.coords.longitude
            };
            map.setCenter(current);
            new google.maps.Marker({position: current, icon: playerAvatar.src, map: map});
            playerAvatar.classList.remove('offline');
            await call('/register_player', {player_id: playerId, character: playerAvatar.id});
            await call('/create_game', {player_id: playerId, game_id: gameId});
            statusline.textContent = 'Waiting for ' + (playerAvatar.id === 'sakura' ? 'superman' : 'sakura') + ' to join';
        });
    };
    playerAvatars.forEach(playerAvatar => playerAvatar.addEventListener('click', playerAvatarClick));
    statusline.textContent = 'Click on your avatar to start a new game or join an existing one';
};

})(this.window);
