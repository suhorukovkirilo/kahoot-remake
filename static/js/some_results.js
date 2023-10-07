socket.connect('http://' + document.domain + ':' + location.port + '/testing');

socket.on('next', function(){
    location.reload()
    });

socket.on('checked', function(){
    location.reload()
});