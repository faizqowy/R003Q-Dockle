# ❌ Using 'latest' tag (bad practice)
FROM node:latest  

# ❌ Using root user (security risk)
USER root  

# ❌ Too many RUN commands (should be combined)
RUN apt-get update  
RUN apt-get install -y curl  
RUN apt-get install -y git  
RUN apt-get install -y vim  
RUN apt-get install -y unzip  

# ❌ Using ADD instead of COPY (unless extracting archives)
ADD myapp.tar.gz /app/  

# ❌ No HEALTHCHECK (recommended for production images)
WORKDIR /app  
COPY . .  
RUN npm install  

# ❌ Exposing too many ports (potential security issue)
EXPOSE 3000  
EXPOSE 8080  

CMD ["node", "server.js"]
