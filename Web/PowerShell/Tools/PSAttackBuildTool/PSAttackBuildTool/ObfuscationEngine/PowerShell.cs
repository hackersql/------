using System;
using System.IO;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Net;
using System.Management.Automation;
using PowerShell = System.Management.Automation.PowerShell;

using PSAttackBuildTool.Utils;

namespace PSAttackBuildTool.ObfuscationEngine
{
    class Posh
    {

        static public void DownloadInvokeObfuscation()
        {
            WebClient wc = new WebClient();
            wc.Headers.Add("user-agent", Strings.githubUserAgent);
            wc.DownloadFile(Strings.invokeObfuscationURL, Strings.invokeObfuscationZipPath);
            PSABTUtils.UnzipFile(Strings.invokeObfuscationZipPath, Strings.invokeObfuscationDir);
        }

        static public string InvokeObfuscation(string source, bool file=false)
        {
            List<string> obfuscationCommands = new List<string>();
            obfuscationCommands.Add(@"TOKEN\COMMAND\3,TOKEN\ARGUMENT\3,TOKEN\ARGUMENT\4,TOKEN\MEMBER\4,TOKEN\VARIABLE\1,TOKEN\COMMENT\1");
            obfuscationCommands.Add(@"TOKEN\COMMAND\1,TOKEN\ARGUMENT\4,TOKEN\MEMBER\4,TOKEN\COMMENT\1");
            obfuscationCommands.Add(@"TOKEN\COMMAND\1,TOKEN\COMMENT\1");

            string result = "";
            bool success = false; // We'll use this to track successful obfuscation.


            foreach (string obfuscationCommand in obfuscationCommands)
            {
                string cmd = $"Invoke-Obfuscation -ScriptBlock {source} -Command '{obfuscationCommand}' -Quiet";

                if (file && File.Exists(source))
                {
                    cmd = $"Invoke-Obfuscation -ScriptPath '{source}' -Command '{obfuscationCommand}' -Quiet";
                }
                if (file && !File.Exists(source))
                {
                    Display.ErrorMessage($"Could not find {source}! Check to see if the file exists.");
                    return "ERROR";
                }

                Display.SecondaryMessage($"Trying obfuscation with the following command: \n\n{cmd}");

                try
                {
                    PowerShell ps = PowerShell.Create();
                    ps.AddScript("Import-Module " + Strings.invokeObfuscationModulePath);
                    ps.Invoke();
                    ps.AddScript(cmd);
                    result = ps.Invoke()[0].ToString();
                }
                catch
                {
                    Display.ErrorMessage($"Obfuscation for {source} failed with {cmd}");
                    return "ERROR";
                }


                if (result == "")
                {
                    Display.ErrorMessage($"Obfuscation for {source} returned an empty string. Maybe AV ate it before it could be obfuscated?");
                    return "ERROR";
                }

                // Create a new, clean PowerShell runspace to test the obfuscated script
                try
                {
                    PowerShell detChamber = PowerShell.Create();
                    detChamber.AddScript(result);
                    detChamber.Invoke();
                    if (detChamber.Streams.Error.Count > 0)
                    {
                        Display.SecondaryMessage($"Obfuscation command {obfuscationCommand} failed. Trying next in list.");
                    }
                    else if (detChamber.Streams.Error.Count == 0)
                    {
                        Display.SecondaryMessage($"Obfuscation command {obfuscationCommand} succeeded.");
                        success = true;
                        break;
                    }
                }
                catch
                {
                    Display.SecondaryMessage($"Obfuscation command {obfuscationCommand} failed. Trying next in list.");
                    return "ERROR";
                }
            }

            if (!success)
            {
                if (file)
                {
                    Display.ErrorMessage($"Obfuscation failed for {source}.", exceptionMessage: null, secondaryMessage: "Press enter to included the un-obfuscated source into your PS>Attack build");
                }
                else
                {
                    Display.ErrorMessage($"Obfuscation failed for command: {source}.", exceptionMessage: null, secondaryMessage: "Press enter to included the un-obfuscated command into your PS>Attack build");
                }
                result = source; // Set result to unobfuscated source
            }

            if (file) // if file, write to file and return path
            {
                string destination = Path.Combine(Strings.obfuscatedScriptsDir, Path.GetFileName(source));
                if (!success) // If obfuscation hasn't sucessfully run, we'll just copy the original file over
                {
                    File.Copy(result, destination);
                }
                else
                {
                    File.WriteAllText(destination, result);
                }
                return destination;
            }
            else // else, return obfuscated command
            {
                return result;
            }
            
        }
    }
}
