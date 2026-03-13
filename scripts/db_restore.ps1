param(
  [Parameter(Mandatory=$true)][string]$FilePath,
  [string]$DBContainerName = $env:DB_CONTAINER_NAME
)
function LoadDotEnv {
  param([string]$path)
  if (Test-Path $path) {
    Get-Content $path | Where-Object { $_ -and -not $_.StartsWith("#") } | ForEach-Object {
      $kv = $_ -split '=',2
      if ($kv.Length -eq 2) {
        $k = $kv[0].Trim()
        $v = $kv[1].Trim().Trim("'").Trim('"')
        if (-not ${env:$k}) { Set-Item -Path "env:$k" -Value $v | Out-Null }
      }
    }
  }
}
function ParseDatabaseUrl {
  param([string]$url)
  $normalized = ($url -replace 'postgresql\+asyncpg','postgresql')
  $rx = '^(?<scheme>[^:]+)://(?<user>[^:/@]+)(?::(?<pass>[^@]*))?@(?<host>[^:/?#]+)(?::(?<port>\d+))?/(?<db>[^?]+)'
  $m = [regex]::Match($normalized, $rx)
  if (-not $m.Success) { throw "DATABASE_URL inválido: $url" }
  $port = if ($m.Groups['port'].Value) { [int]$m.Groups['port'].Value } else { 5432 }
  [pscustomobject]@{
    Scheme   = $m.Groups['scheme'].Value
    User     = $m.Groups['user'].Value
    Pass     = $m.Groups['pass'].Value
    Host     = $m.Groups['host'].Value
    Port     = $port
    Database = $m.Groups['db'].Value
  }
}
function EnsureDocker {
  try { docker --version | Out-Null } catch { throw "Docker no está disponible en PATH" }
}
function TestContainerRunning {
  param([string]$name)
  try {
    $names = docker ps --format "{{.Names}}"
    return @($names) -contains $name
  } catch { return $false }
}
if (-not (Test-Path $FilePath)) { throw "No se encontró el archivo: $FilePath" }
LoadDotEnv (Join-Path (Split-Path (Get-Location) -Parent) ".env")
if (-not $env:DATABASE_URL) { throw "Falta DATABASE_URL en entorno o .env" }
$db = ParseDatabaseUrl $env:DATABASE_URL
if (-not ($db.Scheme -like "postgres*")) { throw "Solo se soporta Postgres actualmente" }
EnsureDocker
$hostForContainer = if ($db.Host -in @("localhost","127.0.0.1")) { "host.docker.internal" } else { $db.Host }
if ($DBContainerName -and (TestContainerRunning $DBContainerName)) {
  $args = @("exec","-i","-e","PGPASSWORD=$($db.Pass)",$DBContainerName,"psql","-h",$db.Host,"-p",$db.Port.ToString(),"-U",$db.User,"-d",$db.Database,"-v","ON_ERROR_STOP=1")
  Get-Content -Raw -Encoding UTF8 $FilePath | & docker @args | Out-Null
} else {
  $args = @("run","--rm","-i","-e","PGPASSWORD=$($db.Pass)","postgres:17-alpine","psql","-h",$hostForContainer,"-p",$db.Port.ToString(),"-U",$db.User,"-d",$db.Database,"-v","ON_ERROR_STOP=1")
  Get-Content -Raw -Encoding UTF8 $FilePath | & docker @args | Out-Null
}
Write-Output "Restauración completada desde: $FilePath"
