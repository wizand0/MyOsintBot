
---

▎1. If the settings in the source code or Dockerfile have changed (build part)

Rebuild the images and restart the containers:
```
docker-compose up -d --build
```

This command:

• Rebuilds the images for containers for which there are changes in the Dockerfile or the build context.

• Stops the old containers and starts new ones in detached mode.

---

▎2. If updated images are available from Docker Hub or another registry

To download updated versions of the images, run:
```
docker-compose pull
```

And then start the containers (this can be combined with rebuilding if necessary):
```
docker-compose up -d
```

---

▎3. If you need to restart the containers (without rebuilding the images)

You can simply restart the services:
```
docker-compose restart
```

This command stops and restarts the containers without affecting the images, which is convenient if the changes involve, for example, environment variables (if they were passed via an env_file or Docker Compose variables).

---

▎4. Full restart (if necessary to remove old containers)

If you need to delete the old containers and perform some operations “from scratch”, you can:

1. Stop and remove the containers:
   ```
   docker-compose down
   ```

2. (Optional) Remove unused images and containers:
   ```
   docker system prune -f
   ```

3. Restart the containers:
   ```
   docker-compose up -d --build
   ```

---