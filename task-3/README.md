## Requirements
 
- [Docker](https://www.docker.com/products/docker-desktop)
 
## Run locally
 
```bash
# 1. clone the repo
git clone <your-repo-url>
cd numpy-docker
 
# 2. build the image
docker build -t numpy-masks .
 
# 3. run the container
docker run --rm numpy-masks
```