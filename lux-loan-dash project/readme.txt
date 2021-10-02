1. Download the tar file (dash-app.tar). Place it in your working directory.
    If not sure where you working directory is:
    in mac - go to terminal and type pwd

2. Navigate to your working directory via your terminal:
    cd ~

3. Start up docker or install it if not already installed, from: https://docs.docker.com/get-docker/

4. In your terminal, type:
    docker load < dash-app.tar

5. To check that the image has been loaded properly, in your terminal, type:
    docker images

   You should see that the dash-app repository has been listed

6. To run the docker image, go to terminal, type:
    docker run -d -p 8000:8000 --name dashboard  dash-app

    Open up your web browser and type: http://127.0.0.1:8000/

The dashboard should load and 3 visualisation charts will be seen.

7. To stop it, close the browser tab/window. In your terminal, type docker stop dashboard

   To confirm that the container has stopped, in your terminal, type:
     docker ps

   The container named ‘dashboard’ should not be seen in the list of running processes.
