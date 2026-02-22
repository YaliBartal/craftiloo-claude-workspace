# Convert all .xlsx files in current directory to .csv
Get-ChildItem -Filter '*.xlsx' | ForEach-Object {
    $excel = New-Object -ComObject Excel.Application
    $excel.Visible = $false
    $excel.DisplayAlerts = $false

    $workbook = $excel.Workbooks.Open($_.FullName)
    $csvPath = $_.FullName -replace '\.xlsx$', '.csv'

    # Save as CSV (format code 6 = xlCSV)
    $workbook.SaveAs($csvPath, 6)
    $workbook.Close($false)
    $excel.Quit()

    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel) | Out-Null

    Write-Host "Converted: $($_.Name) -> $([System.IO.Path]::GetFileName($csvPath))"
}

Write-Host "`nConversion complete!"
