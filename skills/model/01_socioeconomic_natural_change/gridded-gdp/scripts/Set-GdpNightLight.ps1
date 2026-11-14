# Write a new GDP configuration referencing an existing Dataverse crop.
[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$Config,
    [Parameter(Mandatory)][int]$Year,
    [Parameter(Mandatory)][string]$CropDirectory,
    [Parameter(Mandatory)][string]$OutputConfig
)
$ErrorActionPreference = 'Stop'
$cfg = Get-Content -LiteralPath $Config -Raw | ConvertFrom-Json -AsHashtable
$crop = (Resolve-Path -LiteralPath $CropDirectory).ProviderPath
$source = Get-Content -LiteralPath (Join-Path $crop 'source.json') -Raw | ConvertFrom-Json -AsHashtable
$key = [string]$Year
if ($cfg.mode -notin @('synthetic','authorized') -or -not $cfg.annual -or -not $cfg.annual.Contains($key)) {
    throw 'Select an existing annual row in a synthetic or authorized GDP config.'
}
if ($source.year -ne $Year -or $source.verified -ne $true -or $source.path -cne 'crop.tif' -or -not $source.version) {
    throw 'Select the source receipt of a verified crop for this year.'
}
if (($cfg.mode -eq 'synthetic' -and $source.product -ne 'synthetic') -or
    ($cfg.mode -eq 'authorized' -and ($source.product -ne 'Harvard Dataverse' -or $source.doi -ne 'doi:10.7910/DVN/YGIVCD'))) {
    throw 'The annual light product does not match the workflow mode.'
}
$bounds = @($cfg.geo.extent)
$extent = @($source.extent)
$tol = 1e-8
if ($bounds.Count -ne 4 -or $extent.Count -ne 4 -or
    $extent[0] -gt $bounds[0] + $tol -or $extent[1] -lt $bounds[1] - $tol -or
    $extent[2] -gt $bounds[2] + $tol -or $extent[3] -lt $bounds[3] - $tol) {
    throw 'The cropped raster does not cover the configured GDP extent.'
}
$tif = Join-Path $crop 'crop.tif'
if (-not (Test-Path -LiteralPath $tif -PathType Leaf)) { throw 'Crop TIFF is missing.' }
$dest = [IO.Path]::GetFullPath($OutputConfig)
for ($folder = [IO.DirectoryInfo]::new((Split-Path -Parent $dest)); $null -ne $folder; $folder = $folder.Parent) {
    if (-not $folder.Exists -or ($folder.Attributes -band [IO.FileAttributes]::ReparsePoint) -or
        (Test-Path -LiteralPath (Join-Path $folder.FullName '.git'))) { throw 'Use an existing external output folder without links.' }
}
$cfg.annual[$key].light = $source
$cfg.annual[$key].light.path = $tif
$bytes = [Text.Encoding]::UTF8.GetBytes(($cfg | ConvertTo-Json -Depth 30) + [Environment]::NewLine)
$stream = [IO.File]::Open($dest,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None)
try { $stream.Write($bytes,0,$bytes.Length) } finally { $stream.Dispose() }
$dest
