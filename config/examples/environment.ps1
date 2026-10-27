# Copy to <local-root>/config/environment.ps1, review, then dot-source it.
# This example sets path variables only; it does not create files or log in.
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$LocalRoot
)

$amRoot = (Resolve-Path -LiteralPath $LocalRoot -ErrorAction Stop).ProviderPath
if (-not (Get-Item -LiteralPath $amRoot -ErrorAction Stop).PSIsContainer) {
    throw "LocalRoot must be an existing directory outside Git checkouts."
}
$amAncestor = Get-Item -LiteralPath $amRoot -ErrorAction Stop
while ($null -ne $amAncestor) {
    if (Test-Path -LiteralPath (Join-Path $amAncestor.FullName ".git")) {
        throw "LocalRoot must be outside Git checkouts."
    }
    $amAncestor = $amAncestor.Parent
}

$env:AIRMOSAIC_ASSETS_DIR = Join-Path $amRoot "assets"
$env:AIRMOSAIC_CONFIG_DIR = Join-Path $amRoot "config"
$env:AIRMOSAIC_AUTH_DIR = Join-Path $amRoot "auth"

# Configure authorized model/input locations in the personal copy as needed.
# Keep passwords and tokens in a credential manager, not in this file.
