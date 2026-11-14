# Submit one explicitly selected official land-cover request through cdsapi.
[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$Request,
    [Parameter(Mandatory)][string]$Destination,
    [string]$Python = 'python',
    [long]$MaxBytes = 1GB,
    [long]$MaxExtractedBytes = 4GB,
    [switch]$Execute
)
$ErrorActionPreference = 'Stop'
$requestPath = (Resolve-Path -LiteralPath $Request).ProviderPath
$inputRequest = Get-Content -LiteralPath $requestPath -Raw | ConvertFrom-Json -AsHashtable
if (@(Compare-Object @('variable','year','version','area') @($inputRequest.Keys)).Count) {
    throw 'Use the four official request fields in the sample.'
}
$years = @($inputRequest.year)
$year = [string]$years[0]
$area = @($inputRequest.area)
if ($inputRequest.year -isnot [array] -or $years.Count -ne 1 -or $year -notmatch '^\d{4}$' -or
    [int]$year -lt 2016 -or $inputRequest.version -ne 'v2_1_1' -or
    $inputRequest.variable -ne 'all' -or $area.Count -ne 4 -or
    $area[0] -le $area[2] -or $area[3] -le $area[1] -or
    $area[0] -gt 90 -or $area[2] -lt -90 -or $area[1] -lt -180 -or $area[3] -gt 180) {
    throw 'Invalid annual CDS request. Check the official form for this year and area.'
}
$dest = (Get-Item -LiteralPath (Resolve-Path -LiteralPath $Destination).ProviderPath).FullName
$repo = (Resolve-Path (Join-Path $PSScriptRoot '../../../../..')).ProviderPath
for ($parent = Get-Item -LiteralPath $dest; $null -ne $parent; $parent = $parent.Parent) {
    if ($parent -isnot [IO.DirectoryInfo] -or (($parent.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0)) {
        throw 'Use a canonical external destination without links.'
    }
}
if ($dest -eq $repo -or $dest.StartsWith($repo + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) {
    throw 'Use an external data directory.'
}
[pscustomobject]@{ product = 'C3S satellite-land-cover'; year = $year; version = '2.1.1'; area = $area } |
    ConvertTo-Json -Compress
if ($MaxBytes -le 0 -or $MaxExtractedBytes -le 0) { throw 'Positive transfer and extraction limits required.' }
if (-not $Execute) { return }
$helper = Join-Path $repo 'skills/data_acquisition/01_socioeconomic_natural_change/era5/scripts/copernicus_jobs.py'
$output = & $Python (Join-Path $PSScriptRoot 'get_cds_land_cover.py') $requestPath $dest $helper $MaxBytes $MaxExtractedBytes 2>$null
if ($LASTEXITCODE -ne 0) { throw 'CDS staging incomplete. Preserve cds-jobs and cds-cache before review or resume.' }
$result = $output | ConvertFrom-Json
if ($result.remote_status -in @('failed','dismissed','rejected','cancelled','canceled')) {
    throw 'CDS request ended without a result. Review the saved official request before proceeding.'
}
if ($result.status -ne 'downloaded') { throw 'CDS request pending. Resume the same request later; do not submit a duplicate.' }
$output
