using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;


namespace PSAttackBuildTool.Utils
{
    class Display
    {
        static private string dashboard = @"
  __________________________________________________________
 /              __                                          \
 |    _____ ____\ \  _____ _____ _____ _____ _____ _____    |
 |   |  _  |   __\ \|  _  |_   _|_   _|  _  |     |  |  |   |
 |   |   __|__   |> |     | | |   | | |     |   --|    -|   |
 |   |__|  |_____/ /|__|__| |_|   |_| |__|__|_____|__|__|   |
 |              /_/                   BUILD TOOL v{0}       |
 \__________________________________________________________/

 Stage: {1}
 Status: {2}

 {3}

 {4}
";

        static private int stageTop = 10;
        static private int stageLeft = 8;
        static private int statusTop = 11;
        static private int statusLeft = 9;
        static private int messageTop = 13;
        static private int messageLeft = 1;
        static private int secondaryMessageTop = 17;
        static private int secondaryMessageLeft = 1;

        static public void Dashboard()
        {
            Console.Clear();
            Console.Write(dashboard, Strings.version, "","","","");
        }

        static public void Stage(string value)
        {
            Console.CursorTop = stageTop;
            Console.CursorLeft = stageLeft;
            string clear = String.Concat(Enumerable.Repeat(" ",(Console.WindowWidth - stageLeft)));
            Console.Write(clear);
            Console.CursorTop = stageTop;
            Console.CursorLeft = stageLeft;
            Console.Write(value);
        }

        static public void Status(string value)
        {
            Console.CursorTop = statusTop;
            Console.CursorLeft = statusLeft;
            string clear = String.Concat(Enumerable.Repeat(" ", (Console.WindowWidth - statusLeft)));
            string clearWholeLine = String.Concat(Enumerable.Repeat(" ", Console.WindowWidth));
            Console.Write(clear);
            while (Console.CursorTop < messageTop)
            {
                Console.Write(clearWholeLine);
                Console.CursorTop += 1;
            }
            Console.CursorTop = statusTop;
            Console.CursorLeft = statusLeft;
            Console.Write(value);
        }

        static public void PrimaryMessage(string value)
        {
            Console.CursorTop = messageTop;
            Console.CursorLeft = messageLeft;
            string clear = String.Concat(Enumerable.Repeat(" ", (Console.WindowWidth - messageLeft)));
            string clearWholeLine = String.Concat(Enumerable.Repeat(" ", Console.WindowWidth));
            Console.Write(clear);
            int cursorTop = Console.CursorTop;
            int windowHeight = Console.WindowHeight;
            while (Console.CursorTop < (Console.WindowHeight - 1))
            {
                cursorTop = Console.CursorTop;
                windowHeight = Console.WindowHeight;
                Console.Write(clearWholeLine);
            }
            Console.CursorTop = messageTop;
            Console.CursorLeft = messageLeft;
            Console.Write(value);
        }

        static public void SecondaryMessage(string value)
        {
            Console.CursorTop = secondaryMessageTop;
            Console.CursorLeft = secondaryMessageLeft;
            string clear = String.Concat(Enumerable.Repeat(" ", (Console.WindowWidth - secondaryMessageLeft)));
            string clearWholeLine = String.Concat(Enumerable.Repeat(" ", Console.WindowWidth));
            Console.Write(clear);
            while (Console.CursorTop < (Console.WindowHeight - 1))
            {
                Console.Write(clearWholeLine);
            }
            Console.CursorTop = secondaryMessageTop;
            Console.CursorLeft = secondaryMessageLeft;
            Console.Write(value);
        }

        static public void ErrorMessage(string message, string exceptionMessage=null, string secondaryMessage=null)
        {
            ConsoleColor origColor = Console.ForegroundColor;
            Console.ForegroundColor = ConsoleColor.Red;
            Status("ERROR!!");
            PrimaryMessage(message);
            if (secondaryMessage == null)
            {
                secondaryMessage = "PS>Attack will probably not build properly because of this. Press enter to give it a try anyways though.";
            }
            if (exceptionMessage != null)
            {
                secondaryMessage = $"Error message: \n\n {exceptionMessage} \n\n Press enter to continue building PS>Attack..";
            }
            SecondaryMessage(secondaryMessage);
            Console.ReadLine();
            Console.ForegroundColor = origColor;
        }
    }
}
