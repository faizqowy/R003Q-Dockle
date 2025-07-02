# Use the official .NET SDK image as the build environment
FROM mcr.microsoft.com/dotnet/sdk:9.0 AS build

# Set the working directory inside the container
WORKDIR /app

# Copy the project file and restore any dependencies (via NuGet)
COPY *.csproj ./
RUN dotnet restore

# Copy the rest of the application code
COPY . ./

ENV ASPNETCORE_URLS=http://+:5167

# Publish the application to the /out directory in the container
RUN dotnet publish -c Release -o /out

# Use the official .NET runtime image for the final image
FROM mcr.microsoft.com/dotnet/aspnet:9.0 AS base

# Set the working directory inside the container
WORKDIR /app

# Copy the published application from the build environment
COPY --from=build /out .

# Expose the port the app runs on (change to your app's port if different)
EXPOSE 8080

# Set the entry point for the application
ENTRYPOINT ["dotnet", "Dockle.dll"]
