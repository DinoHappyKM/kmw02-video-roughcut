param([string]$DestinationRoot = (Join-Path $env:LOCALAPPDATA 'KMW02AIEditing\0.1.0'), [string]$CodexPath, [switch]$PrepareOnly)
$ErrorActionPreference = 'Stop'
function Read-Sha256([string]$LiteralPath) {
    $stream = [IO.File]::OpenRead($LiteralPath)
    $algorithm = [Security.Cryptography.SHA256]::Create()
    try { return ([BitConverter]::ToString($algorithm.ComputeHash($stream))).Replace('-','').ToLowerInvariant() }
    finally { $stream.Dispose(); $algorithm.Dispose() }
}
$sourceRoot = [IO.Path]::GetFullPath($PSScriptRoot)
$marketRoot = [IO.Path]::GetFullPath($DestinationRoot)
$targetRoot = Join-Path $marketRoot 'plugins\kmw02-ai-editing'
if ($marketRoot.StartsWith($sourceRoot + '\', [StringComparison]::OrdinalIgnoreCase) -or $marketRoot -eq $sourceRoot) { throw '安裝位置不可在來源套件內。' }
$manifest = Get-Content -LiteralPath (Join-Path $sourceRoot 'plugin.json') -Raw -Encoding UTF8 | ConvertFrom-Json
if ($manifest.name -ne 'kmw02-ai-editing' -or $manifest.version -ne '0.1.0') { throw '套件身分或版本不符。' }
$hashes = Get-Content -LiteralPath (Join-Path $sourceRoot 'SHA256SUMS.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$expectedNames = @('SHA256SUMS.json') + @($hashes.PSObject.Properties.Name)
$actualNames = @(Get-ChildItem -LiteralPath $sourceRoot -File -Recurse -Force | ForEach-Object { $_.FullName.Substring($sourceRoot.Length + 1).Replace('\','/') })
if (@(Compare-Object $expectedNames $actualNames).Count -ne 0) { throw '套件有缺檔或額外檔案，請重新解壓縮。' }
foreach ($property in $hashes.PSObject.Properties) {
    $relative = $property.Name
    $source = [IO.Path]::GetFullPath((Join-Path $sourceRoot $relative))
    if (-not $source.StartsWith($sourceRoot + '\', [StringComparison]::OrdinalIgnoreCase)) { throw '非法套件路徑。' }
    if ((Read-Sha256 $source) -ne $property.Value) { throw "來源校驗失敗：$relative" }
}
$market = [ordered]@{
    name = 'kmw02-ai-editing-local'
    interface = @{displayName='黃嘉偉KMW02AI剪輯'}
    plugins = @(@{name='kmw02-ai-editing'; source=@{source='local';path='./plugins/kmw02-ai-editing'};policy=@{installation='AVAILABLE';authentication='ON_INSTALL'};category='Productivity'})
}
$marketJson = $market | ConvertTo-Json -Depth 10
$catalogPath = Join-Path $marketRoot '.agents\plugins\marketplace.json'
if (Test-Path -LiteralPath $catalogPath) {
    $existing = Get-Content -LiteralPath $catalogPath -Raw -Encoding UTF8 | ConvertFrom-Json | ConvertTo-Json -Depth 10
    if ($existing -ne $marketJson) { throw '安裝位置已有不同目錄，保留原檔；請指定新的 DestinationRoot。' }
}
foreach ($relative in $actualNames) {
    $dest = Join-Path $targetRoot $relative
    if (Test-Path -LiteralPath $dest) {
        if (-not (Test-Path -LiteralPath $dest -PathType Leaf)) { throw "目的地不是檔案：$dest" }
        if ((Read-Sha256 $dest) -ne (Read-Sha256 (Join-Path $sourceRoot $relative))) { throw "已有不同內容，保留原檔：$dest" }
    }
}
if (-not $PrepareOnly) {
    if (-not $CodexPath) {
        $found = Get-Command codex -ErrorAction SilentlyContinue
        if ($found) { $CodexPath = $found.Source }
        else {
            $binRoot = Join-Path $env:LOCALAPPDATA 'OpenAI\Codex\bin'
            $candidate = Get-ChildItem -LiteralPath $binRoot -Filter codex.exe -Recurse -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 1
            if ($candidate) { $CodexPath = $candidate.FullName }
        }
    }
    if (-not $CodexPath -or -not (Test-Path -LiteralPath $CodexPath -PathType Leaf)) { throw '找不到 Codex CLI，請安裝桌面版或以 -CodexPath 指定 codex.exe。' }
}
foreach ($relative in $actualNames) {
    $dest = Join-Path $targetRoot $relative
    [IO.Directory]::CreateDirectory([IO.Path]::GetDirectoryName($dest)) | Out-Null
    if (-not (Test-Path -LiteralPath $dest)) { Copy-Item -LiteralPath (Join-Path $sourceRoot $relative) -Destination $dest }
    if ((Read-Sha256 $dest) -ne (Read-Sha256 (Join-Path $sourceRoot $relative))) { throw "安裝校驗失敗：$relative" }
}
[IO.Directory]::CreateDirectory([IO.Path]::GetDirectoryName($catalogPath)) | Out-Null
[IO.File]::WriteAllText($catalogPath, $marketJson, (New-Object Text.UTF8Encoding($false)))
if ($PrepareOnly) { Write-Output "檔案與本機來源已準備：$marketRoot"; return }
& $CodexPath plugin marketplace add $marketRoot --json
if ($LASTEXITCODE -ne 0) { throw '註冊外掛來源失敗；已保留檔案供排查。' }
& $CodexPath plugin add 'kmw02-ai-editing@kmw02-ai-editing-local' --json
if ($LASTEXITCODE -ne 0) { throw '外掛安裝未完成；請保留上方錯誤並由外掛目錄檢查。' }
Write-Output '安裝命令已完成。重新啟動桌面版，選取「黃嘉偉KMW02AI剪輯」，輸入0驗證主選單。'
