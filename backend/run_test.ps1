Start-Process python -ArgumentList "-m uvicorn app.main:app" -NoNewWindow
Start-Sleep -Seconds 5
$response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/pipeline/upload?use_sample=true" -Method Post
Write-Host "Task: $($response.task_id)"
Start-Sleep -Seconds 15
Get-Process -Name "python" | Stop-Process -Force
