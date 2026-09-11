# =========================================================
# crop_led.ps1
# Cropper DaVinci-exporterade mp4:er till ratt bredd/64px hojd
# for de fem LED-displayerna (Shortside/Longside/Media).
# =========================================================

# 1. Setup Backup
$BackupDir = ".\_ORIGINALS_BACKUP"
if (!(Test-Path $BackupDir)) { New-Item -ItemType Directory -Path $BackupDir | Out-Null }

# 2. Get files, excluding the backup folder
$Files = Get-ChildItem -Filter "*.mp4" | Where-Object { $_.FullName -notmatch "_ORIGINALS_BACKUP" }

foreach ($File in $Files) {
    $Name = $File.Name

    # Identify width by specifically looking for your known patterns
    if ($Name -match "192") { $W = 192 }
    elseif ($Name -match "576") { $W = 576 }
    elseif ($Name -match "1344") { $W = 1344 }
    elseif ($Name -match "1728") { $W = 1728 }
    else {
        Write-Host "SKIPPING: $Name matchar ingen kand bredd (192/576/1344/1728)." -ForegroundColor DarkYellow
        continue
    }

    # --- HEIGHT CHECK ---
    # ffprobe -of csv=p=0 kan i vissa fall ge flera rader (t.ex. tom sista rad).
    # Select-Object -First 1 + Trim() garanterar en enkel skalar, inte en array,
    # sa att [int]-castet inte kraschar.
    $RawHeight = & ffprobe -v error -select_streams v:0 -show_entries stream=height -of csv=p=0 "$($File.FullName)"
    $HeightLine = ($RawHeight | Select-Object -First 1)

    if ([string]::IsNullOrWhiteSpace($HeightLine)) {
        Write-Host "FAILED: $Name - kunde inte lasa hojd med ffprobe (ar filen korrupt/laskningsbar?)." -ForegroundColor Red
        continue
    }

    $CurrentHeight = [int]($HeightLine.Trim())

    if ($CurrentHeight -eq 64) {
        Write-Host "SKIPPING: $Name ar redan 64px hog." -ForegroundColor Yellow
        continue
    }

    # --- WIDTH CHECK ---
    # Se aven till att kallans bredd verkligen racker for maalbredden $W,
    # annars blir X-offseten fel / ffmpeg felar.
    $RawWidth = & ffprobe -v error -select_streams v:0 -show_entries stream=width -of csv=p=0 "$($File.FullName)"
    $WidthLine = ($RawWidth | Select-Object -First 1)
    $CurrentWidth = [int]($WidthLine.Trim())

    if ($CurrentWidth -lt $W) {
        Write-Host "FAILED: $Name - kallbredden ($CurrentWidth px) ar mindre an maalbredden ($W px)." -ForegroundColor Red
        continue
    }

    # If height is less than 160, we can't use Y=96. We will center it instead.
    if ($CurrentHeight -ge 160) {
        $Y_Offset = 96
    } else {
        # Centrera vertikalt i kallmaterialet istallet for ett fast varde
        $Y_Offset = [Math]::Max(0, [Math]::Floor(($CurrentHeight - 64) / 2))
    }

    # Centrera horisontellt om kallan ar bredare an maalbredden (inte bara for W=192)
    $X_Offset = [Math]::Max(0, [Math]::Floor(($CurrentWidth - $W) / 2))

    $TempName = "CROPPING_$Name"
    Write-Host "Cropping $Name ($W x 64) fran kalla ${CurrentWidth}x${CurrentHeight} vid X=$X_Offset Y=$Y_Offset..." -ForegroundColor Cyan

    # 3. Run FFmpeg
    & ffmpeg -i "$($File.FullName)" -vf "crop=${W}:64:${X_Offset}:${Y_Offset}" -c:v libx264 -crf 16 -pix_fmt yuv420p "$TempName" -y -loglevel error

    # 4. Finalize
    if ((Test-Path $TempName) -and ((Get-Item $TempName).Length -gt 0)) {
        Move-Item "$($File.FullName)" "$BackupDir\$Name" -Force
        Rename-Item "$TempName" "$Name"
        Write-Host "SUCCESS: $Name processad." -ForegroundColor Green
    } else {
        Write-Host "FAILED: $Name - Kontrollera att kallan ar minst 64px hog och att ffmpeg kunde skriva utfilen." -ForegroundColor Red
        if (Test-Path $TempName) { Remove-Item $TempName -Force }
    }
}

Read-Host "Done! Press Enter"
