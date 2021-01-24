const app = require('express')();
const http = require('http').Server(app);
const io = require('socket.io')(http);
const util = require('util');
//read from serial

const SerialPort = require('serialport')
const Readline = require('@serialport/parser-readline')


const port = 3000;
const clients = [];	//track connected clients

//Server Web Client
app.get('/', function(req, res){
  res.sendFile(__dirname + '/index.html');
});

//make one reference to event name so it can be easily renamed 
const chatEvent = "chatMessage";
const sensorCOM3 = "sensor1";

//start reading serial
const serial = new SerialPort('COM3', {
    baudRate: 115200
})
//parsing line of serial input
const parser = serial.pipe(new Readline({ delimiter: '\r\n' }))


//When a client connects, bind each desired event to the client socket
io.on('connection', socket =>{
	//track connected clients via log
	clients.push(socket.id);
	const clientConnectedMsg = 'User connected ' + util.inspect(socket.id) + ', total: ' + clients.length;
	io.emit(chatEvent, clientConnectedMsg);
	console.log(clientConnectedMsg);

	//track disconnected clients via log
	socket.on('disconnect', ()=>{
		clients.pop(socket.id);
		const clientDisconnectedMsg = 'User disconnected ' + util.inspect(socket.id) + ', total: ' + clients.length;
		io.emit(chatEvent, clientDisconnectedMsg);
		console.log(clientDisconnectedMsg);
	})

	//multicast received message from client
	socket.on(chatEvent, msg =>{
		const combinedMsg = socket.id.substring(0,4) + ': ' + msg;
		io.emit(chatEvent, combinedMsg);
		console.log('multicast: ' + combinedMsg);
	});
});

//Start the Server
// http.listen(port,'192.168.0.100', () => {
//   console.log('listening on *:' + port);
// });
http.listen(port, () => {
	console.log('listening on *:' + port);
  });

parser.on('data', (a) =>{
    let mySTring = JSON.parse(a);
            console.log(a.toString())
			// console.log(mySTring.X,mySTring.Y,mySTring.Z)
			io.emit(sensorCOM3,mySTring);
          })
