using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Collections.ObjectModel;
using System.Management.Automation;
using System.Management.Automation.Runspaces;
using PSAttack.PSAttackShell;
using PSAttack.Utils;

namespace PSAttack.PSAttackProcessing
{
    class Processing
    {
        // This is called everytime a key is pressed.
        public static AttackState CommandProcessor(AttackState attackState)
        {
            // If we're running in meterpreter or something, just try and execute whatever we have.
            if (!(attackState.console))
            {
                if (attackState.cmd == "exit")
                {
                    System.Environment.Exit(0);
                }
                else
                {
                    attackState = PSExec(attackState);
                    attackState.displayCmd = "";
                    Display.Output(attackState);
                }

            }
            else
            {

                attackState.output = null;
                int relativePos = attackState.relativeCursorPos();
                int cmdLength = attackState.displayCmd.Length;
                /////////////////////////
                // BACKSPACE OR DELETE //
                /////////////////////////
                if (attackState.keyInfo.Key == ConsoleKey.Backspace || attackState.keyInfo.Key == ConsoleKey.Delete)
                {
                    attackState.ClearLoop();
                    if (attackState.displayCmd != "" && attackState.relativeCursorPos() > 0)
                    {
                        if (attackState.keyInfo.Key == ConsoleKey.Backspace)
                        {
                            attackState.cursorPos -= 1;
                        }
                        List<char> displayCmd = attackState.displayCmd.ToList();
                        int relativeCursorPos = attackState.relativeCmdCursorPos();
                        displayCmd.RemoveAt(relativeCursorPos);
                        attackState.displayCmd = new string(displayCmd.ToArray());
                    }
                }
                /////////////////////////
                // BACKSPACE OR DELETE //
                /////////////////////////
                else if (attackState.keyInfo.Key == ConsoleKey.Home || attackState.keyInfo.Key == ConsoleKey.End)
                {
                    if (attackState.keyInfo.Key == ConsoleKey.Home)
                    {
                        attackState.cursorPos = attackState.promptLength;
                    }
                    else
                    {
                        attackState.cursorPos = attackState.promptLength + attackState.displayCmd.Length;
                    }
                }
                ////////////////
                // UP OR DOWN //
                ////////////////
                else if (attackState.keyInfo.Key == ConsoleKey.UpArrow || attackState.keyInfo.Key == ConsoleKey.DownArrow)
                {
                    return history(attackState);
                }
                ///////////////////
                // LEFT OR RIGHT //
                ///////////////////

                // TODO: Fix arrows navigating between wrapped command lines
                else if (attackState.keyInfo.Key == ConsoleKey.LeftArrow)
                {
                    if (attackState.relativeCmdCursorPos() > 0)
                    {

                        attackState.ClearLoop();
                        attackState.cursorPos -= 1;
                    }
                    return attackState;
                }
                else if (attackState.keyInfo.Key == ConsoleKey.RightArrow)
                {
                    if (attackState.relativeCmdCursorPos() < attackState.displayCmd.Length)
                    {

                        attackState.ClearLoop();
                        attackState.cursorPos += 1;
                    }
                    return attackState;
                }
                ///////////
                // ENTER //
                ///////////
                else if (attackState.keyInfo.Key == ConsoleKey.Enter)
                {
                    Console.WriteLine();
                    attackState.ClearLoop();
                    attackState.cmd = attackState.displayCmd;
                    // don't add blank lines to history
                    if (attackState.cmd != "")
                    {
                        attackState.history.Add(attackState.cmd);
                    }
                    if (attackState.cmd == "exit")
                    {
                        Console.WriteLine("[i] Running Exit..");
                        System.Environment.Exit(0);
                    }
                    else if (attackState.cmd == "clear")
                    {
                        Console.Clear();
                        attackState.displayCmd = "";
                        Display.printPrompt(attackState);

                    }
                    // TODO: Make this better.
                    //else if (attackState.cmd.Contains(".exe"))
                    //{
                    //    attackState.cmd = "Start-Process -NoNewWindow -Wait " + attackState.cmd;
                    //    attackState = Processing.PSExec(attackState);
                    //    Display.Output(attackState);
                    //}
                    // assume that we just want to execute whatever makes it here.
                    else
                    {
                        //Console.WriteLine("[*] Running PSEXEC");
                        attackState = Processing.PSExec(attackState);
                        attackState.displayCmd = "";
                        Display.Output(attackState);
                    }
                    // clear out cmd related stuff from state
                    attackState.ClearIO(display: true);
                }
                /////////
                // TAB //
                /////////
                else if (attackState.keyInfo.Key == ConsoleKey.Tab)
                {
                    return TabExpansion.Process(attackState);
                }
                //////////
                // if nothing matched, lets assume its a character and add it to displayCmd
                //////////
                else
                {
                    attackState.ClearLoop();
                    // figure out where to insert the typed character
                    List<char> displayCmd = attackState.displayCmd.ToList();
                    int relativeCmdCursorPos = attackState.relativeCmdCursorPos();
                    int cmdInsertPos = attackState.cursorPos - attackState.promptLength;
                    displayCmd.Insert(attackState.cursorPos - attackState.promptLength, attackState.keyInfo.KeyChar);
                    attackState.displayCmd = new string(displayCmd.ToArray());
                    attackState.cursorPos += 1;
                }
            }
            return attackState;
        }

