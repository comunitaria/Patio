declare var require: any

const Mam = require('@iota/mam');
const { asciiToTrytes, trytesToAscii } = require('@iota/converter')
const IOTA = require('iota.lib.js');
const express = require('express');

const provider =  `https://nodes.devnet.iota.org`  // https://nodes.thetangle.org:443
const mode = "restricted"
const secretKey = 'VERYSECRETKEY'
const port = 3500

const mamExplorerLink = `https://mam-explorer.firebaseapp.com/?provider=${encodeURIComponent(provider)}&mode=${mode}&root=`

// remove 'devnet' for mainnet
var iota = new IOTA({ provider: provider })
const app = express();

// Initialise MAM State - PUBLIC
var mamState = Mam.init(iota)

// To add restriction later:
// https://github.com/iotaledger/mam.client.js/blob/master/example/publishAndFetchRestricted.js

// Set channel mode
mamState = Mam.changeMode(mamState, mode, secretKey)

// Publish to tangle
const publish = async (packet: any) => {
  // Create MAM Payload - STRING OF TRYTES
  const trytes = asciiToTrytes(JSON.stringify(packet))
  var message = Mam.create(mamState, trytes)
  // Save new mamState
  mamState = message.state
  // Attach the payload.
  console.log("Before attach")
  // payload, address, depth, weight (14 main and hornet, 9 test) - https://github.com/iotaledger/mam.client.js
  await Mam.attach(message.payload, message.address, 3, 14)
  console.log("After attach")
  console.log('Root: ', message.root)
  console.log('Address: ', message.address)
  console.log(`Verify with MAM Explorer:\n${mamExplorerLink}${message.root}\n`);

  return message.root;
}


app.get('/', async (req: any, res: any) => {
  const { message } = req.query;

  console.log("publishing message:", message);

    try{
        const root = await publish(JSON.parse(message));
        res.json({message, root});
    } catch (e) {
        console.log(e)
    }
  
});

const server = app.listen(port, function (err: any) {
      if (err) { 
         console.log(err);
      } else {
         console.log("App started at port " + port);
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

// ./node_modules/.bin/ts-node src/publisher_restricted.ts
// 
