#!/usr/bin/env python3
""" Command Interpreter """

import cmd
import shlex
import models.base_model import BaseModel
from models import storage


""" importing modules we need """


class HBNBCommand(cmd.Cmd):
    """ Command Interpreter class """

    prompt = "(hbnb) "

    def emptyline(self):
        """Do nothing on empty input line"""
        pass

    def do_create(self, arg):
        """Create a new instance of BaseModel"""
        args = shlex.split(arg)
        if len(args) < 1:
            print("** class name missing **")
            return

        try:
            instance = eval(args[0])()
            instance.save()
            print(instance.id)
        except NameError:
            print("** class doesn't exist **")

    def do_show(self, arg):
        """Print the string representation of an instance"""
        args = shlex.split(arg)
        if len(args) < 1:
            print("** class name missing **")
            return

        try:
            instances = storage.all()
            key = args[0] + "." + args[1]
            if key in instances:
                print(instances[key])
            else:
                print("** no instance found **")
        except IndexError:
            print("** instance id missing **")
        except NameError:
            print("** class doesn't exist **")

    def do_destroy(self, arg):
        """Delete an instance"""
        args = shlex.split(arg)
        if len(args) < 1:
            print("** class name missing **")
            return

        try:
            instances = storage.all()
            key = args[0] + "." + args[1]
            if key in instances:
                del instances[key]
                storage.save()
            else:
                print("** no instance found **")
        except IndexError:
            print("** instance id missing **")
        except NameError:
            print("** class doesn't exist **")

    def do_all(self, arg):
        """Print all instances"""
        args = shlex.split(arg)
        instances = storage.all()
        if len(args) < 1:
            print([str(instances[key]) for key in instances])
        else:
            try:
                class_name = eval(args[0]).__name__
                print([str(instances[key]) for key in instances
                       if class_name in key])
            except NameError:
                print("** class doesn't exist **")

    def do_update(self, arg):
        """Update an instance"""
        args = shlex.split(arg)
        if len(args) < 1:
            print("** class name missing **")
            return

        try:
            instances = storage.all()
            key = args[0] + "." + args[1]
            if key not in instances:
                print("** no instance found **")
                return

            if len(args) < 3:
                print("** attribute name missing **")
                return

            if len(args) < 4:
                print("** value missing **")
                return

            attr_name = args[2]
            attr_val = args[3]
            if hasattr(instances[key], attr_name):
                attr_type = type(getattr(instances[key], attr_name))
                setattr(instances[key], attr_name, attr_type(attr_val))
                instances[key].save()
            else:
                print("** attribute doesn't exist **")
        except IndexError:
            print("** instance id missing **")
        except NameError:
            print("** class doesn't exist **")


if __name__ == '__main__':
    HBNBCommand().cmdloop()
