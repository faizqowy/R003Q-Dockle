using System.Diagnostics;
using Microsoft.AspNetCore.Mvc;
using Dockle.Models;

namespace Dockle.Controllers;

[ApiController]
[Route("scanner")]
public class ScannerController : Controller
{
    private readonly ILogger<ScannerController> _logger;

    public ScannerController(ILogger<ScannerController> logger)
    {
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
        if (file == null || file.Length == 0)
        {
            return BadRequest("No file uploaded.");
        }

        if (file.ContentType != "application/zip")
        {
            return BadRequest("Invalid file type. Please upload a zip file.");
        }

        try{
            using (var stream = new MemoryStream())
            {
                file.CopyTo(stream);
                _logger.LogInformation($"Uploaded file: {file.FileName}, Size: {file.Length} bytes");
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error processing the uploaded file.");
            return StatusCode(500, "Internal server error while processing the file.");
        }

        return Ok("File uploaded successfully.");
    }

    [ResponseCache(Duration = 0, Location = ResponseCacheLocation.None, NoStore = true)]
    public IActionResult Error()
    {
        return View(new ErrorViewModel { RequestId = Activity.Current?.Id ?? HttpContext.TraceIdentifier });
    }
}
