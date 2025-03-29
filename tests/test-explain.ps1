
try{
    $body = @{ query="departments of students?" } | ConvertTo-Json
    $response = Invoke-RestMethod `
    -Uri "http://127.0.0.1:5000/explain" `
    -Method Post `
    -Body $body `
    -ContentType "application/json"
    
    Write-Output $response

    $job_id = $response.job_id

    $response = Invoke-RestMethod `
    -Uri "http://127.0.0.1:5000/get-status/$job_id" `
    -Method Get `
    -ContentType "application/json"

    Write-Output $response

    while ($response.job_status -ne 'finished'){

        Write-Output "------------------------------------------------------"
        Write-Output $response
        Write-Output "------------------------------------------------------"
        Write-Output "Waiting for job $job_id to be finished."

        Start-Sleep -Milliseconds 50
        $response = Invoke-RestMethod `
            -Uri "http://127.0.0.1:5000/get-status/$job_id" `
            -Method Get `
            -ContentType "application/json"
        
    }

    Write-Output "Job $job_id finished."
    $response = Invoke-RestMethod `
        -Uri "http://127.0.0.1:5000/get-results/$job_id" `
        -Method Get `
        -ContentType "application/json"
    
    Write-Output $response


}
catch{
    $statusCode = $_.Exception
    Write-Output "request failed with status code : $_"
}

