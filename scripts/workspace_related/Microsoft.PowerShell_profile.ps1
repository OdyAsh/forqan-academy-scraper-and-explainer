# add the code below to a file called Microsoft.PowerShell_profile.ps1
#   where the location is one of the options mentioned here:
#   https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_profiles?view=powershell-7.4#profile-types-and-locations
# alternatively, you can know where to add that file by running PowerShell, then running this command: 
#   `$PROFILE`

<#
.SYNOPSIS
    Customizes the PowerShell prompt to display the current Conda environment and the current working directory.

.DESCRIPTION
    The prompt function modifies the PowerShell prompt to display the current Conda environment directory 
    and the current working directory in different colors. 
    The Conda environment directory is displayed in green and the current working directory is displayed in cyan.
#>
function prompt {
    Write-Host "$($env:CONDA_PROMPT_MODIFIER)`n" -NoNewline -ForegroundColor Green
    Write-Host "$(Get-Location)`n" -NoNewline -ForegroundColor Cyan
    return "> "
}

<#
.SYNOPSIS
    Installs Python packages using pip and logs the installed packages and versions to a requirements file.

.DESCRIPTION
    The pip-install function installs Python packages using pip. 
    It takes a list of packages as input. After the packages are installed, 
    the function logs the installed packages and their versions to a requirements file. 
    If a package is not found in the requirements file, it is added. 
    The function also maintains a version-less requirements file.
#>
function pip-install {
    param(
        [Parameter(ValueFromRemainingArguments=$true)]
        $packages
    )

    # $condaPath = $($env:CONDA_PROMPT_MODIFIER -replace '\\conda$', '')
    # $reqFile = Join-Path -Path $condaPath -ChildPath "requirements-user-installed.txt"
    $reqFile = "requirements-user-installed.txt"
    $reqFileWithoutVersions = "requirements-user-installed-without-versions.txt"
    $timestamp = Get-Date -Format "yyyy-MM-dd___HH-mm-ss"

    echo "[[Recall: Using command found in Microsoft_PowerShell_profile.ps1, so CWD should be project's root directory]]"

    pip install $packages
    $install_is_successful = $?
    
    if ($install_is_successful) {

        # for loop that assigns a variable called "at_least_one_package_installed" to true if at least one package was installed
        $one_not_found = $false
        foreach ($package in $packages) {
            if ((Get-Content $reqFileWithoutVersions) -notcontains $package) {
                $one_not_found = $true
                break
            }
        }

        if ($one_not_found) {
            echo "# installed the packages below on ${timestamp}:" >> $reqFile
            echo "# installed the packages below on ${timestamp}:" >> $reqFileWithoutVersions
        }

        foreach ($package in $packages) {
            
            $version = (pip show $package | Where-Object { $_ -match 'Version:' }).Split(':')[1].Trim()
            if ((Get-Content $reqFile) -notcontains "$package==$version") {
                echo "$package==$version" >> $reqFile 
            }

            if ((Get-Content $reqFileWithoutVersions) -notcontains $package) {
                echo $package >> $reqFileWithoutVersions 
            }
        }
    }
}

<#
.SYNOPSIS
    Uninstalls Python packages using pip and updates the requirements file.

.DESCRIPTION
    The pip-uninstall function uninstalls Python packages using pip. 
    It takes a list of packages as input. 
    After the packages are uninstalled, the function updates the requirements file to reflect the changes. 
    The function also maintains a version-less requirements file.
