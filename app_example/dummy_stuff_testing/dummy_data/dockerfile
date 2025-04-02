# ✅ Pinning a specific Node.js version
FROM node:18-alpine  

# ✅ Creating a non-root user
RUN addgroup -S appgroup && adduser -S appuser -G appgroup  
USER appuser  

# ✅ Combining RUN commands to reduce layers
RUN apk add --no-cache curl git vim unzip  

# ✅ Using COPY instead of ADD
COPY myapp.tar.gz /app/  

# ✅ Adding a HEALTHCHECK
HEALTHCHECK --interval=30s --timeout=10s \
  CMD curl -f http://localhost:3000 || exit 1  

WORKDIR /app  
COPY . .  
RUN npm install  

# ✅ Minimizing exposed ports
EXPOSE 3000  

CMD ["node", "server.js"]
