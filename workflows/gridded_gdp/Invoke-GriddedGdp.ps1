# Compose the public-data and GDP skills in a fresh external run directory.
[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$RunDirectory,
    [string]$Config,
    [ValidateSet('synthetic','authorized')][string]$Mode = 'synthetic',
    [switch]$Append,
    [switch]$Resume,
    [string]$Rscript = 'Rscript'
)
$ErrorActionPreference = 'Stop'
if ($Mode -eq 'synthetic' -and $Config) { throw 'Synthetic mode generates its own config.' }
$repo = (Resolve-Path (Join-Path $PSScriptRoot '../..')).ProviderPath
$model = Join-Path $repo 'skills/model/01_socioeconomic_natural_change/gridded-gdp/scripts'
$acquisition = Join-Path $repo 'skills/data_acquisition/shared/public-data/scripts'
$run = [IO.Path]::GetFullPath($RunDirectory)
if ($run.TrimEnd('\','/') -eq $repo -or $run.StartsWith($repo + [IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase)) {
    throw 'Choose an external sandbox result directory.'
}
for ($parent = [IO.DirectoryInfo]::new($run); $null -ne $parent; $parent = $parent.Parent) {
    if ($parent.Exists -and ($parent.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
        throw 'Choose a result directory without a redirecting ancestor.'
    }
}
if ($Mode -eq 'authorized' -and (-not $Config -or $Append)) {
    throw 'Authorized mode requires a local config. For an annual append set accepted_model in that config.'
}
if ((Test-Path -LiteralPath $run) -ne [bool]$Resume) { throw 'Choose a fresh run or explicitly resume the existing run.' }
if (-not $Resume) { New-Item -ItemType Directory -Path $run | Out-Null }
$lock = Join-Path $run '.lock'
try { $lease = [IO.File]::Open($lock,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None) }
catch { throw 'Run locked. Check the owner and prior attempt before recovering an interrupted run.' }
try {
    $events = Join-Path $run 'events.jsonl'
    function Write-Event($Step, $State, $Year = $null, $Product = $null) {
        [ordered]@{ at = [datetimeoffset]::Now.ToString('o'); step = $Step; state = $State; year = $Year; product = $Product } |
            ConvertTo-Json -Compress | Add-Content -LiteralPath $events -Encoding utf8NoBOM
    }
    function Invoke-R([string]$Script, [string[]]$Arguments) {
        $output = & $Rscript --vanilla $Script @Arguments 2>&1
        if ($LASTEXITCODE -ne 0) {
            if ($Mode -eq 'synthetic') { $output | ForEach-Object { Write-Host $_ } }
            throw "R stage failed (exit $LASTEXITCODE)."
        }
        $output
    }
    $generation = Join-Path $run 'gen_script'
    $plan = Join-Path $generation 'design.json'
    $sourceFiles = @((Get-ChildItem -LiteralPath $model,$acquisition -File).FullName) +
        @($PSCommandPath,(Join-Path $model '../config/model.json'),
          (Join-Path $repo 'skills/data_acquisition/01_socioeconomic_natural_change/era5/scripts/copernicus_jobs.py'))
    $versions = [ordered]@{}
    foreach ($file in ($sourceFiles | Sort-Object)) {
        $versions[([IO.Path]::GetRelativePath($repo,$file)).Replace('\','/')] = (Get-FileHash -LiteralPath $file).Hash
    }
    $requestHash = if ($Config) { (Get-FileHash -LiteralPath $Config).Hash } else { $null }
    $design = [ordered]@{
        mode = $Mode; append_test = [bool]$Append; request_sha256 = $requestHash; code = $versions
        stages = @('acquire','prepare','pair_validate','fit','predict','calibrate','accept')
        scope = 'Candidate only. Synthetic mode stages invented provider files through the public acquisition scripts.'
    } | ConvertTo-Json -Depth 15
    if ($Resume) {
        if ((Get-Content -LiteralPath $plan -Raw).Trim() -cne $design.Trim()) { throw 'Request or code changed. Start a new run.' }
    } else {
        New-Item -ItemType Directory -Path $generation | Out-Null
        $design | Set-Content -LiteralPath $plan -Encoding utf8NoBOM
        Copy-Item -LiteralPath $PSCommandPath -Destination (Join-Path $generation 'controller.ps1')
    }

    function Resolve-Input($Base, $Path) {
        if (-not $Path) { return $null }
        if ([IO.Path]::IsPathRooted($Path)) { return $Path }
        Join-Path $Base $Path
    }

    function Prepare-Annual($Cfg, $TrialStage) {
        $needed = @($Cfg.output_years)
        if (-not $Cfg.accepted_model) { $needed += @($Cfg.training_years) }
        $needed = @($needed | Sort-Object -Unique)
        $root = $Cfg.data_root
        $staged = Join-Path $run 'acquired'
        $localInputs = @{}
        # Resolve the complete annual inventory before spending transfer budget.
        foreach ($year in $needed) {
            $row = $Cfg.annual[[string]$year]
            if (-not $row) { Write-Event acquire missing $year annual; throw "Missing annual configuration for $year." }
            foreach ($name in @('light','population','cover')) {
                $item = $row[$name]
                if (-not $item) { Write-Event acquire missing $year $name; throw "Missing $name specification for $year." }
                if ($item.year -ne $year -or -not $item.version) {
                    Write-Event acquire invalid $year $name
                    throw "Year or version mismatch for $year $name."
                }
                $path = Resolve-Input $root $item.path
                if ($path -and (Test-Path -LiteralPath $path -PathType Leaf)) {
                    if ($item.sha256 -cnotmatch '^[a-f0-9]{64}$' -or (Get-FileHash -LiteralPath $path).Hash -ne $item.sha256) {
                        Write-Event acquire invalid $year $name
                        throw "Checksum mismatch for $year $name."
                    }
                    $localInputs["$year/$name"] = $true
                    Write-Event acquire verified $year $name
                    continue
                }
                if ($name -eq 'light' -and $item.provider -eq 'dataverse' -and $item.version -match '^\d+\.\d+$') { continue }
                if ($Mode -eq 'authorized' -and $name -eq 'cover' -and $item.provider -eq 'cds') {
                    $request = Resolve-Input $root $item.request
                    if ($request -and (Test-Path -LiteralPath $request -PathType Leaf)) { continue }
                }
                Write-Event acquire missing $year $name
                throw "Missing configured $name input or transfer request for $year."
            }
        }
        New-Item -ItemType Directory -Path $staged -Force | Out-Null
        foreach ($year in $needed) {
            $row = $Cfg.annual[[string]$year]
            foreach ($name in @('light','population','cover')) {
                $item = $row[$name]
                if ($localInputs.ContainsKey("$year/$name")) { continue }
                Write-Event acquire start $year $name
                if ($name -eq 'light' -and $item.provider -eq 'dataverse') {
                    $options = @{ Years = @([int]$year); Action = 'Download'; Destination = $staged; CatalogVersion = $item.version }
                    if ($Mode -eq 'synthetic') {
                        $options.Doi = '10.0000/SYNTHETIC'
                        $options.FixtureCatalog = Resolve-Input $root $item.fixture_catalog
                    }
                    $raw = & (Join-Path $acquisition 'Get-DataverseRaster.ps1') @options
                    $bounds = @($Cfg.geo.extent | ForEach-Object { ([double]$_).ToString('R',[cultureinfo]::InvariantCulture) })
                    $argsR = @((Join-Path $raw 'source.tif'),$staged,(Join-Path $raw 'source.json')) + $bounds
                    $lines = @(Invoke-R (Join-Path $acquisition 'crop_annual_raster.R') $argsR)
                    $crop = ([string]$lines[-1]).Trim()
                    $row[$name] = Get-Content -LiteralPath (Join-Path $crop 'source.json') -Raw | ConvertFrom-Json -AsHashtable
                    $row[$name].path = Join-Path $crop $row[$name].path
                } elseif ($Mode -eq 'authorized' -and $name -eq 'cover' -and $item.provider -eq 'cds') {
                    $request = Resolve-Input $root $item.request
                    $requestBody = Get-Content -LiteralPath $request -Raw | ConvertFrom-Json
                    if (@($requestBody.year).Count -ne 1 -or [string]$requestBody.year[0] -ne [string]$year) {
                        throw "CDS request year differs from $year."
                    }
                    $target = Join-Path $staged "land_cover_$year.nc"
                    & (Join-Path $model 'Get-CdsLandCover.ps1') -Request $request -Destination $staged -Execute | Out-Null
                    $row[$name] = Get-Content -LiteralPath "$target.source.json" -Raw | ConvertFrom-Json -AsHashtable
                    $row[$name].path = $target
                } else {
                    Write-Event acquire missing $year $name
                    throw "Missing local $name for $year. Stage the named source and resume."
                }
                Write-Event acquire complete $year $name
            }
        }
        $resolved = Join-Path $run "resolved-$TrialStage.json"
        $Cfg | ConvertTo-Json -Depth 30 | Set-Content -LiteralPath $resolved -Encoding utf8NoBOM
        $resolved
    }

    $configPath = $Config
    $fixture = Join-Path $run 'fixture'
    if ($Mode -eq 'synthetic') {
        if (-not (Test-Path -LiteralPath (Join-Path $fixture 'initial.json'))) {
            $priorArchive = $env:AIRMOSAIC_GDP_FIXTURE_ARCHIVE
            try {
                $env:AIRMOSAIC_GDP_FIXTURE_ARCHIVE = '1'
                Invoke-R (Join-Path $model 'run_synthetic.R') @($fixture) | Out-Null
            } finally { $env:AIRMOSAIC_GDP_FIXTURE_ARCHIVE = $priorArchive }
        }
        $configPath = Join-Path $fixture 'initial.json'
    }
    $cfg = Get-Content -LiteralPath $configPath -Raw | ConvertFrom-Json -AsHashtable
    if ($cfg.mode -ne $Mode) { throw 'Run mode differs from config.' }
    if ($Mode -eq 'synthetic') {
        $catalog = Join-Path $cfg.data_root 'fixture-catalog.json'
        if (-not (Test-Path -LiteralPath $catalog)) {
            $entries = foreach ($year in ($cfg.annual.Keys | Sort-Object)) {
                $light = $cfg.annual[$year].light
                $label = "${year}_Version2.zip"
                $zip = Join-Path $cfg.data_root $label
                if (-not (Test-Path -LiteralPath $zip)) {
                    Compress-Archive -LiteralPath (Join-Path $cfg.data_root $light.fixture_source) -DestinationPath $zip
                }
                [ordered]@{
                    label = $label; restricted = $false
                    dataFile = @{ id = [int]$year; filesize = (Get-Item -LiteralPath $zip).Length
                                  checksum = @{ type = 'MD5'; value = (Get-FileHash -LiteralPath $zip -Algorithm MD5).Hash } }
                }
            }
            @{ versionState = 'RELEASED'; versionNumber = 1; versionMinorNumber = 0; files = @($entries) } |
                ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $catalog -Encoding utf8NoBOM
        }
    }
    $cfg.work_root = Join-Path $run 'work'
    $cfg.release_root = Join-Path $run 'test-release'
    $stage = 'preflight'
    Write-Event $stage start
    foreach ($key in @('boundary','county_gdp','province_gdp') + $(if (-not $cfg.accepted_model) { @('history','legacy_booster') })) {
        if (-not $key) { continue }
        $path = Resolve-Input $cfg.data_root $cfg.inputs[$key]
        if (-not $path -or -not (Test-Path -LiteralPath $path -PathType Leaf)) {
            Write-Event $stage missing $null $key
            throw "Missing approved input: $key."
        }
    }
    Write-Event $stage complete

    function Run-Candidate($Cfg, $Label) {
        $resolved = Prepare-Annual $Cfg $Label
        Write-Event model start
        $output = Invoke-R (Join-Path $model 'run_gdp.R') @($resolved,'accept')
        if ($Mode -eq 'synthetic') { $output | ForEach-Object { Write-Host $_ } }
        $line = @($output | Where-Object { $_ -is [string] -and $_.StartsWith('ACCEPTED ') })
        if ($line.Count -ne 1) { throw 'Accepted candidate was not reported.' }
        $candidate = $line[0].Substring(9).Trim()
        Write-Event model accepted
        $candidate
    }

    $stage = 'initial'
    $first = Run-Candidate $cfg $stage
    $candidates = @((Split-Path -Leaf $first))
    if ($Append) {
        $stage = 'append'
        $cfg.accepted_model = $candidates[0]
        $cfg.output_years = @(2023)
        $second = Run-Candidate $cfg $stage
        $candidates += Split-Path -Leaf $second
    }
    $files = [ordered]@{}
    foreach ($id in $candidates) {
        $name = "work/candidates/$id/receipt.json"
        $files[$name] = (Get-FileHash -LiteralPath (Join-Path $run $name)).Hash.ToLowerInvariant()
    }
    $files | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $run 'delivery-sha256.json') -Encoding utf8NoBOM
    [ordered]@{ status = 'accepted'; mode = $Mode; candidates = $candidates } |
        ConvertTo-Json | Set-Content -LiteralPath (Join-Path $run 'workflow.json') -Encoding utf8NoBOM
    Write-Event workflow accepted
    $candidates | ForEach-Object { Write-Output (Join-Path $run "work/candidates/$_") }
} catch {
    if (Test-Path -LiteralPath $generation) {
        [ordered]@{ status='incomplete'; mode=$Mode; stage=$stage } |
            ConvertTo-Json | Set-Content -LiteralPath (Join-Path $run 'workflow.json') -Encoding utf8NoBOM
        if (Get-Command Write-Event -CommandType Function -ErrorAction SilentlyContinue) { Write-Event workflow incomplete }
    }
    throw
} finally {
    $lease.Dispose()
    [IO.File]::Delete($lock)
}
