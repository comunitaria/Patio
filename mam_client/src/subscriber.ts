declare var require: any

declare var process: {
  env: {
    ROOT: string
  }
}

const Mam = require('@iota/mam'); // require('./mam.client.js');
const IOTA = require('iota.lib.js');
const express = require('express');

var iota = new IOTA({ provider: `https://nodes.devnet.iota.org` })

// Init State
let root = process.env.ROOT;
console.log('Listening to root:', root);

// Initialise MAM State
var mamState = Mam.init(iota)

const execute = async () => {
  const resp = await Mam.fetch(root, 'public');
  console.log(resp);

  if (resp.nextRoot) {
    root = resp.nextRoot;
    execute();
  } 

}

execute();
