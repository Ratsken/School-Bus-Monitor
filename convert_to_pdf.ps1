# Define output folder for PDFs and text files
$outputFolder = "D:\PROJECTS\Bus_management_system\bus_management\pdf_files"
New-Item -ItemType Directory -Path $outputFolder -Force | Out-Null

# Generate directory tree
$treeOutput = cmd /c "tree /F /A ." | Out-String

# Phase 1: Create combined text files
# -----------------------------------

# Create combined Python text file
$pythonTextFile = "$outputFolder\combined_python_files.txt"
"=== PROJECT DIRECTORY STRUCTURE ===`r`n$treeOutput`r`n=== PYTHON FILES ===`r`n" | Out-File -FilePath $pythonTextFile -Encoding utf8
Get-ChildItem -Path .\ -Recurse -Filter *.py | ForEach-Object {
    $fileContent = Get-Content $_.FullName -Raw
    "`r`n### File: $($_.FullName) ###`r`n$fileContent`r`n" | Out-File -Append -FilePath $pythonTextFile -Encoding utf8
}

# Create combined HTML text file
$htmlTextFile = "$outputFolder\combined_html_files.txt"
"=== PROJECT DIRECTORY STRUCTURE ===`r`n$treeOutput`r`n=== HTML FILES ===`r`n" | Out-File -FilePath $htmlTextFile -Encoding utf8
Get-ChildItem -Path .\ -Recurse -Filter *.html | ForEach-Object {
    $fileContent = Get-Content $_.FullName -Raw
    "`r`n### File: $($_.FullName) ###`r`n$fileContent`r`n" | Out-File -Append -FilePath $htmlTextFile -Encoding utf8
}

# Phase 2: Validate Text Files Before Conversion
# ----------------------------------

if (!(Test-Path $pythonTextFile) -or (Get-Content $pythonTextFile).Length -eq 0) {
    Write-Host "`n❌ Python text file is missing or empty. Check file merging."
    exit
}

if (!(Test-Path $htmlTextFile) -or (Get-Content $htmlTextFile).Length -eq 0) {
    Write-Host "`n❌ HTML text file is missing or empty. Check file merging."
    exit
}

# Phase 3: Convert text files to PDFs
# ----------------------------------
$pythonPdfOutput = "$outputFolder\combined_python_files.pdf"
$htmlPdfOutput = "$outputFolder\combined_html_files.pdf"

Write-Host "`nConverting text files to PDF..."
& wkhtmltopdf --enable-local-file-access "$pythonTextFile" "$pythonPdfOutput"
& wkhtmltopdf --enable-local-file-access "$htmlTextFile" "$htmlPdfOutput"
