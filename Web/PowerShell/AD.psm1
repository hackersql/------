function ad {

<#
    .SYNOPSIS
    AD is an advanced Powershell function. It gives you a menu of powerful Active Directory commands.

    .NOTES
    Author: Patrick Gruenauer, MVP PowerShell
    Web: https://sid-500.com

    .LINK
    None.

    .INPUTS
    None.

    .OUTPUTS
    None.
  #>

$host.ui.RawUI.WindowTitle='Created by SID-500.COM | Patrick Gruenauer'

$bufferSize = $Host.UI.RawUI.BufferSize
$buffersize.Height = 500
$host.UI.RawUI.BufferSize = $buffersize
 
$WindowSize = $host.UI.RawUI.WindowSize
$WindowSize.Height = 45
$host.UI.RawUI.WindowSize = $WindowSize


$line='========================================================='
$line2='________________________________________________________'


if (Get-Module -ListAvailable -Name ActiveDirectory) {
    Import-Module ActiveDirectory
} else {
    ''
    Write-Host "Operation aborted. No Active Directory Module found. Run this tool on a Domain Controller." -ForegroundColor Red
    ''
    throw "Error"
}

cls

do {

$line
Write-Host '      ACTIVE DIRECTORY Domain Services Section (v 1.1)' -ForegroundColor Green 
$line
Write-Host '---------------------------------------------------------'
Write-Host '           Forest | Domain | Domain Controller' -ForegroundColor Yellow
Write-Host '---------------------------------------------------------'
Write-Host " 1 - Forest | Domain | Sites Configuration ($env:userdnsdomain)"
Write-Host ' 2 - List Domain Controller'
Write-Host ' 3 - Replicate all Domain Controller'
Write-Host ' 4 - Show Default Domain Password Policy'
Write-Host ' 5 - List Domain Admins'
Write-Host ' 6 - List of Active GPOs'
Write-Host '---------------------------------------------------------'
Write-Host '                 User | Computer | Groups' -ForegroundColor Yellow
Write-Host '---------------------------------------------------------'
Write-Host ' 7 - List all Windows Clients'
Write-Host ' 8 - List all Windows Server'
Write-Host ' 9 - List all Computers (by Operatingsystem)'
Write-Host '10 - Run Systeminfo on Remote Computers'
Write-Host '11 - Move Computer to OU'
Write-Host '12 - List all Groups'
Write-Host '13 - List Group Membership by User'
Write-Host '14 - List all Users (enabled)'
Write-Host '15 - List User Properties'
Write-Host '16 - Users Last Domain Logon'
Write-Host '17 - Show currently logged on User by Computer'
Write-Host '18 - Send message to Users Desktop'
Write-Host '19 - Find orphaned User or Computer Accounts'
Write-Host '20 - Configure Time-Based-Group-Membership'
Write-Host '---------------------------------------------------------'
Write-Host '                OnBoarding | OffBoarding' -ForegroundColor Yellow
Write-Host '---------------------------------------------------------'
Write-Host '21 - OnBoarding  | Create new AD User (from existing)'
Write-Host '22 - OffBoarding | Disable AD User'
Write-Host '0  - Quit' -ForegroundColor Red

Write-Host ''

$input=Read-Host 'Select'

switch ($input) 
 { 
 1 {
    

    ''
    Write-Host -ForegroundColor Green 'FOREST Configuration' 

    $get=Get-ADForest
    $forest+=New-Object -TypeName PSObject -Property ([ordered]@{

    'Root Domain'=$get.RootDomain
    'Forest Mode'=$get.ForestMode
    'Domains'=$get.Domains -join ','
    'Sites'=$get.Sites -join ','
    })
   
    $forest | Format-Table -AutoSize -Wrap
    
    
    Write-Host -ForegroundColor Green 'DOMAIN Configuration' 
     
    Get-ADDomain | Format-Table DNSRoot, DomainMode, ComputersContainer, DomainSID -AutoSize -Wrap

    Write-Host -ForegroundColor Green 'SITES Configuration'
        
        $GetSite = [System.DirectoryServices.ActiveDirectory.Forest]::GetCurrentForest().Sites
        $Sites = @()
        foreach ($Site in $GetSite) {
        $Sites += New-Object -TypeName PSObject -Property (
        @{
        'SiteName'  = $site.Name
        'SubNets' = $site.Subnets -Join ','
        'Servers' = $Site.Servers -Join ','
        }
        )
        }
        $Sites | Format-Table -AutoSize -Wrap
        
    
    Write-Host -ForegroundColor Green 'Enabled OPTIONAL FEATURES' 
    Get-ADOptionalFeature -Filter * | Format-Table Name,RequiredDomainMode,RequiredForestMode -AutoSize -Wrap
    
    Read-Host 'Press 0 and Enter to continue'
	
    } 
    
    

 2 {
    $dcs=Get-ADDomainController -Filter * 
    $dccount=$dcs | Measure-Object | Select-Object -ExpandProperty count
    ''
    Write-Host -ForegroundColor Green "Active Directory Domain Controller ($env:userdnsdomain)" 
   
    
    $domdc=@()

    foreach ($dc in $dcs) {
    $domdc += New-Object -TypeName PSObject -Property (

    [ordered]@{
    'Name' = $dc.Name
    'IP Address' = $dc.IPv4Address
    'OS' = $dc.OperatingSystem
    'Site' = $dc.Site
    'Global Catalog' = $dc.IsGlobalCatalog
    'FSMO Roles' = $dc.OperationMasterRoles -join ','
    }
    )
    }
    ''
    
    $domdc | Format-Table -AutoSize -Wrap

    
    Write-Host 'Total Number: '$dccount"" -ForegroundColor Yellow

    ''
	
    $ping=Read-Host "Do you want to test connectivity (ping) to these Domain Controllers? (Y/N)"

    If ($ping -eq 'Y') {
	foreach ($items in $dcs.Name) {
	Test-Connection $items -Count 1 | Format-Table Address, IPv4Address, ReplySize, ResponseTime}
    Read-Host 'Press 0 and Enter to continue'
    }
    
    else {
    ''
    Read-Host 'Press 0 and Enter to continue'
    }

    }

 3 { 
    ''
    Write-Host "This sub-menu replicates all Domain Controller on all Sites of the Domain $env:userdnsdomain."
    ''

    Write-Host 'Start Replication?' -ForegroundColor Yellow
    ''
    $startr=Read-Host 'Y/N'

    If ($startr) 

    {

    (Get-ADDomainController -Filter *).Name | Foreach-Object {repadmin /syncall $_ (Get-ADDomain).DistinguishedName /e /A | Out-Null}; Start-Sleep 10; Get-ADReplicationPartnerMetadata -Target "$env:userdnsdomain" -Scope Domain | Select-Object Server, LastReplicationSuccess | Out-Host


    }


    }
 
 4 {
    ''
     Write-Host -ForegroundColor Green 'The Default Domain Policy is configured as follows:'`n 
     Get-ADDefaultDomainPasswordPolicy | Format-List ComplexityEnabled, LockoutDuration,LockoutObservationWindow,LockoutThreshold,MaxPasswordAge,MinPasswordAge,MinPasswordLength,PasswordHistoryCount,ReversibleEncryptionEnabled
     
     Read-Host 'Press 0 and Enter to continue' 
    
    } 


5 {

    ''
    Write-Host -ForegroundColor Green 'The following users are member of the Domain Admins group:'`n

    $sid=(Get-ADDomain).DomainSid.Value + '-512'
    Get-ADGroupMember -identity $sid | Format-Table Name,SamAccountName,SID -AutoSize -Wrap
    ''
    Read-Host 'Press 0 and Enter to continue'
    
    } 

6 {
    ''
    Write-Host -ForegroundColor Green 'The GPOs below are linked to AD Objects:'`n 
    Get-GPO -All | ForEach-Object {
    If ( $_ | Get-GPOReport -ReportType XML | Select-String '<LinksTo>' ) {
    Write-Host $_.DisplayName}}
    ''
    Read-Host 'Press 0 and Enter to continue'


    }

 
 7 {
    $client=Get-ADComputer -Filter {operatingsystem -notlike '*server*'} -Properties Name,Operatingsystem,OperatingSystemVersion,IPv4Address 
    $ccount=$client | Measure-Object | Select-Object -ExpandProperty count
    ''
    Write-Host -ForegroundColor Green "Windows Clients $env:userdnsdomain"
    
    Write-Output $client | Sort-Object Operatingsystem | Format-Table Name,Operatingsystem,OperatingSystemVersion,IPv4Address -AutoSize
    ''
    Write-Host 'Total: '$ccount"" -ForegroundColor Yellow
    ''
    Read-Host 'Press 0 and Enter to continue'
    }
 
 8 {
    $server=Get-ADComputer -Filter {operatingsystem -like '*server*'} -Properties Name,Operatingsystem,OperatingSystemVersion,IPv4Address 
    $scount=$server | Measure-Object | Select-Object -ExpandProperty count
    ''
    Write-Host -ForegroundColor Green "Windows Server $env:userdnsdomain" 
   
    Write-Output $server | Sort-Object Operatingsystem | Format-Table Name,Operatingsystem,OperatingSystemVersion,IPv4Address
    ''
    Write-Host 'Total: '$scount"" -ForegroundColor Yellow
    ''
    Read-Host 'Press 0 and Enter to continue'
    }
 
 9 {
    $all=Get-ADComputer -Filter * -Properties Name,Operatingsystem,OperatingSystemVersion,IPv4Address 
    $acount=$all | Measure-Object | Select-Object -ExpandProperty count
    ''
    Write-Host -ForegroundColor Green "All Computer $env:userdnsdomain" 
     
    Write-Output $all | Select-Object Name,Operatingsystem,OperatingSystemVersion,IPv4Address | Sort-Object OperatingSystem | Format-Table -GroupBy OperatingSystem 
    Write-Host 'Total: '$acount"" -ForegroundColor Yellow
    ''
    Read-Host 'Press 0 and Enter to continue'
    }

 10  {    do {

        Write-Host ''
        Write-Host 'This runs systeminfo on specific computers. Select scope:' -ForegroundColor Green
        Write-Host ''
        Write-Host '1 - Localhost' -ForegroundColor Yellow
        Write-Host '2 - Remote Computer (Enter Computername)' -ForegroundColor Yellow
        Write-Host '3 - All Windows Server' -ForegroundColor Yellow
        Write-Host '4 - All Windows Computer' -ForegroundColor Yellow
        Write-Host '0 - Quit' -ForegroundColor Yellow
        Write-Host ''
        $scopesi=Read-Host 'Select'
        
        $header='Host Name','OS','Version','Manufacturer','Configuration','Build Type','Registered Owner','Registered Organization','Product ID','Install Date','Boot Time','System Manufacturer','Model','Type','Processor','Bios','Windows Directory','System Directory','Boot Device','Language','Keyboard','Time Zone','Total Physical Memory','Available Physical Memory','Virtual Memory','Virtual Memory Available','Virtual Memory in Use','Page File','Domain','Logon Server','Hotfix','Network Card','Hyper-V'


        switch ($scopesi) {

        1 {
            
            & "$env:windir\system32\systeminfo.exe" /FO CSV | Select-Object -Skip 1 | ConvertFrom-Csv -Header $header | Out-Host
            
          }

        2 {
            ''
            Write-Host 'Separate multiple computernames by comma. (example: server01,server02)' -ForegroundColor Yellow
            Write-Host ''
            $comps=Read-Host 'Enter computername'
            $comp=$comps.Split(',')

            $cred=Get-Credential -Message 'Enter Username and Password of a Member of the Domain Admins Group'
            Invoke-Command -ComputerName $comps -Credential $cred {systeminfo /FO CSV | Select-Object -Skip 1} -ErrorAction SilentlyContinue | ConvertFrom-Csv -Header $header | Out-Host
            

            }

        3 { 
            $cred=Get-Credential -Message 'Enter Username and Password of a Member of the Domain Admins Group'

            Invoke-Command -ComputerName (Get-ADComputer -Filter {operatingsystem -like '*server*'}).Name -Credential $cred {systeminfo /FO CSV | Select-Object -Skip 1} -ErrorAction SilentlyContinue | ConvertFrom-Csv -Header $header | Out-Host
            
            }

        4 {
            $cred=Get-Credential -Message 'Enter Username and Password of a Member of the Domain Admins Group'

            Invoke-Command -ComputerName (Get-ADComputer -Filter *).Name -Credential $cred {systeminfo /FO CSV | Select-Object -Skip 1} -ErrorAction SilentlyContinue | ConvertFrom-Csv -Header $header | Out-Host
            
            }

            }  
            
            }
        while ($scopesi -ne '0')
            }
                     
      
 
 11 {
        ''
    Write-Host 'This sections moves Computer Accounts to an OU.' -ForegroundColor Green

    do {
     
     ''
     Write-Host 'Enter Computer Name or Q to quit' -ForegroundColor Yellow
     ''
     $comp=Read-Host 'Computer Name'

     $c=Get-ADComputer -Filter 'name -like $comp' -Properties CanonicalName -ErrorAction SilentlyContinue

     $cfound=$c.Name
     
     If ($comp -eq 'Q') {Break}
     
     If ($cfound)
     
     {

     $discfound=$c.CanonicalName

     ''
     Write-host -foregroundcolor Green "$comp in $discfound found!"
     ''
     
     }

    elseif (!$cfound) {
    ''
    Write-Host -ForegroundColor Red "$comp not found. Please try again."}
    

    
   }
   
   while (!$cfound)

    do {


     If (($comp -eq 'Q') -or (!$cfound)) {Break}

     $Domain=(Get-ADDomain).DistinguishedName

     Write-Host 'Enter Name of OU (e.g. HR) or Q to quit' -ForegroundColor Yellow
     ''
     
     $OU=Read-Host 'Enter OU Name'

     $OUfound=Get-ADOrganizationalUnit -Filter 'name -like $OU'
     
     If ($OU -eq 'Q') {Break}
     
     If ($OUfound)
     
     {
     ''
     Write-host -foregroundcolor Green "$OUfound found!"
     ''
     }

    elseif (!$OUfound) {
    ''
    Write-Host -ForegroundColor Red "$OU not found. Please try again."
    ''
    
    }
     }
   
   
   while (!$OUfound)

    If ($comp -eq 'Q') {Break}

    If ($OUfound -and $cfound) 

                {
        ''
        Write-Host "Are you sure you want to move Computer $cfound to $OUfound ?" -ForegroundColor Yellow
        ''
        $dec=Read-Host "Press Y or any other key to abort"}

    If ($dec -eq "Y")

            {

            $dis=$OUfound.DistinguishedName

            Get-ADComputer $cfound | Move-ADObject -TargetPath "$dis"

            ''

            Write-Host "Computer $cfound moved to $OUfound" -ForegroundColor Green

            ''

            Get-ADComputer -Identity $cfound | Select-Object Name,DistinguishedName,Enabled,SID | Out-Host


            }

else 

{
''
Write-Host 'Operation aborted.' -ForegroundColor Red
}
''
Read-Host 'Press 0 and Enter to continue'

    }
    
 
 12 {
    ''
        Write-Host 'Overview of all Active Directory Groups' -ForegroundColor Green
        Get-ADGroup -Filter * -Properties * | Sort-Object Name | Format-Table Name,GroupCategory,GroupScope,SID -AutoSize -Wrap | more
        Read-Host 'Press 0 and Enter to continue'
    }

 13 {
        do {
        ''
        $groupm=Read-Host 'Enter group name'
        ''
        Write-Host "Group Members of $groupm" -ForegroundColor Green
        Get-ADGroupMember $groupm | Format-Table Name,SamAccountName,SID -AutoSize -Wrap
        $input=Read-Host 'Quit searching groups? (Y/N)'
        }
        while ($input -eq 'N')
    }
 
 14 { 
        ''
        Write-Host "The following users in $env:userdnsdomain are enabled:" -ForegroundColor Green
        Get-ADUser -Filter {enabled -eq $true} -Properties CanonicalName,whenCreated | Sort-Object Name | Format-Table Name,SamAccountName,CanonicalName,whenCreated -AutoSize -wrap | more
        Read-Host 'Press 0 and Enter to continue'
     
     } 
 


 15 {
        do {
        ''
        $userp=Read-Host 'Enter user logon name'
        ''
        Write-Host "Details of user $userp" -ForegroundColor Green
        
        Get-ADUser $userp -Properties * | Format-List GivenName,SurName,DistinguishedName,Enabled,EmailAddress,ProfilePath,ScriptPath,MemberOf,LastLogonDate,whencreated
        $input=Read-Host 'Quit searching users? (Y/N)'
        }
        while ($input -eq 'N')
        
        }

 16 {   ''
        Write-Host "This section shows the latest Users Active Directory Logon based on all Domain Controllers of $env:userdnsdomain." -ForegroundColor Green
        

        do {

        do {
        ''
        Write-Host 'Enter USER LOGON NAME (Q to quit)' -ForegroundColor Yellow
        ''
        $userl=Read-Host 'USER LOGON NAME'
        
        If ($userl -eq 'Q') {Break}
        
        $ds=dsquery user -samid $userl

        ''

        If ($ds)

        {

        Write-Host "User $userl found! Please wait ... contacting all Domain Controllers ... Showing results from most current DC ..." -ForegroundColor Green

        }

        else 

        {


        Write-Host "User $userl not found. Try again" -ForegroundColor Red}
        
        }

        while (!$ds)
 
        $resultlogon=@()

        If ($userl -eq 'Q') {Break}

        $getdc=(Get-ADDomainController -Filter *).Name

        foreach ($dc in $getdc) {

        Try {
        
        $user=Get-ADUser $userl -Server $dc -Properties lastlogon -ErrorAction Stop
        
        $resultlogon+=New-Object -TypeName PSObject -Property ([ordered]@{
                
                'Most current DC' = $dc
                'User' = $user.Name
                'LastLogon' = [datetime]::FromFileTime($user.'lastLogon')
                
                })
        
        }

        Catch {
        ''
        Write-Host "No reports from $dc!" -ForegroundColor Red

        }

        }
        
        

        If ($userl -eq 'Q') {Break}
        ''

        $resultlogon | Where-Object {$_.lastlogon -NotLike '*1601*'} | Sort-Object LastLogon -Descending | Select-Object -First 1 | Format-Table -AutoSize

        If (($resultlogon | Where-Object {$_.lastlogon -NotLike '*1601*'}) -EQ $null)

        {
        
        ''
        Write-Host "All domain controllers report that the user"$user.name"has never logged on til now." -ForegroundColor Red}
        
        Write-Host 'Search again? Press Y or any other key to quit ' -ForegroundColor Yellow
        ''
        $input=Read-Host 'Enter (Y/N)'    
        


}

while ($input -eq 'Y')


}


 17 {    $result=@()

       ''
       Write-Warning 'This section only works flawlessly on English Operating Systems.'

       ''

       $read=Read-Host 'Enter COMPUTER NAME to query logged on users'

       $cred=Get-Credential -Message 'Enter Username and Password of a Member of the Domain Admins Group (domain/username)'

       Invoke-Command -ComputerName $read -ScriptBlock {quser} -Credential $cred | Select-Object -Skip 1 | Foreach-Object {

       $b=$_.trim() -replace '\s+',' ' -replace '>','' -split '\s'


       If (($b[2] -like 'Disc*') -or ($b[2] -like 'Getr*')) {

          $result+= New-Object -TypeName PSObject -Property ([ordered]@{
                'User' = $b[0]
                'Computer' = $read
                'Date' = $b[4]
                'Time' = $b[5..6] -join ' '
                })
           
            
            }

        else {

        $result+= New-Object -TypeName PSObject -Property ([ordered]@{
                'User' = $b[0]
                'Computer' = $read
                'Date' = $b[5]
                'Time' = $b[6..7] -join ' '
                })

                }

        

} 
         ''
         Write-Host "User Logons on $read" -ForegroundColor Green

         $result | Format-Table

         Read-Host 'Press 0 and Enter to continue'
        }


 18 {    do {
        Write-Host ''
        Write-Host 'To which computers should a message be sent?'
        Write-Host ''
        Write-Host '1 - Localhost' -ForegroundColor Yellow
        Write-Host '2 - Remote Computer (Enter Computername)' -ForegroundColor Yellow
        Write-Host '3 - All Windows Server' -ForegroundColor Yellow
        Write-Host '4 - All Windows Computer' -ForegroundColor Yellow
        Write-Host '0 - Quit' -ForegroundColor Yell
        Write-Host ''
        $scopemsg=Read-Host 'Select'
        
        

        switch ($scopemsg) {

        1 {
            
            ''
            Write-Host 'Enter message sent to all users logged on LOCALHOST' -ForegroundColor Yellow
            ''
            $msg=Read-Host 'Message'
            msg * "$msg"
            
          }

        2 {
            ''
            Write-Host 'Separate multiple computernames by comma. (example: server01,server02)' -ForegroundColor Yellow
            ''
            $comp=Read-Host 'Enter Computername'
            $comps=$comp.Split(',')
            ''
            $msg=Read-Host 'Enter Message'
            $cred=Get-Credential -Message 'Enter Username and Password of a Member of the Domain Admins Group'
            Invoke-Command -ComputerName $comps -Credential $cred -ScriptBlock {msg * $using:msg}
            
          } 
            

        3 {
            ''
            
            Write-Host 'Note that the message will be sent to all servers!' -ForegroundColor Yellow
            ''
            $msg=Read-Host 'Enter Message'
            $cred=Get-Credential -Message 'Enter Username and Password of a Member of the Domain Admins Group'

            
            (Get-ADComputer -Filter {operatingsystem -like '*server*'}).Name | Foreach-Object {Invoke-Command -ComputerName $_ -ScriptBlock {msg * $using:msg} -Credential $cred -ErrorAction SilentlyContinue}}
           
         4 { 
            ''
            
            Write-Host 'Note that the message will be sent to all computers!' -ForegroundColor Yellow
            ''
            $msg=Read-Host 'Enter Message'

            $cred=Get-Credential -Message 'Enter Username and Password of a Member of the Domain Admins Group'

            (Get-ADComputer -Filter *).Name | Foreach-Object {Invoke-Command -ComputerName $_ -ScriptBlock {msg * $using:msg} -Credential $cred -ErrorAction SilentlyContinue}}

           
           }}
        
        while ($scopemsg -ne '0')
}

 19 {
    ''
    
    Write-Host 'Enter U for searching orphaned USER accounts or C for COMPUTER accounts or Q to quit' -ForegroundColor Yellow
    ''
    $orp=Read-Host 'Enter (U/C)'
    If ($orp -eq 'Q')

    {Break}

    ''

    Write-Host 'Enter time span in DAYS in which USERS or COMPUTERS have not logged on since today. Example: If you enter 365 days, the system searches for all users/computers who have not logged on for a year.' -ForegroundColor Yellow
    ''
    
    $span=Read-Host 'Timespan'


    If ($orp -eq 'U') {

    ''

    Write-Host "The following USERS are enabled and have not logged on for $span days:" -ForegroundColor Green

    Get-ADUser -Filter 'enabled -ne $false' -Properties LastLogonDate,whenCreated | Where-Object {$_.lastlogondate -ne $null -and $_.lastlogondate -le ((get-date).adddays(-$span))} | Format-Table Name,SamAccountName,LastLogonDate,whenCreated
    
    Write-Host 'User and Computer Logons are replicated every 14 days. Data might be not completely up-to-date.' -ForegroundColor Yellow
    ''
    Read-Host 'Press 0 and Enter to continue'
    
    }

    If ($orp -eq 'C') {

    ''

    Write-Host "The following COMPUTERS are enabled have not logged on for $span days:" -ForegroundColor Green

    Get-ADComputer -Filter 'enabled -ne $false' -Properties LastLogonDate,whenCreated | Where-Object {$_.lastlogondate -ne $null -and $_.lastlogondate -le ((get-date).adddays(-$span))} | Format-Table Name,SamAccountName,LastLogonDate,whenCreated
    
    Write-Host 'User and Computer Logons are replicated every 14 days. Data might be not completely up-to-date.' -ForegroundColor Yellow
    ''
    Read-Host 'Press 0 and Enter to continue'
    
    }
        
}

20 {

    $checkF=(Get-ADForest).ForestMode
    $opt=Get-ADOptionalFeature -Identity "Privileged Access Management Feature"

    ''

    If (($checkF -like '*2016*') -or ($checkF -like '*2019*') -and ($opt))

    {


    ''

    Write-Host "Forest mode is $checkF. Privileged Access Management Feature enabled. Everything's fine. Moving on ..." -ForegroundColor Green
    ''
    Write-Host "This section configures Time-Based-Group-Membership. Provide User, Group and Timespan." -ForegroundColor Green
    ''

    do {

    Write-Host 'Enter USER LOGON Name for Time-Based-Group-Membership or press Q to quit.' -ForegroundColor Yellow
    ''

    $user=Read-Host "USER LOGON Name"
    If ($user -eq 'Q') {Break}
    $ds=dsquery user -samid $user

    ''

    If ($ds)

    {

    Write-Host "User $user found!" -ForegroundColor Green

    }

    else 

    {


    Write-Host "User $user not found. Try again" -ForegroundColor Red}
    ''
    }

    while (!$ds)

    do {

    If ($user -eq 'Q') {Break}

    Write-Host 'Enter GROUP Name for Time-Based-Group-Membership or press Q to quit.' -ForegroundColor Yellow
    ''

    $group=Read-Host "GROUP Name"
    If ($group -eq 'Q') {Break}
    $dsg=dsquery group -samid $group
    ''
    If ($dsg)

    {

    Write-Host "Group $group found!" -ForegroundColor Green

    }

    else 

    {


    Write-Host "Group $group not found. Try again" -ForegroundColor Red}
    ''

    

    If ($group -eq 'Q')
    {Break}

    }

    while (!$dsg)

    If (($user -eq 'Q') -or ($group -eq 'Q')) {Break}

    Write-Host 'Enter timespan for Group Membership in HOURS or Q to quit' -ForegroundColor Yellow
    ''

    $timegpm=Read-Host 'TIMESPAN'
    If ($timegpm -eq 'Q')
    {Break}

    Add-ADGroupMember -Identity "$group" -Members $user -MemberTimeToLive (New-TimeSpan -Hours $timegpm)
    ''
    Write-Host "Here's your configuration:" -ForegroundColor Yellow
    ''
    $groupup=$group.ToUpper()
    Write-Host "Time-Based-Group-Membership for $groupup" -ForegroundColor Green
    ''
    Get-ADGroup $group -Properties Member -ShowMemberTimeToLive | Select-Object Name -ExpandProperty Member | Where-Object {($_ -like '*TTL*')}
    Write-Host ''
    Read-Host 'Press 0 and Enter to continue'
      }
    
    else 

    {
    ''
    $fname=(Get-ADForest).Name
    Write-Host "Operation aborted." -ForegroundColor Red
    ''
    Write-Host "The forest $fname does not meet the minimum requirements (Windows Server 2016 Forest Mode) and/or the Privileged Access Management Feature is not enabled. Solution: Upgrade all Domain Controllers to Windows Server 2016, then raise the Forest Level and activate Privileged Access Management." -ForegroundColor Yellow
    ''
    Read-Host 'Press 0 and Enter to continue'
    }

    }

 21 {
    ''
    Write-Host "This menu item creates a new AD User based on an existing one for the domain $env:userdnsdomain." -ForegroundColor Green
    
    ''
    do {

    Write-Host 'Enter LOGON NAME of an EXISTING USER to copy (Q to quit)' -ForegroundColor Yellow
    ''
    $nameds = Read-Host "LOGON NAME (existing user)"

    If ($nameds -eq 'Q') {Break}
    
    If (dsquery user -samid $nameds) {
    '' 
    Write-host -ForegroundColor Green "AD User $nameds found!"}


    elseif ($nameds = "null") {
    ''
    Write-Host "User not found. Please try again." -ForegroundColor Red
    ''}

    }
    while ($nameds -eq "null")

    If ($nameds -eq 'Q') {Break}

    $name = Get-AdUser -Identity $nameds -Properties *

    $DN = $name.distinguishedName
    $OldUser = [ADSI]"LDAP://$DN"
    $Parent = $OldUser.Parent
    $OU = [ADSI]$Parent
    $OUDN = $OU.distinguishedName
    Write-Host ''
    Write-Host 'Enter the LOGON NAME of the NEW USER' -ForegroundColor Yellow
    ''
    $NewUser = Read-Host "LOGON NAME (new user)"
    $firstname = Read-Host "First Name"
    $Lastname = Read-Host "Last Name"
    $NewName = "$firstname $lastname"
    $domain = [System.DirectoryServices.ActiveDirectory.Domain]::GetCurrentDomain() 
    $prof = $name.ProfilePath

    ''
    Write-Host "Are you sure you want to create user $firstname $lastname with the logon name $newuser and copy properties from $nameds to $newuser (Y/N)" -ForegroundColor Yellow
    ''
    
    $surely=Read-Host "Enter (Y/N)"

    If ($surely -eq 'y')

    {

    New-ADUser -SamAccountName $NewUser -Name $NewName -GivenName $firstname -displayname "$firstname $lastname" -Surname $lastname -Instance $DN -Path "$OUDN" -AccountPassword (Read-Host "Enter Password for $firstname $lastname" -AsSecureString) –userPrincipalName $NewUser@$domain -Company $name.Company -Department $name.Department -Manager $name.Manager -title $name.Title -Office $name.Office -City $name.city -PostalCode $name.postalcode -Country $name.country -Fax $name.fax -State $name.State -StreetAddress $name.StreetAddress -Enabled $true -ProfilePath ($prof -replace $name.SamAccountName, $NewUser) -HomePage $name.wWWHomePage -ScriptPath $name.ScriptPath
    Set-ADUser -identity $newUser -ChangePasswordAtLogon $true

    ''

    Write-Host "Copying Group Memberships, Profile Path, Logon Script and more ..."
   

    $groups = (Get-ADUser –Identity $name –Properties MemberOf).MemberOf
    foreach ($group in $groups) {

    Add-ADGroupMember -Identity $group -Members $NewUser
    }
    ''
    Write-Host 'The following user has been created by the Active Directory Services Section Tool:' -ForegroundColor Green
    
    Get-ADUser $NewUser -Properties * | Format-List GivenName,SurName,CanonicalName,Enabled,ProfilePath,ScriptPath,MemberOf,whencreated
    }

    else {Break}

    Read-Host 'Press 0 and Enter to continue'
}

 22 {

    ''
    Write-Host "This menu item deactivates an AD User in the domain $env:userdnsdomain." -ForegroundColor Yellow
    
    ''

    do {
     
     $a=Read-Host 'Enter LOGON NAME of the user to be deactivated (Q to quit)'
     
     If ($a -eq 'Q') {Break}
     
     If (dsquery user -samid $a)
     
     {
     ''
     Write-host -foregroundcolor Green "AD User $a found!"
     
     }

    elseif ($a = "null") {
    ''
    Write-Host -ForegroundColor Red "AD User not found. Please try again."
    ''}
     }
     while ($a -eq "null")

    If ($a -eq 'Q') {Break}

    
    $det=((Get-ADuser -Identity $a).GivenName + ' ' + (Get-ADUser -Identity $a).SurName)
    
    ''
    Write-Host "User $det will be deactivated. Are you sure? (Y/N)" -ForegroundColor Yellow
    ''
    $sure=Read-Host 'Enter (Y/N)'

    If ($sure -eq 'Y')

    {

    Get-ADUser -Identity "$a" | Set-ADUser -Enabled $false

    ''

    Write-Host -ForegroundColor Green "User $a has been deactivated."

    ''

    $b=Read-Host "Do you want to remove all group memberships from that user ($a)? (Y/N)"

    If ($b -eq 'Y') {

    $ADgroups = Get-ADPrincipalGroupMembership -Identity "$a" | where {$_.Name -ne 'Domain Users'}

    If ($ADgroups -ne $null) {Remove-ADPrincipalGroupMembership -Identity "$a" -MemberOf $ADgroups -Confirm:$false -WarningAction SilentlyContinue -ErrorAction Ignore
    }

    }
    
    }

    else {Break}
    ''

    
    Write-Host 'The following user has been deactivated by the Active Directory Services Section Tool:' -ForegroundColor Green

    Get-ADUser $a -Properties * | Format-List GivenName,SurName,DistinguishedName,Enabled,MemberOf,LastLogonDate,whencreated

    Read-Host 'Press 0 and Enter to continue'
}


}

}

while ($input -ne '0')

}
