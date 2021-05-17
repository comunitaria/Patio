const { createChannel, createMessage, parseMessage, mamAttach, mamFetch, TrytesHelper } = require('@iota/mam.js');
const crypto = require('crypto');
const fs = require('fs');

const express = require('express');

const provider =  `https://chrysalis-nodes.iota.org`  // `https://nodes.devnet.iota.org`  // https://nodes.thetangle.org:443
const mode = "public"
const mamExplorerLink = `https://explorer.iota.org/mainnet/streams/0/`
//`https://mam-explorer.firebaseapp.com/?provider=${encodeURIComponent(provider)}&mode=${mode}&root=`
const port = 3000
const app = express();


let channelState;
// Try and load the channel state from json file
try {
  const currentState = fs.readFileSync('./channelState.json');
  if (currentState) {
      channelState = JSON.parse(currentState.toString());
  }
} catch (e) { }

// If we couldn't load the details then create a new channel.
if (!channelState) {
  channelState = createChannel(generateSeed(81), 2, mode)
}



// Publish to tangle
const publish = async (packet) => {
  // Create a MAM message using the channel state.
  const mamMessage = createMessage(channelState, TrytesHelper.fromAscii(JSON.stringify(packet)));

  // Store the channel state.
  try {
    fs.writeFileSync('./channelState.json', JSON.stringify(channelState, undefined, "\t"));
  } catch (e) {
      console.error(e)
  }
  // Attach the payload.
  console.log("Before attach")
  // payload, address, depth, weight (14 main and hornet, 9 test) - https://github.com/iotaledger/mam.client.js
  const { messageId } = await mamAttach(provider, mamMessage);
  console.log("After attach")
  console.log('Root: ', mamMessage.root)
  //console.log('Address: ', message.address)
  console.log(`Verify with MAM Explorer:\n${mamExplorerLink}${mamMessage.root}/${mode}/\n`);

  return mamMessage.root;
}


app.get('/', async (req, res) => {
  const { message } = req.query;

  console.log("publishing message:", message);

    try{
        const root = await publish(JSON.parse(message));
        res.json({message, root});
    } catch (e) {
        console.log(e)
    }
  
});

const server = app.listen(port, function (err) {
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

function generateSeed(length) {
  const charset = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ9';
  let seed = '';
  while (seed.length < length) {
      const byte = crypto.randomBytes(1)
      if (byte[0] < 243) {
          seed += charset.charAt(byte[0] % 27);
      }
  }
  return seed;
}

// ./node_modules/.bin/ts-node src/publisher.ts
// 
