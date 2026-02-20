# Architecture

## Goal
Provide a lightweight deployment runtime on VM2 using Docker Compose, with image build and release from VM1.

## Topology
- **VM1 (build node):** builds container images and pushes them to registry
- **Registry (GHCR):** stores versioned images
- **VM2 (deploy node):** pulls image tags and runs workloads with Docker Compose

## Deployment flow
1. Build image on VM1
2. Push image to GHCR with immutable tag
3. Run remote deploy script from VM1
4. VM2 pulls image and updates running service
5. Healthcheck validates successful rollout
