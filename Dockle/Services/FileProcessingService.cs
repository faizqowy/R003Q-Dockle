using System;
using System.IO;
using Microsoft.Extensions.Logging;

namespace Dockle.Services;

public class FileProcessingService
{
    private readonly ILogger<FileProcessingService> _logger;

    public FileProcessingService(ILogger<FileProcessingService> logger)
    {
        _logger = logger;
    }

    public bool ValidateProjectStructure(string extractedPath)
    {
        var dockerComposePath = Path.Combine(extractedPath, "docker-compose.yaml");
        bool hasDockerCompose = File.Exists(dockerComposePath);

        _logger.LogInformation($"docker-compose.yaml found: {hasDockerCompose}");

        var folders = Directory.GetDirectories(extractedPath);
        var hasDockerfiles = false;

        _logger.LogInformation($"Found {folders.Length} folders in the extracted directory.");

        foreach (var folder in folders)
        {
            var dockerfilePath = Path.Combine(folder, "dockerfile");
            if (File.Exists(dockerfilePath))
            {
                hasDockerfiles = true;
                _logger.LogInformation($"Dockerfile found in: {folder}");
            }
            else
            {
                _logger.LogWarning($"No Dockerfile found in: {folder}");
            }
        }

        if(hasDockerfiles == false)
        {
            var dockerfileRootPath = Path.Combine(extractedPath, "dockerfile");
            if (File.Exists(dockerfileRootPath))
            {
                hasDockerfiles = true;
                _logger.LogInformation($"Dockerfile found in root: {dockerfileRootPath}");
            }
            else
            {
                _logger.LogWarning($"No Dockerfile found in root: {dockerfileRootPath}");
            }
        }

        // Check if there is at least one Dockerfile anywhere in the extracted directory
        if (!hasDockerCompose && !hasDockerfiles)
        {
            _logger.LogError("Invalid structure: No Dockerfile or docker-compose.yaml found.");
            return false;
        }

        _logger.LogInformation("Project structure validated successfully.");
        return true;
    }
}