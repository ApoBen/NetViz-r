Write-Host "======================================" -ForegroundColor Cyan
Write-Host "     🌐 NetVizör Kurulum Sihirbazı" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan

$HasPython = [bool](Get-Command "python" -ErrorAction SilentlyContinue)
if ($HasPython) {
    $PyTest = python --version 2>&1
    if ($null -eq $PyTest -or $PyTest -like "*not recognized*" -or $PyTest.Length -eq 0) {
        $HasPython = $false
    }
}

if (-not $HasPython) {
    Write-Host "[*] Python bulunamadi. Python otomatik olarak indiriliyor..." -ForegroundColor Yellow
    $Installer = "$env:TEMP\python_install.exe"
    Invoke-WebRequest -UseBasicParsing -Uri "https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe" -OutFile $Installer
    Write-Host "[+] Python arka planda kuruluyor, lutfen bekleyin..." -ForegroundColor Green
    Start-Process -FilePath $Installer -ArgumentList "/quiet PrependPath=1" -Wait
    Remove-Item $Installer -Force
    
    # PATH degiskenlerini guncelle
    $env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [Environment]::GetEnvironmentVariable("Path", "User")
    $PythonUserPath = "$env:LOCALAPPDATA\Programs\Python\Python311"
    if (Test-Path $PythonUserPath) {
        $env:Path += ";$PythonUserPath;$PythonUserPath\Scripts"
    }
    
    if (-not (Get-Command "python" -ErrorAction SilentlyContinue)) {
        Write-Host "[!] Hata: Python kurulmaya calisildi ancak sistem yolunda (PATH) algilanamadi. Lutfen bilgisayarinizi yeniden baslatin." -ForegroundColor Red
        Read-Host "Cikmak icin Enter tusuna basin..."
        return
    }
}
$HasGit = [bool](Get-Command "git" -ErrorAction SilentlyContinue)

$InstallDir = "$env:USERPROFILE\.netvizor"

if ($HasGit) {
    if (Test-Path $InstallDir) {
        Write-Host "[+] Eski kurulum guncelleniyor (Git)..." -ForegroundColor Green
        Set-Location $InstallDir
        git pull origin main
    } else {
        Write-Host "[+] NetVizör indiriliyor (Git)..." -ForegroundColor Green
        git clone https://github.com/ApoBen/netvizor.git $InstallDir
        Set-Location $InstallDir
    }
} else {
    Write-Host "[*] Git bulunamadi. Proje ZIP olarak indiriliyor..." -ForegroundColor Yellow
    
    $ZipPath = "$env:TEMP\netvizor.zip"
    $ExtractPath = "$env:TEMP\netvizor_extracted"
    
    if (Test-Path $ExtractPath) { 
        Remove-Item -Recurse -Force $ExtractPath | Out-Null 
    }
    
    Write-Host "[+] ZIP dosyasi indiriliyor..." -ForegroundColor Green
    Invoke-WebRequest -UseBasicParsing -Uri "https://github.com/ApoBen/netvizor/archive/refs/heads/main.zip" -OutFile $ZipPath
    
    Write-Host "[+] ZIP dosyasi ayiklaniyor..." -ForegroundColor Green
    Expand-Archive -Path $ZipPath -DestinationPath $ExtractPath -Force
    
    if (-not (Test-Path $InstallDir)) { 
        New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null 
    }
    
    Write-Host "[+] Dosyalar kopyalaniyor..." -ForegroundColor Green
    Copy-Item -Path "$ExtractPath\netvizor-main\*" -Destination $InstallDir -Recurse -Force
    
    # Temizlik
    Remove-Item -Path $ZipPath -Force
    Remove-Item -Recurse -Force $ExtractPath
    
    Set-Location $InstallDir
}

Write-Host "[+] Sanal ortam (venv) olusturuluyor ve bagimliliklar yukleniyor..." -ForegroundColor Green
python -m venv venv
.\venv\Scripts\python.exe -m pip install --upgrade pip | Out-Null
.\venv\Scripts\pip.exe install -r requirements.txt | Out-Null

Write-Host "[+] Global calistirici (netvizor) ayarlaniyor..." -ForegroundColor Green
$BinDir = "$env:USERPROFILE\.netvizor\bin"
if (-not (Test-Path $BinDir)) { New-Item -ItemType Directory -Force -Path $BinDir | Out-Null }

$WrapperScript = "@echo off`ncd /d `"$InstallDir`"`ncall run.bat %*"
Set-Content -Path "$BinDir\netvizor.bat" -Value $WrapperScript -Encoding Ascii

# Safely add to User PATH
$UserPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($UserPath -notlike "*$BinDir*") {
    $NewPath = if ($UserPath) { $UserPath + (if ($UserPath.EndsWith(";")) {""} else {";"}) + $BinDir } else { $BinDir }
    [Environment]::SetEnvironmentVariable("Path", $NewPath, "User")
    $env:Path = $env:Path + ";" + $BinDir
    Write-Host "[*] PATH degiskeni guncellendi." -ForegroundColor Yellow
}

Write-Host "[+] Kurulum basariyla tamamlandi! 🎉" -ForegroundColor Green
Write-Host "Artik PowerShell veya CMD ekraninda sadece 'netvizor' yazarak baslatabilirsiniz." -ForegroundColor White
