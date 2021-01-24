const express = require('express');
const app = require('express')();
const http = require('http').Server(app);
const io = require('socket.io')(http);
const util = require('util');
const oscNode = require('node-osc');
// import {Client} from 'node-osc';
// const Audic = require("audic");
// var player = require("play-sound")(opts = {});
// const sound = require("sound-play");

//read from serial

const SerialPort = require('serialport')
const Readline = require('@serialport/parser-readline');
const OscClient = new oscNode.Client('127.0.0.1',9001);
const textures = ['wood','mud','metal','grass','snow'];
var pressure1 = 1000;
var pressure2 = 1000;
var pressure1Temp = 1000;
var pressure2Temp = 1000;




const port = 5000;
app.use(express.static('public'))
const clients = [];	//track connected clients
// const snow = new Audic("snowtrim.mp3")

//Server Web Client
app.get('/', function(req, res){
  res.sendFile(__dirname + '/index.html');
});

//make one reference to event name so it can be easily renamed 
const chatEvent = "chatMessage";
const sensorCOM3 = "sensorWalk";
const windRecMSG = 'wind';

//start reading serial
const serial = new SerialPort('/dev/ttyACM0', {
	baudRate: 115200
			})

const serial2 = new SerialPort('/dev/ttyACM1', {
	baudRate: 115200
			})	
// //parsing line of serial input
const parser = serial.pipe(new Readline())
const parser2 = serial2.pipe(new Readline())



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

	//Receving wind message 
	socket.on(windRecMSG, msg => {
		// console.log("hi");
		// console.log('Wind location is: --- '+msg)
		// let windLoc = JSON.parse(msg);
		yaw_to_id(msg).then((res)=>{
			if(res == 1 | res ==2){
				// console.log('{"fan":[1,1,0,0]}');
				serial.write('{"fan":[1,1,0,0]}');
			}else if(res == 3 | res ==4){
				// console.log('{"fan":[0,1,1,0]}');
				serial.write('{"fan":[0,1,1,0]}');
			}else if(res == 5 | res ==6){
				// console.log('{"fan":[0,0,1,1]}');
				serial.write('{"fan":[0,0,1,1]}');
			}else if(res == 7 | res ==8){
				// console.log('{"fan":[1,0,0,1]}');
				serial.write('{"fan":[1,0,0,1]}');
			}
				
		});
			
		
	})

	socket.on('walkingMat', msg => {
		console.log('walking mat is: --- '+msg.toString())
		let jss = JSON.parse(msg)
		let texture = jss.id;
		let textureID = textures.indexOf(texture);

		OscClient.send('/ino/texture',textureID,()=>{
			console.log('Texture Changed to: '+texture);
		});

		// let value = parseInt(jss.value);
		// console.log(texture,value);
		// if(value == 1){
		// 	OscClient.send('/ino/texture',1,1,()=>{
		// 		console.log('OSC SENT');
		// 	});

		// }else{
		// 	OscClient.send('/ino/texture',1,1,()=>{
		// 		console.log('OSC SENT');
		// 	});

		// };
		//ino/step 1,1 means foot on, left foot
		//ino/step 2,2 means foot off, right foot
		// OscClient.send('/ino/step',1,1,()=>{
		// 	console.log('OSC SENT');
		// });

	})

	// socket.on(sensorCOM3, msg => {
	// 	console.log('walking mat is: --- '+msg)
	// })
});


http.listen(port, () => {
    console.log('listening on *:' + port);
    
  });
// const snow = new Audic("snowtrim2.mp3");
// snow.load();
// var mySound = new Audio('snowtrim2.mp3');
// mySound.load();
parser.on('data', (a) =>{
	//console.log(a);
    	let mySTring = JSON.parse(a);
            // player.kill();
        // console.log(a.toString());
			// console.log(mySTring.X,mySTring.Y,mySTring.Z)
        io.emit(sensorCOM3,mySTring);
		  })
		  
parser2.on('data', (a) =>{
	// console.log(a);
		let mySTring = JSON.parse(a);
		let step = mySTring.step;
		let val = mySTring.val;
		if(val == 1){
			OscClient.send('/ino/step',1,step,()=>{
				console.log('OSC SENT');
				});	
		}
		if(val == 0){
			OscClient.send('/ino/step',2,step,()=>{
				console.log('OSC SENT');
				});	
		}
		
		// OscClient.send('/ino/step',2-val,step,()=>{
		// console.log('OSC SENT');
		// });	
		//ino/step 1,1 means foot on, left foot
		//ino/step 2,2 means foot off, right foot
		// OscClient.send('/ino/step',1,1,()=>{
		// 	console.log('OSC SENT');
		// });
            // player.kill();
        console.log(a.toString());
			// console.log(mySTring.X,mySTring.Y,mySTring.Z)
        // io.emit(sensorCOM3,mySTring);
          })


/////////////functional
const yaw_to_id = async function (msg) {
	// console.log(msg);
	let yaw = JSON.parse(msg).yaw;
	// console.log(yaw);
	
	if(yaw>0){ 
		// console.log('bigger');
		yaw = yaw/45;
		yaw = Math.round(yaw);
		return yaw
	}else{
		// console.log('bigger');
		yaw = -yaw/45;
		yaw = Math.round(yaw);
		return 8-yaw
	}
};

const pressure_detect = async function(json){
	let pres1 = json.pressure1;
	let pres2 = json.pressure2;
	if(pres2<300){

	}
}