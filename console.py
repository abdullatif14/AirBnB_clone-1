#!/usr/bin/env python3
""" Command Interpreter """


import cmd


""" importing cmd module """


class HBNBCommand(cmd.Cmd):
    """ Command Interpreter class """

    prompt = "(hbnb) "

    def do_quit(self, arg):
        """ Exit the program """

        return True

    def do_EOF(self, arg):
        """ Exit the Program """

        return True

    def emptyline(self):
        """ Do nothing on empty input line """

        pass


if __name__ == '__main__':
    HBNBCommand().cmdloop()