#>
function pip-uninstall {
    param(
        [Parameter(ValueFromRemainingArguments=$true)]
        $packages
    )

    echo "[[Recall: Using command found in Microsoft_PowerShell_profile.ps1, so CWD should be project's root directory]]"

    pip3-autoremove $packages
    $uninstall_is_successful = $?

    # logic that will comment out the uninstalled package(s) from the requirements files:
    if ($uninstall_is_successful) {
        
        $reqFile = "requirements-user-installed.txt"
        $content = Get-Content -path $reqFile
        
        $reqFileWithoutVersions = "requirements-user-installed-without-versions.txt"
        $contentWithoutVersions = Get-Content -path $reqFileWithoutVersions
        
        $timestamp = Get-Date -Format "yyyy-MM-dd___HH-mm-ss"
        
        foreach ($package in $packages) {
            $content | ForEach-Object {
                if ($_ -match "$package==" -and $_ -notmatch 'uninstalled later') {
                    "# $_ # got uninstalled later by python3-pip-autoremove package on $timestamp"
                } else {
                    $_
                }
            } | Out-File -FilePath $reqFile
            # DEBUGGING NOTE: for some reason, using Set-Content instead of Out-File here 
            #   will cause the .txt file to corrupt if we later try to run pip-install function

            $contentWithoutVersions | ForEach-Object {
                if ($_ -eq $package) {
                    "# $_ # got uninstalled later by python3-pip-autoremove package on $timestamp"
                } else {
                    $_
                }
            } | Out-File -FilePath $reqFileWithoutVersions
        }
    }

}


# OLD LOGIC inside `pip-uninstall` function:
# logic that will just remove the uninstalled package(s) from the requirements files:
# foreach ($package in $packages) {
#     if ($?) { 
#         ((Get-Content -path $reqFile) -notmatch "$package==") | Set-Content -path $reqFile
#         ((Get-Content -path $reqFileWithoutVersions) -notmatch $package) | Set-Content -path $reqFileWithoutVersions
#     }
# }

# OLD CODE for `prompt` function: 

<#
    This function sets the custom prompt for the PowerShell console.
    It displays the current Conda environment directory and the current working directory.
    
    Side note 1: based on this source:
    https://medium.com/@anjkeesari/hiding-the-full-file-path-in-vscode-terminal-f3c6993a6c07

    Side note 2: the "if (...)" logic is suitable only if you want to retain the first virtual conda environment.
    Examples for when to do this: when running a script at the start of VSCOde and pressing ctrl+c, 
    the MiniConda3 environment gets stacked on top of the intial virtual environment.
    Read more about stacking conda environments here:
    https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#nested-activation
#>

# function prompt {
#   # Check if there are any CONDA_PREFIX environment variables set
#   $env_vars = Get-ChildItem env: | Where-Object { $_.Name -like 'CONDA_PREFIX_*' }
#   if ($env_vars) 
#   {
#     # If there are multiple CONDA_PREFIX variables, find the one with the highest index
#     $max_index = $env_vars.Name | ForEach-Object { [int]($_ -replace 'CONDA_PREFIX_', '') } | Measure-Object -Maximum | Select-Object -ExpandProperty Maximum
#     $env_var_name = "CONDA_PREFIX_" + $max_index
#   } 
#   else 
#   {
#     # If there is only one CONDA_PREFIX variable, use it
#     $env_var_name = "CONDA_PREFIX"
#   }
#   # Get the full path of the "currently activated/needed" Conda environment
#   $env_path = Get-Content -Path "env:$env_var_name"
#   # Get the path's leaf (i.e., the last directory of the path, which is the environment's name)
#   $env_dir = Split-Path -leaf -path $env_path


#   # Get the current working directory's full path
#   $p = Get-Location

#   # If there's a common string part between $env_path and $p, then update $p to be only the part after the common part
#   $parent_path = Split-Path -Parent -Path $env_path
#   $grandparent_path = (Split-Path -Parent -Path $parent_path) + '\'
#   if ($p -like "*$grandparent_path*") {
#     $p = $p -replace [regex]::Escape($grandparent_path), ''
#   }
#   else {
#     # If there's no common part, then update $p to be just the leaf of the current working directory
#     $p = Split-Path -leaf -path (Get-Location)
#   }

#   $ps_shell_output = "(BASE\PROJ\$env_dir) BASE\$p> "

#   # uncomment code below for default values:
#   # $env_path = Get-Content -Path env:CONDA_PREFIX
#   # $env_dir = $env_path
#   # $p = Get-Location
#   # $ps_shell_output = "($env_dir) $p> "

#   # Set the custom prompt format
#   "$ps_shell_output"
# }