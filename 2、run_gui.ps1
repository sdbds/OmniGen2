# train script by @bdsqlsz

#region Configuration
$Config = @{
  checkpoint_path = "" # Or let it download automatically by not specifying
  port            = 7865
  share           = $false                # Set to $true to enable Gradio sharing link
}
#endregion

# Activate python venv
Set-Location $PSScriptRoot
if ($env:OS -ilike "*windows*") {
  if (Test-Path "./venv/Scripts/activate") {
    Write-Output "Windows venv"
    ./venv/Scripts/activate
  }
  elseif (Test-Path "./.venv/Scripts/activate") {
    Write-Output "Windows .venv"
    ./.venv/Scripts/activate
  }
}
elseif (Test-Path "./venv/bin/activate") {
  Write-Output "Linux venv"
  ./venv/bin/Activate.ps1
}
elseif (Test-Path "./.venv/bin/activate") {
  Write-Output "Linux .venv"
  ./.venv/bin/activate.ps1
}

$Env:HF_HOME = "huggingface"
$Env:TORCH_HOME = "torch"
#$Env:HF_ENDPOINT = "https://hf-mirror.com"
$Env:XFORMERS_FORCE_DISABLE_TRITON = "1"

#region Build Arguments
$AppArgs = [System.Collections.ArrayList]::new()

# Add arguments from Config
if ($Config.checkpoint_path) {
  [void]$AppArgs.Add("--model_path=$($Config.checkpoint_path)")
}
if ($Config.port) { [void]$AppArgs.Add("--port=$($Config.port)") }

# Boolean flags
if ($Config.share) { [void]$AppArgs.Add("--share") }

$FinalArgs = $AppArgs -join " "
#endregion

Write-Output "Running: python app.py $FinalArgs"
Invoke-Expression "python -m accelerate.commands.launch 'app.py' $FinalArgs"

Read-Host | Out-Null ;
