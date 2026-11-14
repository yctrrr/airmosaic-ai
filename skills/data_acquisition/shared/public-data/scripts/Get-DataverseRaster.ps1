# Locate versioned public Dataverse files and verify annual single-TIFF archives.
[CmdletBinding()]
param(
    [Parameter(Mandatory)][int[]]$Years,
    [ValidateSet('Catalog','Download')][string]$Action = 'Catalog',
    [string]$Destination,
    [string]$Doi = '10.7910/DVN/YGIVCD',
    [string]$FilePattern = '{year}_Version2.zip',
    [long]$MaxArchiveBytes = 150MB,
    [long]$MaxExtractedBytes = 20GB,
    [string]$FixtureCatalog,
    [string]$CatalogVersion = 'latest',
    [int]$TimeoutSeconds = 300
)
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
if (($Years | Where-Object { $_ -lt 1900 -or $_ -gt 2199 }) -or ($Years | Sort-Object -Unique).Count -ne $Years.Count) {
    throw 'Provide distinct four-digit years.'
}
$origin = 'https://dataverse.harvard.edu'
if ($Doi -notmatch '^10[.][0-9]{4,9}/[A-Za-z0-9.\-_/]+$' -or
    $FilePattern -cnotmatch '^[a-zA-Z0-9._-]*\{year\}[a-zA-Z0-9._-]*[.]zip$') { throw 'Invalid DOI or annual ZIP naming pattern.' }
