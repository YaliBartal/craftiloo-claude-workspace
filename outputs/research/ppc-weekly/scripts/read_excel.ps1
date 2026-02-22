$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$workbook = $excel.Workbooks.Open("c:\temp\catalog.xlsx")
$sheet = $workbook.Sheets.Item(1)
$usedRange = $sheet.UsedRange
$rows = $usedRange.Rows.Count
$cols = $usedRange.Columns.Count
for($r=1; $r -le $rows; $r++) {
    $line = ""
    for($c=1; $c -le $cols; $c++) {
        $cell = $sheet.Cells.Item($r,$c).Text
        $line += $cell + "|"
    }
    Write-Output $line
}
$workbook.Close($false)
$excel.Quit()
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel) | Out-Null
