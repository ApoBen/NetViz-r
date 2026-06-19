Write-Host "======================================" -ForegroundColor Cyan
Write-Host "     🌐 NetVizör Kurulum Sihirbazı" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan

if (-not (Get-Command "python" -ErrorAction SilentlyContinue)) {
    Write-Host "[!] Hata: Python bulunamadi. Lutfen indirip kurun." -ForegroundColor Red
    Read-Host "Cikmak icin Enter tusuna basin..."
    return
}
if (-not (Get-Command "git" -ErrorAction SilentlyContinue)) {
    Write-Host "[!] Hata: Git bulunamadi. Lutfen indirip kurun." -ForegroundColor Red
    Read-Host "Cikmak icin Enter tusuna basin..."
    return
}

$InstallDir = "$env:USERPROFILE\.netvizor"
if (Test-Path $InstallDir) {
    Write-Host "[+] Eski kurulum guncelleniyor..." -ForegroundColor Green
    Set-Location $InstallDir
    git pull origin main
} else {
    Write-Host "[+] NetVizör indiriliyor..." -ForegroundColor Green
    git clone https://github.com/ApoBen/NetViz-r.git $InstallDir
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
Set-Content -Path "$BinDir\netvizor.bat" -Value $WrapperScript -Encoding UTF8

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
