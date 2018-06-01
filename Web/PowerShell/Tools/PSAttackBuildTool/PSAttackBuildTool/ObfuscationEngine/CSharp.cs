using System;
using System.IO;
using System.Collections.Generic;
using System.Text.RegularExpressions;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

using PSAttackBuildTool;
using PSAttackBuildTool.Utils;
using PSAttackBuildTool.PSAttack;

namespace PSAttackBuildTool.ObfuscationEngine
{
    class CSharp
    {        
        static Dictionary<String,String> VariableKey { get; set; }

        static public string ProcessSource(string sourcePath, GeneratedStrings rulesStrings, GeneratedStrings keyStoreStrings, Attack attack)
        {
            // To make sure that we obfuscate and then save the file while maintaining directory structure
            // we do some string chopping here. TODO: Clean this up


            string originalFileName = Path.GetFileName(sourcePath);
            string readScript = File.ReadAllText(sourcePath);
            string obfuscatedSourcePath = sourcePath.Replace(attack.unzipped_dir, Strings.obfuscatedSourceDir);
            string fileStub = obfuscatedSourcePath.Replace(Strings.obfuscatedSourceDir, "");

            foreach (KeyValuePair<string, string> rule in rulesStrings.Store)
            {
                fileStub = fileStub.Replace(rule.Key, rule.Value);
            }

            obfuscatedSourcePath = Path.Combine(Strings.obfuscatedSourceDir, fileStub);
            //obfuscatedSourcePath = obfuscatedSourcePath.Replace("AttackState", generatedStrings.Store["attackStateReplacement"]);
            //obfuscatedSourcePath = obfuscatedSourcePath.Replace("PSParam", generatedStrings.Store["psparamReplacement"]);

            // Process Rules
            FileInfo file = new System.IO.FileInfo(obfuscatedSourcePath);
            file.Directory.Create();
            if (!(sourcePath.Contains(keyStoreStrings.Store["keyStoreFileName"]) || (sourcePath.Contains("Modules"))))
            {
                foreach (KeyValuePair<string,string> rule in rulesStrings.Store)
                {
                    Display.PrimaryMessage($"Checking for instances of {rule.Key} in file.");
                    readScript = RuleProcessor(rule, readScript);
                }
                File.WriteAllText(obfuscatedSourcePath, readScript);
            }
            else
            {
                File.Copy(sourcePath, obfuscatedSourcePath, true);
            }
            return obfuscatedSourcePath;
        }

        static private string RuleProcessor(KeyValuePair<string,string> rule, String scriptContents)
        {
            string modifiedContents = "";
            Regex regex = new Regex(rule.Key, RegexOptions.IgnoreCase);
            string replacementText = rule.Value;
            Display.SecondaryMessage($"Replacing {rule.Key} with {replacementText}");
            modifiedContents = regex.Replace(scriptContents, replacementText);
            


            //if (rule.Type == "ReplaceList")
            //{
            //    Display.Message("Running ReplaceList Rule '" + rule.Name + "'");
            //    VariableKey = new Dictionary<string, string>();
            //    Regex regex = new Regex(rule.Trigger, RegexOptions.IgnoreCase);
            //    List<string> safeVars = new List<string>(new string[] { "true", "false", "null", "error" });
            //    string replacementText = rule.Action;
            //    Match hit = regex.Match(scriptContents);
            //    modifiedContents = scriptContents;
            //    while (hit.Success)
            //    {
            //        if (safeVars.Contains(hit.Value.Replace("$", "").ToLower()))
            //        {
            //            replacementText = null;
            //        }
            //        else if (VariableKey.ContainsKey(hit.Value))
            //        {
            //            Display.updateSecondaryMessage("Found hit for key:" + hit.Value);
            //            replacementText = VariableKey[hit.Value];
            //        }
            //        else
            //        {
            //            Display.updateSecondaryMessage("Creating new string for key:" + hit.Value);
            //            replacementText = rule.Action.Replace("#RANDOM", PSABTUtils.RandomString(32, rand));
            //            VariableKey.Add(hit.Value, replacementText);
            //        }
            //        if (replacementText != null)
            //        {
            //            Display.updateSecondaryMessage("Replacing " + hit.Value + " with " + replacementText);
            //            string variable_match = @"(\$)" + hit.Value.Replace("$", "");
            //            Regex regex_step2 = new Regex(variable_match, RegexOptions.IgnoreCase);
            //            modifiedContents = regex_step2.Replace(modifiedContents, replacementText);
            //        }
            //        else
            //        {
            //            Display.updateSecondaryMessage("Safe variable  " + hit.Value + " found. Not replacing.");
            //        }
            //        hit = hit.NextMatch();
            //    }

            //}
            return modifiedContents;
        }

        static public GeneratedStrings CreateRules()
        {
            GeneratedStrings rulesStrings = new GeneratedStrings();
            rulesStrings.AddValue("PSAttack");
            rulesStrings.AddValue("PS>Attack");
            rulesStrings.AddValue("PS Attack!!!");
            rulesStrings.AddValue("PSParam");
            rulesStrings.AddValue("AttackState");
            rulesStrings.AddValue("PSInit");
            rulesStrings.AddValue("PSExec");
            rulesStrings.AddValue("displayCmd");
            rulesStrings.AddValue("paramAutoComplete");
            rulesStrings.AddValue("variableAutoComplete");
            rulesStrings.AddValue("pathAutoComplete");
            rulesStrings.AddValue("cmdAutoComplete");
            rulesStrings.AddValue("seedIdentification");
            rulesStrings.AddValue("dislayCmdComponents");
            rulesStrings.AddValue("PSColors");
            rulesStrings.AddValue("DecryptString");
            rulesStrings.AddValue("DecryptFile");
            rulesStrings.AddValue("CryptoUtils");
            rulesStrings.AddValue("createPrompt");
            rulesStrings.AddValue("ImportModules");
            rulesStrings.AddValue("encryptionKey");
            rulesStrings.AddValue("valueStore");
            rulesStrings.AddValue("autocompleteSeed");
            rulesStrings.AddValue("cmdComplete");
            rulesStrings.AddValue("promptLength");
            rulesStrings.AddValue("decryptedStore");
            rulesStrings.AddValue("psaLogos");
            return rulesStrings;
        }
    }
}
