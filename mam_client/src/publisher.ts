declare var require: any

const Mam = require('@iota/mam'); // require('./mam.client.js');
const IOTA = require('iota.lib.js');
const express = require('express');

var iota = new IOTA({ provider: `https://nodes.devnet.iota.org` })
const app = express();

// Initialise MAM State - PUBLIC
var mamState = Mam.init(iota)

// To add restriction later:
// https://github.com/iotaledger/mam.client.js/blob/master/example/publishAndFetchRestricted.js


// Publish to tangle
const publish = async (packet: any) => {
  // Create MAM Payload - STRING OF TRYTES
  var message = Mam.create(mamState, packet)
  // Save new mamState
  mamState = message.state
  // Attach the payload.
  console.log("Before attach")
  await Mam.attach(message.payload, message.address)
  console.log("After attach")
  console.log('Root: ', message.root)
  console.log('Address: ', message.address)
  return message.root;
}


app.get('/', async (req: any, res: any) => {
  const { message } = req.query;

  console.log("publishing message:", message);

    try{
        const root = await publish(message);
        res.json({message, root});
    } catch (e) {
        console.log(e)
    }
  
});

const server = app.listen(3000, function (err: any) {
      if (err) { 
         console.log(err);
      } else {
         console.log("App started at port 3000");
      }    
});

process.on('SIGTERM', () => {
  server.close(() => {
    console.log('Process terminated')
  })
})
process.on('SIGINT', () => {
  server.close(() => {
    console.log('Process terminated')
  })
})

// ./node_modules/.bin/ts-node src/publisher.ts
