# 1️⃣ Using `latest` instead of a specific version
FROM python:latest  

# 2️⃣ Running as root (bad practice)
USER root

# 3️⃣ No WORKDIR before running commands
RUN apt-get update
RUN apt-get install -y python3 python3-pip

# 4️⃣ Multiple `RUN` commands (should be combined)
RUN pip install flask
RUN pip install requests
RUN pip install numpy

# 5️⃣ Using `ADD` instead of `COPY` (bad for single files)
ADD app.py /app/app.py  

# 6️⃣ Exposing port but missing HEALTHCHECK
EXPOSE 5000

# 7️⃣ Running app without a non-root user
CMD ["python3", "/app/app.py"]