$datasetDoi = 'doi:' + $Doi
if ($FixtureCatalog -and $Doi -ne '10.0000/SYNTHETIC') { throw 'Fixture catalogs require the synthetic dataset identifier.' }
if ($MaxArchiveBytes -le 0 -or $MaxExtractedBytes -le 0) { throw 'Invalid archive or extraction limit.' }
$escapedDoi = [uri]::EscapeDataString($datasetDoi)
function Read-DataverseMetadata([string]$Uri) {
    try {
        $response = Invoke-WebRequest -Uri $Uri -TimeoutSec 40
        if ($response.StatusCode -ne 200 -or $response.Headers['Content-Type'] -notmatch 'application/json') { throw 'Metadata unavailable.' }
        $body = $response.Content | ConvertFrom-Json
        if ($body.status -ne 'OK' -or -not $body.data) { throw 'Metadata unavailable.' }
        $body.data
    } catch {
        throw 'Dataverse did not return valid dataset metadata. Retain verified files and retry the same catalog later.'
    }
}
if ($FixtureCatalog) {
    $version = Get-Content -LiteralPath $FixtureCatalog -Raw | ConvertFrom-Json
} elseif ($CatalogVersion -eq 'latest') {
    $uri = "$origin/api/datasets/:persistentId/?persistentId=$escapedDoi"
    $version = (Read-DataverseMetadata $uri).latestVersion
} else {
    if ($CatalogVersion -notmatch '^\d+\.\d+$') { throw 'Use a published Dataverse version number.' }
    $uri = "$origin/api/datasets/:persistentId/versions/$CatalogVersion" + "?persistentId=$escapedDoi"
    $version = Read-DataverseMetadata $uri
}
$versionName = "$($version.versionNumber).$($version.versionMinorNumber)"
if ($CatalogVersion -ne 'latest' -and $versionName -ne $CatalogVersion) { throw 'Catalog version differs from the requested release.' }
if ($version.versionState -ne 'RELEASED') { throw 'A published Dataverse dataset version is required.' }
$rows = foreach ($year in ($Years | Sort-Object)) {
    $matchesForYear = @($version.files | Where-Object {
        -not $_.restricted -and $_.label -ceq $FilePattern.Replace('{year}',[string]$year)
    })
    if ($matchesForYear.Count -gt 1) { throw "Ambiguous annual archive for $year." }
    $file = if ($matchesForYear.Count -eq 1) { $matchesForYear[0] } else { $null }
    [pscustomobject]@{
        year = $year
        product = $(if ($FixtureCatalog) { 'synthetic' } else { 'Harvard Dataverse' })
        doi = $datasetDoi
        catalog_version = $versionName
        label = $file.label
        file_id = $file.dataFile.id
        bytes = $file.dataFile.filesize
        checksum_type = $file.dataFile.checksum.type
        checksum = $file.dataFile.checksum.value
        status = if ($file) { 'listed' } else { 'unavailable' }
    }
}
if ($versionName -notmatch '^\d+\.\d+$') { throw 'Invalid catalog version metadata.' }
if ($Action -eq 'Catalog') {
    ConvertTo-Json -InputObject @($rows) -Depth 6
    return
}
if (@($rows | Where-Object status -ne 'listed').Count) { throw 'Requested annual archive is unavailable.' }
if (-not $Destination) { throw 'Destination must be an existing directory outside the repository.' }
$repo = (Resolve-Path (Join-Path $PSScriptRoot '../../../../..')).ProviderPath
$dest = (Get-Item -LiteralPath (Resolve-Path -LiteralPath $Destination).ProviderPath).FullName
# Reject directory links and junctions on the path, including an external alias into Git.
for ($parent = Get-Item -LiteralPath $dest; $null -ne $parent; $parent = $parent.Parent) {
    if ($parent -isnot [IO.DirectoryInfo] -or (($parent.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0)) {
        throw 'Use a canonical external destination without links.'
    }
}
if ($dest -eq $repo -or $dest.StartsWith($repo + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) {
    throw 'Use an external data directory.'
}

foreach ($row in $rows) {
    $algorithm = ($row.checksum_type -replace '-', '').ToUpperInvariant()
    if ($algorithm -notin @('MD5','SHA1','SHA256','SHA512') -or -not $row.checksum -or $row.bytes -le 0 -or $row.bytes -gt $MaxArchiveBytes -or $row.file_id -le 0) {
        throw "Provider checksum or byte count missing for $($row.year)."
    }
    $key = '{0}-dataverse-{1}-{2}' -f $row.year,$versionName,$row.file_id
    $final = Join-Path $dest $key
    if (Test-Path -LiteralPath $final) {
        $folder = Get-Item -LiteralPath $final
        if (-not $folder.PSIsContainer -or (($folder.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0)) {
            throw 'Existing acquisition folder redirects.'
        }
        $receipt = Get-Content -LiteralPath (Join-Path $final 'source.json') -Raw | ConvertFrom-Json
        $zip = Join-Path $final $row.label
        $tif = Join-Path $final 'source.tif'
        if ($receipt.doi -ne $datasetDoi -or $receipt.year -ne $row.year -or $receipt.file_id -ne $row.file_id -or (Get-Item -LiteralPath $zip).Length -ne $row.bytes -or
            (Get-FileHash -LiteralPath $zip -Algorithm $algorithm).Hash -ne $row.checksum -or
            (Get-FileHash -LiteralPath $tif).Hash -ne $receipt.sha256) {
            throw 'Existing download does not match its receipt.'
        }
        Write-Output $final
        continue
    }
    $pending = Join-Path $dest ('.download-' + [Guid]::NewGuid().ToString('N'))
    [IO.Directory]::CreateDirectory($pending) | Out-Null
    try {
        $zip = Join-Path $pending $row.label
        $tif = Join-Path $pending 'source.tif'
        try {
            if ($FixtureCatalog) {
                $fixtureZip = Join-Path (Split-Path -Parent (Resolve-Path -LiteralPath $FixtureCatalog).ProviderPath) $row.label
                [IO.File]::Copy($fixtureZip, $zip)
            } else {
                & curl.exe --fail --silent --show-error --location --proto '=https' --proto-redir '=https' --retry 1 --max-time $TimeoutSeconds --max-filesize $MaxArchiveBytes --output $zip "$origin/api/access/datafile/$($row.file_id)?format=original" 2>$null
                if ($LASTEXITCODE -ne 0) { throw 'Transfer failed.' }
            }
        } catch {
            throw "Dataverse download failed for $($row.year)."
        }
        if ((Get-Item -LiteralPath $zip).Length -ne $row.bytes -or
            (Get-FileHash -LiteralPath $zip -Algorithm $algorithm).Hash -ne $row.checksum) {
            throw 'Dataverse archive fails provider size or checksum.'
        }
        $archive = [IO.Compression.ZipFile]::OpenRead($zip)
        try {
            $members = @($archive.Entries | Where-Object { $_.Name -match '\.tiff?$' })
            if ($members.Count -ne 1 -or $members[0].Length -le 0 -or $members[0].Length -gt $MaxExtractedBytes) {
                throw 'Expected exactly one TIFF within the extraction budget.'
            }
            # Stream just the selected member to a fixed filename.
            [IO.Compression.ZipFileExtensions]::ExtractToFile($members[0], $tif, $false)
            if ((Get-Item -LiteralPath $tif).Length -ne $members[0].Length) { throw 'Extracted TIFF size differs.' }
        } finally {
            $archive.Dispose()
        }
        [pscustomobject]@{
            product = $row.product
            doi = $datasetDoi
            year = $row.year
            version = $versionName
            file_id = $row.file_id
            provider_checksum = $row.checksum
            checksum_type = $algorithm
            archive_bytes = $row.bytes
            path = 'source.tif'
            sha256 = (Get-FileHash -LiteralPath $tif).Hash.ToLowerInvariant()
        } | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $pending 'source.json') -Encoding utf8NoBOM
        [IO.Directory]::Move($pending, $final)
        Write-Output $final
    } finally {
        if ([IO.Directory]::Exists($pending)) {
            # Only these three literal files can have been created in this staging directory.
            foreach ($name in @($row.label,'source.tif','source.json')) {
                $stagedFile = Join-Path $pending $name
                if ([IO.File]::Exists($stagedFile)) { [IO.File]::Delete($stagedFile) }
            }
            [IO.Directory]::Delete($pending)
        }
    }
}
