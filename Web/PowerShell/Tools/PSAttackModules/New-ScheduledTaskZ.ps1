function New-ScheduledTaskZ {
    <# 
      .SYNOPSIS 
      Creates Scheduled Tasks using the Schedule.Service COM Object

      Author: Jared Haight (@jaredhaight)
      License: MIT License
      Required Dependencies: None
      Optional Dependencies: None

      .DESCRIPTION 
      This script allows you to create Time, OnBoot and OnLogon scheduled tasks. You can specify a command and its arguments to be run.

      .PARAMETER Name
      The name of the Scheduled Task to be created

      .PARAMETER Time  
      Create a task that runs at a specified time

      .PARAMETER OnStartup
      Create a task that runs after the computer boots. Requires Admin Rights.

      .PARAMETER OnLogon  
      Create a task that runs after a user logs in. Requres Admin Rights.
      
      .PARAMETER StartTime
      A DateTime object for when the task becomes effective. Defaults to Now + 30 seconds

      .PARAMETER EndTime  
      A DateTime object for when the task will stop being effective. Defaults to Now + 30 years
      
      .PARAMETER Repeat
      How often the task will repeat, specified in minutes.

      .PARAMETER Command
      The command to run

      .PARAMETER Arguments
      The arguments to pass to the command when it's run.

      .EXAMPLE 
      PS C:\>$StartTime = (Get-Date).AddMinutes(15)
      PS C:\>New-ScheduledTaskZ -Name Updater -Time -StartTime $StartTime -Command powershell.exe -Arguments "-Command &{3 + 2; read-host}" -Repeat 90
 
      Description
      -----------
      Create a Scheduled Task named Updater that adds 3+2 in PowerShell. Task will start in 15 minutes and repeat every 90 minutes.

      .EXAMPLE 
      PS C:\>New-ScheduledTaskZ -Name TaskMan -OnBoot -Command powershell.exe -Arguments "-Command &{3 + 2; read-host}" -Repeat 15 -Username DERBYCON\AuditNomNom -Password ChangeMe1
 
      Description
      -----------
      Create a Scheduled Task named TaskMan that starts on boot and repeats every 15 minutes. This task will run as the AuditNomNom user even when they are not logged in.
      

      .EXAMPLE 
      PS C:\>New-ScheduledTaskZ -Name AuditCheck -OnLogin -Command powershell.exe -Arguments "-Command &{3 + 2; read-host}" -Repeat 15 -Hidden -Username Administrator -Password Password123
 
      Description
      -----------
      Create a Scheduled Task named AuditCheck that starts when any user logs in. Task will repeat every 15 minutes and will be hidden from view.

      .LINK 
      Script source can be found at https://github.com/jaredhaight/PowerPunch/Persistence/New-ScheduledTaskZ.ps1
    #>
  
    [CmdletBinding()]
    Param(      
        [Parameter()]
        [switch]$Time,

        [Parameter()]
        [switch]$OnLogon,
    
        [Parameter()]
        [switch]$OnStartup,
    
        [Parameter(Mandatory=$True)]
        [string]$Name,
    
        [Parameter()]
        [string]$ComputerName = $null,
    
        [Parameter()]
        [string]$Username = $null,
    
        [Parameter()]
        [string]$Password = $null,

        [Parameter()]
        [DateTime]$StartTime = ((Get-Date).AddSeconds(30)),

        [Parameter()]
        [DateTime]$EndTime = ((Get-Date).AddYears(30)),
    
        [Parameter()]
        [int]$Repeat,
    
        [Parameter(Mandatory=$True)]
        [string]$Command,
    
        [Parameter()]
        [string]$Arguments,
    
        [Parameter()]
        [switch]$Hidden = $false
    )
  
    if ($Time) {$TriggerType = 1}
    elseif ($OnStartup) {$TriggerType = 8}
    elseif ($OnLogon) {$TriggerType = 9}
  
    $ActionTypeExec = 0
    $TaskScheduler = New-Object -ComObject "Schedule.Service"

    try {
        $TaskScheduler.Connect($ComputerName)
    }
    catch {
        Write-Error "Could not connect to computer: $ComputerName"
        Break
    }

    $RootFolder = $TaskScheduler.GetFolder('\')
    $TaskDefinition = $TaskScheduler.NewTask(0)

    $Principal = $TaskDefinition.Principal
    $Principal.LogonType = 3
  
    if ($Username) {
        $Principal.UserId = $Username
    }
  
    if ($Username.ToUpper() -match "SYSTEM"){
        $Principal.LogonType = 5
        $Principal.RunLevel = 1
    }
  
    if ($Password) {
        $Principal.LogonType = 1
    }
  
    if ($Highest) {
        $Principal.RunLevel = 1
    }
  
    $TaskSettings = $TaskDefinition.Settings
    $TaskSettings.Enabled = $True
    $TaskSettings.StartWhenAvailable = $True
    $TaskSettings.Hidden = $Hidden

    $Triggers = $TaskDefinition.Triggers
    $Trigger = $Triggers.Create($TriggerType)

    $StartTimeFormated = Get-Date $StartTime -Format s
    $EndTimeFormated = Get-Date $EndTime -Format s 
    $Trigger.StartBoundary = $StartTimeFormated
    $Trigger.EndBoundary = $EndTimeFormated
    $Trigger.Enabled = $True

    if ($Repeat) {
        $Trigger.Repetition.Interval = "PT" + $Repeat.ToString() + "M"
    }

    $Action = $TaskDefinition.Actions.Create($ActionTypeExec)
    $Action.Path = $Command

    if ($Arguments) {
        $Action.Arguments = $Arguments
    }
 
    $RootFolder.RegisterTaskDefinition($Name,$TaskDefinition,6,$Username, $Password, $Principal.LogonType)
}
