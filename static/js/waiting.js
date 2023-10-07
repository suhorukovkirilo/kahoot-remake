socket.connect('http://' + document.domain + ':' + location.port + '/testing');

socket.on('add_user', function(nickname) {
    var child = document.createElement('div');
    child.innerHTML = '<a href="/del/' + nickname + '" class="btn btn-primary" style="background-color: #381272; border-color: #381272; margin-left: 2px; margin-right: 2px;">' + nickname + '</a>';
    child = child.firstChild;
    document.getElementById('users').appendChild(child);
});

socket.on('quiz_start', function() {
    location.reload()
});

var play = function() {
    var audio = document.getElementById('audio');
    audio.volume = 0.35;
    audio.play();
    document.getElementById('play').style.visibility = 'hidden';
}