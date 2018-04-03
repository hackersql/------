Welcome to the fimap project!
=============================

fimap is a little python tool which can find, prepare, audit, exploit and even google automaticly for local and remote file inclusion bugs in webapps. fimap should be something like [sqlmap](http://sqlmap.sourceforge.net) just for LFI/RFI bugs instead of sql injection. It's currently under heavy development but it's usable.


The goal of fimap is to improve the quality and security of **your** website.

**Do not use this tool on servers where you don't have permission to pentest!**

I am dead serious.

* * *

**To clone this project, use the HTTPS link! SSH cloning doesn't work for guests.**

* * * 

Find fimap on twitter: [http://twitter.com/fimap](http://twitter.com/fimap)

## Quick News for SVN and upcoming versions

*   fimap has moved! The official fimap site is now available at https://tha-imax.de/git/root/fimap
*   Thank you to https://github.com/Oweoqi for doing the hard work and converting the project from googlecode to github!

## fimap Features

*   Check a Single URL, List of URLs, or Google results fully automaticly.
*   Can identify and exploit file inclusion bugs.
  *   Relative\Absolute Path Handling.
  *   Tries automaticly to eleminate suffixes with Nullbyte and other methods like Dot-Truncation.
  *   Remotefile Injection.
  *   Logfile Injection.
*   Test and exploit multiple bugs:
  *   include()
  *   include_once()
  *   require()
  *   require_once()
*   You always define absolute pathnames in the configs. No monkey like redundant pathes like:
  *   ../etc/passwd
  *   ../../etc/passwd
  *   ../../../etc/passwd
*   Has a Blind Mode (--enable-blind) for cases when the server has disabled error messages.
*   Has an interactive exploit mode which...
  *   ...can spawn a shell on vulnerable systems.
  *   ...can spawn a reverse shell on vulnerable systems.
  *   ...can do anything you can imagine through it's plugin interface.
*   Add your own payloads and pathes to the xml files or go ahead and write a new plugin.
*   Has a Harvest mode which can collect URLs from a given domain for later pentesting.
*   Works also on windows.
*   Can handle directories in RFI mode like:
  *   <tt><? include ($_GET["inc"] . "/content/index.html"); ?></tt>
  *   <tt><? include ($_GET["inc"] . "_lang/index.html"); ?></tt>
  *   where Null-Byte and the '?' trick is not possible.
*   Can use proxys.
*   Scans and exploits GET, POST and Cookies.
*   Has a very small footprint. (No senseless bruteforcing of pathes - unless you need it.)
*   Can attack also windows servers! 
*   Has a tiny plugin interface for writing exploitmode plugins 
*   Non Interactive Exploiting

## What doesn't work yet?
*   Other languages than PHP (even if engine is ready for others as well.)

## Is there a How To?

*   Check out [this](http://kaoticcreations.blogspot.com/2011/08/automated-lfirfi-scanning-exploiting.html) post by HR from [Kaotic Creations](http://kaoticcreations.blogspot.com) which explains fimap really good :) It's a tutorial for windows but I think unix heads should understand it as well.

## Credits

*   Main Developer: [Iman Karim](mailto:fimap.dev@gmail.com)

*   Trusted Plugins:

*   Metasploit binding by [Xavier Garcia](mailto:xavi.garcia(atom)gmail(dot)com)
*   Weevily Injector by [Darren "Infodox" Martyn](mailto:infodox(atom)insecurety(dot)net) from [http://insecurety.net/](http://insecurety.net/)
*   AES Reverse Shell by [Darren "Infodox" Martyn](mailto:infodox(atom)insecurety(dot)net) from [http://insecurety.net/](http://insecurety.net/)

*   Additional thanks goes out to:

*   Peteris Krumins for [xgoogle](http://www.catonmat.net/blog/python-library-for-google-search/) python module.
*   Pentestmonkey for [php-reverse-shell](http://pentestmonkey.net/tools/php-reverse-shell/).
*   Crummy for [BeautifulSoup](http://www.crummy.com/software/BeautifulSoup/).
*   Zeth0 from [commandline.org.uk](http://commandline.org.uk/) for ssh.py.

*   Also thanks to:

*   The [Python](http://python.org) Project
*   The [Eclipse](http://eclipse.org) Project
*   The [Netbeans](http://netbeans.org) Project
