using System;
using System.Diagnostics;
using System.IO;
using System.IO.Compression;
using System.Linq;
using System.Collections.Generic;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;
using Dockle.Models;
using Dockle.Services;

namespace Dockle.Controllers;

[ApiController]
[Route("scanner")]
public class ScannerController : Controller
{
    private readonly ILogger<ScannerController> _logger;
    private readonly FileProcessingService _fileProcessingService;

    public ScannerController(ILogger<ScannerController> logger, FileProcessingService fileProcessingService)
    {
        _fileProcessingService = fileProcessingService;
        _logger = logger;
    }

    [HttpGet]
    public IActionResult Index()
    {
        return View();
    }

    [HttpPost("upload-zip")]
    public IActionResult Scan(IFormFile file)
    {
        if (file == null || file.Length == 0){
            return BadRequest("No file uploaded.");
        }

        if (file.ContentType != "application/zip"){
            return BadRequest("Invalid file type. Please upload a zip file.");
        }

        try{
            var uploadPath = Path.Combine(Directory.GetCurrentDirectory(), "uploads");
            if (!Directory.Exists(uploadPath)){
                Directory.CreateDirectory(uploadPath);
            }

            var filePath = Path.Combine(uploadPath, file.FileName);
            using (var stream = new FileStream(filePath, FileMode.Create)){
                file.CopyTo(stream);
            }

            _logger.LogInformation($"File saved to: {filePath}");

            // Extract the zip file
            var extractedPath = Path.Combine(uploadPath, Path.GetFileNameWithoutExtension(file.FileName));
            if (Directory.Exists(extractedPath)){
                Directory.Delete(extractedPath, true);
            }

            ZipFile.ExtractToDirectory(filePath, extractedPath);
            _logger.LogInformation($"File extracted to: {extractedPath}");

            // Step 2: Validate Project Structure
            if (!_fileProcessingService.ValidateProjectStructure(extractedPath)){
                return BadRequest("Invalid project structure. Check logs for details.");
            }

            // Step 3: Check for Docker Smells
            var smellResults = _fileProcessingService.CheckDockerSmells(extractedPath);

            // Step 4: Optimize docker-compose.yaml
            var dockerComposePath = Path.Combine(extractedPath, "docker-compose.yaml");
            var optimizationResults = _fileProcessingService.OptimizeDockerCompose(dockerComposePath);

            // Log the results
            foreach (var entry in smellResults){
                _logger.LogInformation($"Dockerfile: {entry.Key}");
                foreach (var warning in entry.Value)
                {
                    _logger.LogWarning(warning);
                }
            }

            foreach (var optimization in optimizationResults)
            {
                _logger.LogInformation(optimization);
            }

            return Ok(new { message = "File uploaded and analyzed successfully.", Dockerfile = smellResults, Dockercompose = optimizationResults });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error processing the uploaded file.");
            return StatusCode(500, "Internal server error while processing the file.");
        }
    }

    [ResponseCache(Duration = 0, Location = ResponseCacheLocation.None, NoStore = true)]
    public IActionResult Error()
    {
        return View(new ErrorViewModel { RequestId = Activity.Current?.Id ?? HttpContext.TraceIdentifier });
    }
}
