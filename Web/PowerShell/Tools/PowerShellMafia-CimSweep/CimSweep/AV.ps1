Function Get-CSAVInfo
{
<#    
.SYNOPSIS

此功能枚举安装在远程主机上的防病毒和任何有用的注册表项。

Author: Chris Ross (@xorrior)
License: BSD 3-Clause

.DESCRIPTION

Get-CSAVInfo使用AntiVirusProduct WMI类枚举本地或远程主机上的防病毒软件，包含的名称，可执行文件路径，状态和注册表项在自定义PowerShell对象中返回。
	
.PARAMETER CimSession

指定用于此cmdlet的CIM会话。输入包含CIM会话的变量或创建或获取CIM会话的命令，例如New-CimSession或Get-CimSession cmdlet。 有关更多信息，请参阅about_CimSessions。
.EXAMPLE

Get-CimAVInfo

.EXAMPLE

Get-CimAVInfo -Session $CimSession

.OUTPUTSGet-CSAVInfo

CimSweep.AVInfo

输出代表当前反病毒软件配置的自定义对象。
#>
	
	[CmdletBinding()]
	[OutputType('CimSweep.AVInfo')]
	param
	(
		[Alias('Session')]
		[ValidateNotNullOrEmpty()]
		[Microsoft.Management.Infrastructure.CimSession[]]$CimSession
	)
	
	
	BEGIN
	{
		if (-not $PSBoundParameters['CimSession'])
		{
			$CimSession = ''
		}
	}
	
	PROCESS
	{
		foreach ($Session in $CimSession)
		{
			$ComputerName = $Session.ComputerName
			#如果远程会话不返回计算机名，则在本机执行
			if (-not $Session.ComputerName) { $ComputerName = 'localhost' }
			
			#初始化一个散列表保存命令行参数
			$CommonArgs = @{ }
			$InstanceArgs = @{ }
			$InstanceArgs['ClassName'] = 'AntiVirusProduct'
			
			#检查是否指定了会话
			if ($Session.Id) { $CommonArgs['CimSession'] = $Session }
			
			#确定命名空间是否存在
			if (Get-CimInstance -Namespace root -ClassName __NAMESPACE -Filter 'Name="SecurityCenter2"' @CommonArgs)
			{
				$InstanceArgs['Namespace'] = 'root/SecurityCenter2'
			}
			elseif (Get-CimInstance -Namespace root -ClassName __NAMESPACE -Filter 'Name="SecurityCenter"' @CommonArgs)
			{
				$InstanceArgs['Namespace'] = 'root/SecurityCenter'
			}
			else
			{
				Write-Error "[$ComputerName] SecurityCenter2和SecurityCenter名称空间都不存在."
				break
			}
			
			$AV = Get-CimInstance @InstanceArgs @CommonArgs
			
			if ($InstanceArgs['NameSpace'] -eq 'root/SecurityCenter2')
			{
				$ObjectProperties = [Ordered] @{
					PSTypeName  = 'CimSweep.AVInfo'
					Name	    = $AV.displayName
					Executable  = $AV.pathToSignedProductExe
					InstanceGUID = $AV.instanceGuid
					ScannerEnabled = $null
					Updated	    = $null
					ExclusionInfo = $null
				}
				
				#解析productState的字节值
				#解码productState属性为十六进制值
				$state = '{0:X6}' -f $AV.productState
				#我本机的productState为262144，十六进制值为040000。
				#获取040000的第二位和第三位值，00代表关闭，10代表开启。
				$scanner = $state[2, 3] -join '' -as [byte] #判断是防病毒否开启
				#最后2个00将指示产品是否是最新的，值为00意味着它是最新的。
				$updated = $state[4, 5] -join '' -as [byte]#判断防病毒软件是否是最新的
				
				#如果productState的十六进制值第二位和第三位值匹配10代表反病毒软件被启用
				#00则为关闭状态
				if ($scanner -ge (10 -as [byte]))
				{
					$ObjectProperties.ScannerEnabled = $True
				}
				elseif ($scanner -eq (00 -as [byte]) -or $scanner -eq (01 -as [byte]))
				{
					$ObjectProperties.ScannerEnabled = $False
				}
				
				#如果productState的十六进制值最后2位匹配00代表反病毒软件是最新的，反之亦然。
				#确定反病毒软件是否是最新的
				if ($updated -eq (00 -as [byte]))
				{
					$ObjectProperties.Updated = $True
				}
				elseif ($updated -eq (10 -as [byte]))
				{
					$ObjectProperties.Updated = $False
				}
				
				if ($Session.ComputerName) { $ObjectProperties['PSComputerName'] = $Session.ComputerName }
				
				$AntiVirus = [PSCustomObject]$ObjectProperties
			}
			else
			{
				$ObjectProperties = [Ordered] @{
					PSTypeName  = 'CimSweep.AVInfo'
					Name	    = $AV.displayName
					Executable  = $AV.pathToEnableOnAccessUI
					InstanceGUID = $AV.instanceGuid
					ScannerEnabled = $AV.onAccessScanningEnabled
					Updated	    = $AV.productUptoDate
					ExclusionInfo = $null
					PSComputerName = $Session.ComputerName
				}
				
				if ($Session.ComputerName) { $ObjectProperties['PSComputerName'] = $Session.ComputerName }
				
				$AntiVirus = [PSCustomObject]$ObjectProperties
			}
			
			
			#获取反病毒软件排除项，白名单问件和文件夹
			$DefenderPaths = @{
				ExcludedPaths	    = 'SOFTWARE\Microsoft\Windows Defender\Exclusions\Paths\'
				ExcludedExtensions  = 'SOFTWARE\Microsoft\Windows Defender\Exclusions\Extensions\'
				ExcludedProcesses   = 'SOFTWARE\Microsoft\Windows Defender\Exclusions\Processes\'
			}
			
			$McAfeePaths = @{
				Exclusions			      = 'SOFTWARE\McAfee\AVSolution\OAS\DEFAULT\'
				EmailIncludedProcesses    = 'SOFTWARE\McAfee\AVSolution\OAS\EMAIL\'
				ProcessStartupExclusions  = 'SOFTWARE\McAfee\AVSolution\HIP\'
			}
			
			if ($AntiVirus.Name -match 'Windows Defender')
			{
				$ExclusionInfo = [PSCustomObject] @{ }
				$DefenderPaths.GetEnumerator() | ForEach-Object {
					$ExclusionInfo | Add-Member -NotePropertyName $_.Key -NotePropertyValue $(Get-CSRegistryValue -Hive HKLM -SubKey $($_.Value) @CommonArgs).ValueName
				}
				
			}
			elseif ($AntiVirus.Name -match 'McAfee')
			{
				$ExclusionInfo = [PSCustomObject] @{ }
				$McAfeePaths.GetEnumerator() | ForEach-Object {
					$ExclusionInfo | Add-Member -NotePropertyName $_.Key -NotePropertyValue $(Get-CSRegistryValue -Hive HKLM -SubKey $($_.Value) @CommonArgs).ValueName
				}
			}
			
			$AntiVirus.ExclusionInfo = $ExclusionInfo
			
			$AntiVirus
		}
	}
}
Get-CSAVInfo
