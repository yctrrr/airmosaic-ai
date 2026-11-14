# Launch the direct R stages without sending data or credentials to external services.
[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$Config,
    [ValidateSet('preflight','prepare','panel','validate','fit','grid','accept','plan','publish','rollback')]
    [string]$Stage = 'preflight',
    [string]$Rscript = 'Rscript',
    [string]$Candidate,
    [string]$Tag
)
$ErrorActionPreference = 'Stop'
if ($Stage -in @('plan','publish','rollback')) {
    if (-not $Candidate -or -not $Tag) { throw 'Candidate and Tag are required for release operations.' }
    & $Rscript --vanilla (Join-Path $PSScriptRoot 'publish_gdp.R') $Config $Candidate $Tag $Stage
} else {
    & $Rscript --vanilla (Join-Path $PSScriptRoot 'run_gdp.R') $Config $Stage
}
if ($LASTEXITCODE -ne 0) { throw "GDP workflow failed at $Stage (exit $LASTEXITCODE)." }
