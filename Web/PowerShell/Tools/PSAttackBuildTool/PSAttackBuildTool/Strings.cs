using System;
using System.IO;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using PSAttackBuildTool.Utils;

namespace PSAttackBuildTool
{
    class Strings
    {
        public static string version = "1.9.1";
        public static string githubUserAgent = "PSAttackBuildTool";
        public static string releasesURL = "https://api.github.com/repos/jaredhaight/psattack/releases";
        public static string masterURL = "https://github.com/jaredhaight/PSAttack/archive/master.zip";
        public static string devURL = "https://github.com/jaredhaight/PSAttack/archive/dev.zip";
        public static string attackUnzipDir = Path.Combine(PSABTUtils.GetPSAttackBuildToolDir(), "PSAttackSrc") + "\\";
        public static string attackZipPath = Path.Combine(PSABTUtils.GetPSAttackBuildToolDir(), "PSAttack.zip");
        public static string moduleSrcDir = Path.Combine(PSABTUtils.GetPSAttackBuildToolDir(), "ModuleSrc") + "\\";
        public static string obfuscatedScriptsDir = Path.Combine(PSABTUtils.GetPSAttackBuildToolDir(), "ObfuscatedScripts") + "\\";
        public static string obfuscatedSourceDir = Path.Combine(PSABTUtils.GetPSAttackBuildToolDir(), "ObfuscatedSource") + "\\";
        public static string invokeObfuscationDir = Path.Combine(PSABTUtils.GetPSAttackBuildToolDir(), "InvokeObfuscation") + "\\";
        public static string invokeObfuscationZipPath = Path.Combine(PSABTUtils.GetPSAttackBuildToolDir(), "InvokeObfuscation.zip");
        public static string invokeObfuscationURL = "https://github.com/danielbohannon/Invoke-Obfuscation/archive/master.zip";
        public static string invokeObfuscationModulePath = Path.Combine(invokeObfuscationDir, "Invoke-Obfuscation-master", "Invoke-Obfuscation.psd1");
        public static string attackModulesDir = "PSAttack\\Modules\\";
        public static string attackResourcesDir = "PSAttack\\Resources\\";
        public static string attackCSProjFile = "PSAttack\\PSAttack.csproj";
        public static string attackConfigFile = "PSAttack\\app.config";
        public static string attackSettingsDesignerFile = "PSAttack\\Properties\\Settings.Designer.cs";
        public static string attackBuildDir = "\"" + Path.Combine(PSABTUtils.GetPSAttackBuildToolDir(), "PSAttackBuild") + "\"";
        public static List<string> psabtLogos = new List<string>()
        {
@"
  _____   _______       _______ _______       _____ _  __
 |  __ \ / ____\ \   /\|__   __|__   __|/\   / ____| |/ /
 | |__) | (___  \ \ /  \  | |     | |  /  \ | |    | ' / 
 |  ___/ \___ \  > / /\ \ | |     | | / /\ \| |    |  <  
 | |     ____) |/ / ____ \| |     | |/ ____ | |____| . \ 
 |_|    |_____//_/_/    \_|_|     |_/_/    \_\_____|_|\_\
                                             [BUILD TOOL]
",
@"
 (   (                                           )  
 )\ ))\ )   (      *   ) *   )   (       (    ( /(  
(()/(()/(   )\   ` )  /` )  /(   )\      )\   )\()) 
 /(_)/(_)((((_)(  ( )(_)( )(_)((((_)(  (((_)|((_)\  
(_))(_))__)\ _ )\(_(_()(_(_()) )\ _ )\ )\___|_ ((_) 
| _ / __\ (_)_\(_|_   _|_   _| (_)_\(_((/ __| |/ /  
|  _\__ \> / _ \   | |   | |    / _ \  | (__  ' <   
|_| |___/_/_/ \_\  |_|   |_|   /_/ \_\  \___|_|\_\ 
         \/\/\/\/ BUILD TOOL \/\/\/\/
",
@"
           __                                       
 _____ ____\ \  _____ _____ _____ _____ _____ _____ 
|  _  |   __\ \|  _  |_   _|_   _|  _  |     |  |  |
|   __|__   |> |     | | |   | | |     |   --|    -|
|__|  |_____/ /|__|__| |_|   |_| |__|__|_____|__|__|
           /_/                            BUILD TOOL                

",
@"
   ___  _____   ___ _______________  _______ __
  / _ \/ __\ \ / _ /_  __/_  __/ _ |/ ___/ //_/
 / ____\ \  > / __ |/ /   / / / __ / /__/ ,<   
/_/  /___/ /_/_/ |_/_/   /_/ /_/ |_\___/_/|_|  
               ///BUILD TOOL///
",
@"
 ######   #####  #       #    ####### #######    #     #####  #    # 
 #     # #     #  #     # #      #       #      # #   #     # #   #  
 #     # #         #   #   #     #       #     #   #  #       #  #   
 ######   #####     # #     #    #       #    #     # #       ###    
 #             #   #  #######    #       #    ####### #       #  #   
 #       #     #  #   #     #    #       #    #     # #     # #   #  
 #        #####  #    #     #    #       #    #     #  #####  #    # 
                          BUILD TOOL
                                                                     
",
@"
 ____    ____     __    ______  ______ ______ ______  ____    __  __     
/\  _`\ /\  _`\  /\ `\ /\  _  \/\__  _/\__  _/\  _  \/\  _`\ /\ \/\ \    
\ \ \L\ \ \,\L\_\\ `\ `\ \ \L\ \/_/\ \\/_/\ \\ \ \L\ \ \ \/\_\ \ \/'/'   
 \ \ ,__/\/_\__ \ `\ >  \ \  __ \ \ \ \  \ \ \\ \  __ \ \ \/_/\ \ , <    
  \ \ \/   /\ \L\ \ /  / \ \ \/\ \ \ \ \  \ \ \\ \ \/\ \ \ \L\ \ \ \\`\  
   \ \_\   \ `\____/\_/   \ \_\ \_\ \ \_\  \ \_\\ \_\ \_\ \____/\ \_\ \_\
    \/_/    \/_____\//     \/_/\/_/  \/_/   \/_/ \/_/\/_/\/___/  \/_/\/_/
                                                     \\\\\BUILD TOOL\\\\\
",
@"
  _   __       ___ ___      _    
 |_) (_  \  /\  |   |  /\  /  |/ 
 |   __) / /--\ |   | /--\ \_ |\ 
         (build tool)                       
",
@"
 ______   ______    _______ _______ _______ _______ _______ _     _ 
(_____ \ / _____)_ (_______(_______(_______(_______(_______(_)   | |
 _____) ( (____ ( \ _______    _       _    _______ _       _____| |
|  ____/ \____ \ ) |  ___  |  | |     | |  |  ___  | |     |  _   _)
| |      _____) (_/| |   | |  | |     | |  | |   | | |_____| |  \ \ 
|_|     (______/   |_|   |_|  |_|     |_|  |_|   |_|\______|_|   \_)
                            BUILD TOOL                                                                    
",
@"
      ___      ___         ___                          ___         ___         ___     
     /  /\    /  /\       /  /\        ___      ___    /  /\       /  /\       /__/|    
    /  /::\  /  /:/_     /  /::\      /  /\    /  /\  /  /::\     /  /:/      |  |:|    
   /  /:/\:\/  /:/ /\   /  /:/\:\    /  /:/   /  /:/ /  /:/\:\   /  /:/       |  |:|    
  /  /:/~/:/  /:/ /::\ /  /:/~/::\  /  /:/   /  /:/ /  /:/~/::\ /  /:/  ___ __|  |:|    
 /__/:/ /:/__/:/ /:/\:/__/:/ /:/\:\/  /::\  /  /::\/__/:/ /:/\:/__/:/  /  //__/\_|:|____
 \  \:\/:/\  \:\/:/~/:\  \:\/:/__\/__/:/\:\/__/:/\:\  \:\/:/__\\  \:\ /  /:\  \:\/:::::/
  \  \::/  \  \::/ /:/ \  \::/    \__\/  \:\__\/  \:\  \::/     \  \:\  /:/ \  \::/~~~~ 
   \  \:\   \__\/ /:/   \  \:\         \  \:\   \  \:\  \:\      \  \:\/:/   \  \:\     
    \  \:\    /__/:/     \  \:\         \__\/    \__\/\  \:\      \  \::/     \  \:\    
     \__\/    \__\/       \__\/                        \__\/       \__\/       \__\/    
                                     
                                    [BUILD TOOL]
",
@"
   _ \    ___| \ \     \     |    |                 |     | 
  |   | \___ \  \ \   _ \    __|  __|   _` |   __|  |  /  | 
  ___/        |   /  ___ \   |    |    (   |  (       <  _| 
 _|     _____/  _/ _/    _\ \__| \__| \__,_| \___| _|\_\ _) 
                                               [build tool]
"
        };
        public static string psaStartMsg = @"
 The PS>Attack Build Tool downloads a copy of PS>Attack, downloads the latest versions of
 the files in modules.json, encrypts them and then compiles PS>Attack with these new and 
 unique files. Antivirus software (including Windows Defender) may flag the downloaded 
 files as malicious.  If you run into issues with these files you will have to configure
 your AV software to allow them to be downloaded or remove them from modules.json.

 The PS>Attack Build Tool relies on a full install of .NET 3.5. Targeting 3.5 allows 
 PS>Attack to work on Windows 7 and up. If you encounter build errors, the first thing 
 you should do is make sure you have the full version of .NET 3.5 installed. Google (or 
 Duck Duck Go, or Bing, etc) is your friend.";

        public static string psaWarningMsg = @"
 WARNING: This build tool downloads various PowerShell modules from  sources on the 
 internet with the goal of executing them within PS>Attack. For the most part, these 
 files come from developers with established reputations who probably aren't jerks. As 
 always though, there is risk involved in downloading code blindly from the internet and 
 running it. You can customize the modules.json file to decide what code is downloaded 
 and from where.

 To verify that scripts still work after being obfuscated, this build tool attempts to 
 run the obfuscated file/command in a PowerShell runspace. It does not invoke any
 functions from the scripts, it simply verifies that they load successfully. This is the
 same behavior as if you'd run PS>Attack on your own computer and not entered any 
 commands. If you'd like to disable this behavior, set 'obfuscatePowerShell' to false in
 the config file.";

        public static string psaEndSuccess = @"
 Build complete! Your build of PS>Attack is available at: 

 {0}

 You'll need the PSAttack.exe and PSAttack.exe.config files, the 
 others are extra from the build process. PSAttack.exe should be
 run from the same folder that has the config file.

 Press return to open up the folder. Thanks for using PS>Attack!
";
        public static string psaEndNoMSBuild = @"
 Hrm.. we couldn't find MSBuild.exe. That _should_ be here:

 {0}

 At least, that's where we were Windows is telling us your
 .NET install is (which should contain MSBuild.exe). Get
 MSBuild and then try again!

 Press return to close this window.
 ";
        public static string psaEndFailure = @"
 Oh no! It looks like the build failed. You should check the build
 output above and see if there's an obvious issue. If you can't 
 resolve the problem on your own, go ahead and submit an issue  at
 https://github.com/jaredhaight/psattackbuildtool/issues/ and maybe 
 I can help. Make sure to include the output from the build process 
 (the gray text starting with 'Running build with this command:' up
 to this error message)

 Press return to close this window.
 ";
    }
}

