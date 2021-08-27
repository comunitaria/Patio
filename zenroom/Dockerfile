# Importing node12 docker image
FROM node:12-alpine

# Add dependencies
RUN apk add git python make g++

# Installing restroom
RUN npx degit dyne/restroom-template /restroom-mw
WORKDIR /restroom-mw
RUN yarn

# OLD - Install the latest restroom-mw packages
# RUN yarn add @restroom-mw/core@next @restroom-mw/db@next @restroom-mw/http@next @restroom-mw/sawroom@next @restroom-mw/ui@next @restroom-mw/utils@next


# Configure restroom
ENV ZENCODE_DIR=/restroom-mw/zencode
ENV CUSTOM_404_MESSAGE="nothing to see here"
ENV HTTP_PORT=3300
ENV HTTPS_PORT=3301
ENV OPENAPI=true


RUN cd zencode \
rm -rf  confkeys.conf confkeys.keys confkeys.zen random.zen keypair_username.zen keypair_username.keys ./restroom-mw/ ./misc/


# Adding the exported files
RUN echo "Adding exported contracts from apiroom"
RUN echo -e "\n# Always use 'Rule caller restroom-mw' when using Restroom\nRule caller restroom-mw\n\n\n# The scenario is not really necessary here, but nice to have\nScenario Patio: Store data into Sawroom \n\n# Here we are telling Zenroom where the Sawroom node is \nGiven that I have a sawroom endpoint named 'sawroomEndpoint'\n\n# Here we load a string, that we'll store in Sawroom\nGiven I have a 'string dictionary' named 'dataToStore'\n\n\n# IMPORTANT: always print the object(s) you want to write in Sawroom\n# otherwise Restroom won't be able to read them \nThen print the 'dataToStore'\n\n# The following statement stores the data in Sawroom and will return \n# a key/value where the key is the name of the tag you pass to it, \n# and the value is a unique identifier of this data, that you have to store\n# as you'll need it to retrieve the data from Sawroom\nThen I ask Sawroom to store the data named 'dataToStore' into the tag 'log_tag'\n\n"> ./zencode/patio_save_energy.zen
RUN echo -e '{"sawroomEndpoint":"http://195.201.41.35:8008"}' > ./zencode/patio_save_energy.keys
RUN echo -e "\n# Always use 'Rule caller restroom-mw' when using Restroom\nRule caller restroom-mw\n\n# The scenario is not really necessary here, but nice to have\nScenario Patio: Retrieve data from Sawroom\n\n\n# Here we are definining the 'endpoint' to connect where Sawroom is located\n\nGiven that I have a sawroom endpoint named 'sawroomEndpoint'\n\n\n# Here we are formatting the output of the reading \nAnd I have a 'string dictionary' named 'energy_log'\n\n\n# And I read the data with tag 'log_tag_id' from sawroom and save the output into 'energy_log'\n\nGiven I read from Sawroom the data in tag 'log_tag_id' and save the output into 'energy_log'\n\n\nThen print all data\n\n\n\n"> ./zencode/patio_load_energy_log.zen
RUN echo -e '{"sawroomEndpoint":"http://195.201.41.35:8008"}' > ./zencode/patio_load_energy_log.keys

# yarn install and run
CMD yarn start


