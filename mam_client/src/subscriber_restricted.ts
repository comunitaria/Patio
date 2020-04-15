declare var require: any

declare var process: {
  env: {
    ROOT: string
  }
}

const Mam = require('@iota/mam');
const IOTA = require('iota.lib.js');
const { asciiToTrytes, trytesToAscii } = require('@iota/converter')
const express = require('express');

var iota = new IOTA({ provider: `https://nodes.devnet.iota.org` })
const mode = "restricted"
const secretKey = 'VERYSECRETKEY'

// Init State
let root = process.env.ROOT;
console.log('Listening to root:', root);

// Initialise MAM State
var mamState = Mam.init(iota)

const execute = async () => {
    const resp = await Mam.fetch(root, mode, secretKey);
    try {
      resp.messages.forEach((message: any) => console.log(trytesToAscii(message)));
    } catch (e) {
        console.log(e)
    }

  if (resp.nextRoot) {
    root = resp.nextRoot;
    execute();
  } 

}

execute();
