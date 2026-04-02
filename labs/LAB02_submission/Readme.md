# Lab 2 Submission README

## Student Information
- Name: Colton Wedell
- Date: 2026-04-02

## Deliverables Included
- `inference_api/Dockerfile`
- `preprocessor/Dockerfile`
- `inference_api/app.py` (with `/health` and `/stats`)
- `sample_classifications_20.jsonl` (first 20 lines from logs)
- `Reflection.md`

## Docker Build Commands Used

### Inference API
```bash
docker build -t classifier-app .
```

### Preprocessor
```bash
docker build -t watcher-app .
```

## Docker Run Commands Used

### Inference API Container
```bash
docker run --name my-classifier-container -p 8000:8000 -v ${PWD}\..\logs:/logs classifier-app
```

### Preprocessor Container
```bash
docker run --name my-watcher-container -e API_URL="http://host.docker.internal:8000" -v ${PWD}\..\incoming:/incoming watcher-app
```

## Brief Explanation: How the Containers Communicate
Each container can only access the endpoints that it needs to operate. The inference API container mounts to /logs to allow it to output results, and it uses the /predict endpoint to do its actual classification. The preprocessor container mounts to /incoming to allow it to view images, and it sends images to the API_URL that we defined when we first ran it. We give it the URL which points to the open port that we exposed when building the inference API image. Images and logs are preserved because we don't store anything inside the actual containers - we store everything on the host machine and simply allow the containers to access and modify those directories. Finally, we use host.docker.internal instead of localhost as the domain for our API URL, since localhost within a container simply refers to that container, and we need to back out to the host machine to access port 8000 where the inference API container is listening.

Points to cover:
- Which container calls which endpoint.
- How the preprocessor knows where to find the inference API.
- How images and logs persist using mounted host folders.
- Why `localhost` can be tricky inside containers.