        // called when up or down is entered
        static AttackState history(AttackState attackState)
        {
            if (attackState.history.Count > 0)
            {
                if (attackState.loopType == null)
                {
                    attackState.loopType = "history";
                    if (attackState.loopPos == 0)
                    {
                        attackState.loopPos = attackState.history.Count;

                    }
                }
                if (attackState.keyInfo.Key == ConsoleKey.UpArrow && attackState.loopPos > 0)
                {
                    attackState.loopPos -= 1;
                    attackState.displayCmd = attackState.history[attackState.loopPos];

                }
                if (attackState.keyInfo.Key == ConsoleKey.DownArrow)
                {

                    if ((attackState.loopPos + 1) > (attackState.history.Count - 1))
                    {
                        attackState.displayCmd = "";
                    }
                    else
                    {
                        attackState.loopPos += 1;
                        attackState.displayCmd = attackState.history[attackState.loopPos];
                    }
                }
                attackState.cursorPos = attackState.endOfDisplayCmdPos();
            }
            return attackState;
        }

        // Here is where we execute posh code
        public static AttackState PSExec(AttackState attackState)
        {
            using (Pipeline pipeline = attackState.runspace.CreatePipeline())
            {
                //Console.WriteLine("[*] puting cmd in pipeline");
                pipeline.Commands.AddScript(attackState.cmd);
                // If we're in an auto-complete loop, we want the PSObjects, not the string from the output of the command
                // TODO: clean this up
                if ((attackState.loopType != null) || (!attackState.console))
                {
                    //Console.WriteLine("[*] Merging results 1");
                    pipeline.Commands[0].MergeMyResults(PipelineResultTypes.Error, PipelineResultTypes.Output);
                }
                else
                {
                    //Console.WriteLine("[*] Merging results 2");
                    pipeline.Commands[0].MergeMyResults(PipelineResultTypes.Error, PipelineResultTypes.Output); pipeline.Commands.Add("out-default"); pipeline.Commands.Add("Write-Host");
                }
                //try
                //{
                //Console.WriteLine("[*] trying to evoke pipeline");
                if (attackState.console)
                {
                    attackState.results = pipeline.Invoke();
                }
                else
                {
                    pipeline.InvokeAsync();
                    while (!pipeline.Output.EndOfPipeline)
                    {
                        pipeline.Output.WaitHandle.WaitOne();
                        while (pipeline.Output.Count > 0)
                        {
                            PSObject psObject = pipeline.Output.Read();
                            // Write output object data.
                            Console.WriteLine(psObject.ToString());
                            Collection<PSObject> results = new Collection<PSObject>();
                            results.Add(psObject);
                            attackState.results = results;
                        }
                    }
                }

                //}
                //catch (Exception e)
                //{
                //    Console.WriteLine("[!] Exeception..");
                //    attackState.results = null;
                //    Display.Exception(attackState, e.Message);
                //}

                pipeline.Dispose();
            }
            //Clear out command so it doesn't get echo'd out to console again.
            attackState.ClearIO();
            if (attackState.loopType == null)
            {
                attackState.cmdComplete = true;
            }
            return attackState;
        }
    }

}