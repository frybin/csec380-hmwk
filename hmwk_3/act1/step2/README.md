# Running this part

## Build the docker image
> docker build -t step2 .

## Run the docker container with volume
> docker run --rm -v "$PWD"/images:/staff_pics step2

The downloaded photos will be saved locally to a folder called `images`