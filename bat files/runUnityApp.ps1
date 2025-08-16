# Path to your application
$exePath = "C:\Users\Exhibit\Desktop\Echoing Emotions\Echoing Emotions.exe"

while ($true) {
    Write-Host "Launching Unity application..."

    # Start the process and wait for it to exit
    $process = Start-Process -FilePath $exePath -PassThru

    $process.WaitForExit()

    Write-Host "Application exited at $(Get-Date). Restarting in 1 second..."

    Start-Sleep -Seconds 1
}
