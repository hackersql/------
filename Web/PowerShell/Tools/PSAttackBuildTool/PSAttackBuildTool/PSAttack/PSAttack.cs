using System;
using System.IO;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Net;
using System.Runtime.Serialization;
using System.Configuration;

using PSAttackBuildTool.Utils;

namespace PSAttackBuildTool.PSAttack
{
    [DataContract]
    class Attack
    {
        [DataMember]
        public string Name { get; set; }
        [DataMember]
        public string tag_name { get; set; }
        [DataMember]
        public string zipball_url { get; set; }
        [DataMember]
        public string published_at { get; set; }

        public string unzipped_dir { get; set; }

        public string modules_dir
        {
            get
            {
                return Path.Combine(this.unzipped_dir, Strings.attackModulesDir);
            }
        }

        public string resources_dir
        {
            get
            {
                return Path.Combine(this.unzipped_dir, Strings.attackResourcesDir);
            }
        }

        public string csproj_file
        {
            get
            {
                return Path.Combine(this.unzipped_dir, Strings.attackCSProjFile);
            }
        }

        public string config_file
        {
            get
            {
                return Path.Combine(this.unzipped_dir, Strings.attackConfigFile);
            }
        }
        public string settings_designer_file
        {
            get
            {
                return Path.Combine(this.unzipped_dir, Strings.attackSettingsDesignerFile);
            }
        }
        public string build_args(string slnFile)
        {
            string solutionPath = "\"" + slnFile + "\"";
            return solutionPath + $" /p:Configuration=Release /p:Platform={ConfigurationManager.AppSettings["arch"]} /p:DebugType=None /p:OutputPath=" + Strings.attackBuildDir;
        }

        public void DownloadZip()
        {
            WebClient wc = new WebClient();
            wc.Headers.Add("user-agent", Strings.githubUserAgent);
            wc.DownloadFile(this.zipball_url, Strings.attackZipPath);
        }

        public void ClearModules()
        {
            try
            {
                Directory.Delete(this.modules_dir, true);
            }
            catch (Exception e)
            {
                Console.WriteLine("Could not clear out modules dir at {0}.\n Error message {1}", this.modules_dir, e.Message);
            }
            if (!(Directory.Exists(this.modules_dir)))
            {
                Directory.CreateDirectory(this.modules_dir);
            }
        }

        public void ClearCsproj()
        {
            try
            {
                File.Delete(this.csproj_file);
            }
            catch (Exception e)
            {
                Console.WriteLine("Could not clear out CSProj file at {0}.\n Error message {1}", this.csproj_file, e.Message);
            }
        }

        public void ClearConfigFile()
        {
            try
            {
                File.Delete(this.config_file);
            }
            catch (Exception e)
            {
                Console.WriteLine("Could not clear out Config file at {0}.\n Error message {1}", this.csproj_file, e.Message);
            }
        }
    }
}
