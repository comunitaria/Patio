#!/bin/bash

# Run publisher forever, restarting when exiting due to connection issues.
while :
do
    ./node_modules/.bin/ts-node src/publisher.ts
done
