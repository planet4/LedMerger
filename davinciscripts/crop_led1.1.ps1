# 1. Setup Backup
$BackupDir = ".\_ORIGINALS_BACKUP"
if (!(Test-Path $BackupDir)) { New-Item -ItemType Directory -Path $BackupDir }

# 2. Get files, excluding the backup folder
$Files = Get-ChildItem -Filter "*.mp4" | Where-Object { $_.FullName -notmatch "_ORIGINALS_BACKUP" }

foreach ($File in $Files) {
    $Name = $File.Name
    
    # Identify width by specifically looking for your known patterns
    if ($Name -match "192") { $W = 192 }
    elseif ($Name -match "576") { $W = 576 }
    elseif ($Name -match "1344") { $W = 1344 }
    elseif ($Name -match "1728") { $W = 1728 }
    else { continue }

    # CHECK HEIGHT: Use ffprobe to see if we even need to crop
    $CurrentHeight = & ffprobe -v error -select_streams v:0 -show_entries stream=height -of csv=p=0 "$($File.FullName)"
    
    if ([int]$CurrentHeight -eq 64) {
        Write-Host "SKIPPING: $Name is already 64px high." -ForegroundColor Yellow
        continue
    }

    # If height is less than 160, we can't use Y=96. We will center it instead.
    $Y_Offset = if ([int]$CurrentHeight -ge 160) { 96 } else { 0 }
    $X_Offset = if ($W -eq 192) { 32 } else { 0 }
    
    $TempName = "CROPPING_$Name"
    Write-Host "Cropping $Name ($W x 64) at Y=$Y_Offset..." -ForegroundColor Cyan

    # 3. Run FFmpeg
    & ffmpeg -i "$($File.FullName)" -vf "crop=${W}:64:${X_Offset}:${Y_Offset}" -c:v libx264 -crf 16 -pix_fmt yuv420p "$TempName" -y -loglevel error

    # 4. Finalize
    if ((Test-Path $TempName) -and ((Get-Item $TempName).Length -gt 0)) {
        Move-Item "$($File.FullName)" "$BackupDir\$Name" -Force
        Rename-Item "$TempName" "$Name"
        Write-Host "SUCCESS: $Name processed." -ForegroundColor Green
    } else {
        Write-Host "FAILED: $Name - Check if source is at least 64px tall." -ForegroundColor Red
    }
}
Read-Host "Done! Press Enter"