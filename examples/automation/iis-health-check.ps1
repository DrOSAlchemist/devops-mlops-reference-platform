param(
    [Parameter(Mandatory = $true)]
    [string]$SiteName,

    [Parameter(Mandatory = $true)]
    [string]$HealthUrl
)

$ErrorActionPreference = "Stop"
Import-Module WebAdministration

$site = Get-Website -Name $SiteName
$appPoolState = (Get-WebAppPoolState -Name $site.applicationPool).Value
$httpStatus = 0

try {
    $response = Invoke-WebRequest -Uri $HealthUrl -TimeoutSec 10 -UseBasicParsing
    $httpStatus = [int]$response.StatusCode
}
catch {
    if ($_.Exception.Response) {
        $httpStatus = [int]$_.Exception.Response.StatusCode
    }
}

$result = [ordered]@{
    site = $site.Name
    siteState = $site.State.ToString()
    appPool = $site.applicationPool
    appPoolState = $appPoolState
    healthUrl = $HealthUrl
    httpStatus = $httpStatus
}
$result | ConvertTo-Json -Compress

if ($site.State.ToString() -ne "Started" -or $appPoolState -ne "Started" -or $httpStatus -lt 200 -or $httpStatus -ge 400) {
    exit 1
}