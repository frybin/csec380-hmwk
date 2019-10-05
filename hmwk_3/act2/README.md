# Running this part

## Build the docker image
> docker build -t act2_2 .

## Run the docker container with volume
> docker run --rm -v "$PWD":/tmp act2_2

The all of the `depth` files with the respective emails will be saved to your local directory.