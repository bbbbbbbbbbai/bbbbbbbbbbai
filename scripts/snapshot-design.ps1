param(
    [Parameter(Mandatory = $true)]
    [string] $SourceRoot
)

$ErrorActionPreference = 'Stop'
$source = (Resolve-Path -LiteralPath $SourceRoot).Path
$repo = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$destination = [IO.Path]::GetFullPath((Join-Path $repo 'design'))
if (-not (Test-Path -LiteralPath (Join-Path $source 'manifest.json'))) {
    throw 'Source must be the design atlas directory containing manifest.json.'
}
if ($destination.StartsWith($source + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) {
    throw 'Destination cannot be within the source tree.'
}
$extensions = @('.png', '.jpg', '.jpeg', '.webp', '.json', '.html', '.md', '.py', '.cjs', '.txt')
$textExtensions = @('.json', '.html', '.md', '.py', '.cjs', '.txt')
$secretPattern = '(sk-[A-Za-z0-9_-]{16,}|AKID[A-Za-z0-9]{16,}|gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----)'
$files = @(Get-ChildItem -LiteralPath $source -File -Recurse | Where-Object {
    $_.Extension -in $extensions -and $_.FullName -notmatch '[\\/](__pycache__|\.git|node_modules)[\\/]'
})

# Complete the credential preflight before copying any artifact.
foreach ($file in $files) {
    if ($file.Extension -in $textExtensions) {
        if ([IO.File]::ReadAllText($file.FullName) -match $secretPattern) {
            throw "Credential pattern detected in $($file.Name); no snapshot was copied."
        }
    }
}

$copied = 0
$unchanged = 0
foreach ($file in $files) {
    $relative = [IO.Path]::GetRelativePath($source, $file.FullName)
    $target = [IO.Path]::GetFullPath((Join-Path $destination $relative))
    if (-not $target.StartsWith($destination + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) {
        throw 'Resolved target escapes the snapshot directory.'
    }
    if ((Test-Path -LiteralPath $target) -and
        ((Get-FileHash -LiteralPath $file.FullName).Hash -eq (Get-FileHash -LiteralPath $target).Hash)) {
        $unchanged++
        continue
    }
    $parent = Split-Path -Parent $target
    if (-not (Test-Path -LiteralPath $parent)) {
        New-Item -ItemType Directory -Path $parent -Force | Out-Null
    }
    Copy-Item -LiteralPath $file.FullName -Destination $target
    $copied++
}

[pscustomobject]@{
    Source = $source
    Destination = $destination
    Copied = $copied
    Unchanged = $unchanged
    Deleted = 0
}
