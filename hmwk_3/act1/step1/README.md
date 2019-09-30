# Running this step

## Build the docker image
> docker build -t step1 .

## Run the docker image
> docker run --rm -v "$PWD":/stuff step1

This runs the docker image and saves the `courses.csv` file to your local directory