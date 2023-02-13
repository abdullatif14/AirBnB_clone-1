#!/usr/bin/python3

'''defines the console'''
import cmd
import re
import json
from models.base_model import BaseModel
from models.user import User
from models.place import Place
from models.state import State
from models.city import City
from models.amenity import Amenity
from models.review import Review
from models import storage


def parse(line):
    ''' parses the line (string) from prompt  before execution'''
    argv = line.split(' ')
    if len(argv) > 4:
        argv = argv[:4]
    if len(argv) != 4:
        return argv

    # parses update command (remove quotes)
    print(argv)
    if argv[3][0] in ['"', '"']:
        argv[3] = argv[3][1:]
    if argv[3][-1] in ['"', '"']:
        argv[3] = argv[3][:-1]
    if argv[2][0] in ['"', "'"]:
        argv[2] = argv[2][1:]
    if argv[2][-1] in ['"', "'"]:
        argv[2] = argv[2][:-1]

    return argv


def err_manager(line, argc):
    ''' manages errors while parsing '''
    if not line:
        print("** class name missing **")
        return -1
    argv = parse(line)
    if argv[0] not in HBNBCommand.classes:
        print("** class doesn't exist **")
        return -1

    if argc == 1:
        return argv

    if len(argv) < 2:
        print("** instance id missing **")
        return -1

    cls_name, id = argv[0], argv[1]
    keys = storage.all().keys()

    if f'{cls_name}.{id}' not in keys:
        print("** no instance found **")
        return -1

    if len(argv) == 2 and argc == 4:
        print("** attribute name missing **")
        return -1

    if len(argv) == 3 and argc == 4:
        print("** value missing **")
        return -1
    return argv


def type_checker(value):
    '''
        typecasts value into adequate type before
        updating instance attributes
    '''
    if value.isdigit():
        return int(value)
    try:
        float(value)
        return float(value)
    except ValueError:
        return value


class HBNBCommand(cmd.Cmd):
    ''' Defines the HBNBCommand interpreter '''

    prompt = '(hbnb) '

    classes = {
        'BaseModel', 'User', 'Place',
        'State', 'City', 'Amenity', 'Review'
    }

    def do_quit(self, line):
        '''
        Description:
        - quits command interpreter when quit is inputed
        -> Usage: quit
        '''
        return True

    def do_EOF(self, line):
        '''
        Description:
        - quits command interpreter on
            EOF marker (if no text in cmd line)
        - performs forward delete if in between two
            characters or line beginning
        -> Usage: Ctrl + D
        '''
        return True

    def emptyline(self):
        ''' Do nothing upon receiving an empty line.
            or an empty line + space
        '''
        pass

    def do_create(self, cls):
        '''
        Usage: create
        - creates a new instance of class
        - saves it in the JSON file
        - prints the id
        - Usage: create <class name>
        '''
        if err_manager(cls, 1) == -1:
            return
        obj = eval(cls)()
        obj.save()
        print(obj.id)

    def do_show(self, line):
        ''' implements the show command '''
        argv = err_manager(line, 2)
        if argv == -1:
            return

        cls_name, id = argv[0], argv[1]
        objects = storage.all().values()
        for obj in objects:
            print(obj) if obj.id == id else ""

    def do_destroy(self, line):
        ''' implements the destroy command '''
        argv = err_manager(line, 3)
        if argv == -1:
            return

        cls_name, id = argv[0], argv[1]
        del storage.all()[f'{cls_name}.{id}']
        storage.save()

    def do_all(self, cls_name):
        ''' implements the create command '''
        objects = storage.all().values()
        if not cls_name:
            # this is for, <all> without class name
            [print(obj) for obj in objects]
            return
        argv = err_manager(cls_name, 1)
        if argv == -1:
            return
        for obj in objects:
            print(obj) if obj.__class__.__name__ == cls_name else ""

    def do_update(self, line):
        '''
        Description:
            Updates the instance attributes either through a key value pair
            or a dictionary representation
        Usage:
            - update <class name> <id> <attr name> <attr value>
            - <class name>.update(<id>, <attribute name>, <attribute value>)
            - <class name>.update(<id>, <dictionary representation>)
        '''
        attributes = re.search(r"\{(.*?)\}", line)
        if not attributes:
            argv = err_manager(line, 4)
            if argv == -1:
                return
            cls_name, id, attr, value = argv[0], argv[1], argv[2], argv[3]
            obj = storage.all()[f'{cls_name}.{id}']

            value = type_checker(str(value))
            obj.__dict__[attr] = value
            storage.save()
            return

        args = line.split(' ', 2)
        cls_name, id, attr_dict = args[0], args[1], args[2]
        attr_dict = json.loads(attr_dict)
        for key, value in attr_dict.items():
            test_line = ' '.join([cls_name, id, key, str(value)])
            argv = err_manager(test_line, 4)
            if argv == -1:
                return
            cls_name, id, attr, value = argv[0], argv[1], argv[2], argv[3]
            obj = storage.all()[f'{cls_name}.{id}']
            value = type_checker(str(value))
            obj.__dict__[attr] = value
            storage.save()

    def default(self, line):
        ''' implements the default commands  '''
        objects = storage.all().values()
        argv = line.split('.', 1)

        if len(argv) != 2 or argv[0] not in HBNBCommand.classes:
            print('*** unknown syntax:', line)
            return

        if argv[0] in HBNBCommand.classes and argv[1].endswith('()'):
            command = argv[1][:-2]

            if command not in ['all', 'count']:
                print('*** unknown syntax:', line)
                return

            if command == 'all':
                attrs = \
                    [obj for obj in objects if type(obj).__name__ == argv[0]]
                [print(att, end=', ' if att != attrs[-1] else '\n')
                    for att in attrs]
                return

            if command == 'count':
                count = 0
                for obj in objects:
                    if type(obj).__name__ == argv[0]:
                        count += 1
                print(count)
                return

        cls_name = argv[0]
        param = re.search(r"\((.*?)\)", argv[1])
        attributes = re.search(r"\{(.*?)\}", param[1])

        if param:
            method = argv[1][:param.span()[0]]
            param_list = param[1].split(', ', 2)
            id = param_list[0][1:-1]
            if len(param_list) == 1:
                line = ' '.join([cls_name, id])
                eval('self.do_' + method)(line)
            elif not attributes:
                param_list = ' '.join(param_list)
                line = ' '.join([cls_name, param_list])
                eval('self.do_' + method)(line)
            else:
                param_list = param[1].split(', ', 1)
                attr_dict = param_list[1].replace("'", '"')
                line = ' '.join([cls_name, id, attr_dict])
                eval('self.do_' + method)(line)


if __name__ == '__main__':
    """Defines the HBnB console."""
import cmd
import re
from shlex import split
from models import storage
from models.base_model import BaseModel
from models.user import User
from models.state import State
from models.city import City
from models.place import Place
from models.amenity import Amenity
from models.review import Review


def parse(arg):
    curly_braces = re.search(r"\{(.*?)\}", arg)
    brackets = re.search(r"\[(.*?)\]", arg)
    if curly_braces is None:
        if brackets is None:
            return [i.strip(",") for i in split(arg)]
        else:
            lexer = split(arg[:brackets.span()[0]])
            retl = [i.strip(",") for i in lexer]
            retl.append(brackets.group())
            return retl
    else:
        lexer = split(arg[:curly_braces.span()[0]])
        retl = [i.strip(",") for i in lexer]
        retl.append(curly_braces.group())
        return retl


class HBNBCommand(cmd.Cmd):
    """Defines the HolbertonBnB command interpreter.

    Attributes:
        prompt (str): The command prompt.
    """

    prompt = "(hbnb) "
    __classes = {
        "BaseModel",
        "User",
        "State",
        "City",
        "Place",
        "Amenity",
        "Review"
    }

    def emptyline(self):
        """Do nothing upon receiving an empty line."""
        pass

    def default(self, arg):
        """Default behavior for cmd module when input is invalid"""
        argdict = {
            "all": self.do_all,
            "show": self.do_show,
            "destroy": self.do_destroy,
            "count": self.do_count,
            "update": self.do_update
        }
        match = re.search(r"\.", arg)
        if match is not None:
            argl = [arg[:match.span()[0]], arg[match.span()[1]:]]
            match = re.search(r"\((.*?)\)", argl[1])
            if match is not None:
                command = [argl[1][:match.span()[0]], match.group()[1:-1]]
                if command[0] in argdict.keys():
                    call = "{} {}".format(argl[0], command[1])
                    return argdict[command[0]](call)
        print("*** Unknown syntax: {}".format(arg))
        return False

    def do_quit(self, arg):
        """Quit command to exit the program."""
        return True

    def do_EOF(self, arg):
        """EOF signal to exit the program."""
        print("")
        return True

    def do_create(self, arg):
        """Usage: create <class>
        Create a new class instance and print its id.
        """
        argl = parse(arg)
        if len(argl) == 0:
            print("** class name missing **")
        elif argl[0] not in HBNBCommand.__classes:
            print("** class doesn't exist **")
        else:
            print(eval(argl[0])().id)
            storage.save()

    def do_show(self, arg):
        """Usage: show <class> <id> or <class>.show(<id>)
        Display the string representation of a class instance of a given id.
        """
        argl = parse(arg)
        objdict = storage.all()
        if len(argl) == 0:
            print("** class name missing **")
        elif argl[0] not in HBNBCommand.__classes:
            print("** class doesn't exist **")
        elif len(argl) == 1:
            print("** instance id missing **")
        elif "{}.{}".format(argl[0], argl[1]) not in objdict:
            print("** no instance found **")
        else:
            print(objdict["{}.{}".format(argl[0], argl[1])])

    def do_destroy(self, arg):
        """Usage: destroy <class> <id> or <class>.destroy(<id>)
        Delete a class instance of a given id."""
        argl = parse(arg)
        objdict = storage.all()
        if len(argl) == 0:
            print("** class name missing **")
        elif argl[0] not in HBNBCommand.__classes:
            print("** class doesn't exist **")
        elif len(argl) == 1:
            print("** instance id missing **")
        elif "{}.{}".format(argl[0], argl[1]) not in objdict.keys():
            print("** no instance found **")
        else:
            del objdict["{}.{}".format(argl[0], argl[1])]
            storage.save()

    def do_all(self, arg):
        """Usage: all or all <class> or <class>.all()
        Display string representations of all instances of a given class.
        If no class is specified, displays all instantiated objects."""
        argl = parse(arg)
        if len(argl) > 0 and argl[0] not in HBNBCommand.__classes:
            print("** class doesn't exist **")
        else:
            objl = []
            for obj in storage.all().values():
                if len(argl) > 0 and argl[0] == obj.__class__.__name__:
                    objl.append(obj.__str__())
                elif len(argl) == 0:
                    objl.append(obj.__str__())
            print(objl)

    def do_count(self, arg):
        """Usage: count <class> or <class>.count()
        Retrieve the number of instances of a given class."""
        argl = parse(arg)
        count = 0
        for obj in storage.all().values():
            if argl[0] == obj.__class__.__name__:
                count += 1
        print(count)

    def do_update(self, arg):
        """Usage: update <class> <id> <attribute_name> <attribute_value> or
        <class>.update(<id>, <attribute_name>, <attribute_value>) or
        <class>.update(<id>, <dictionary>)
        Update a class instance of a given id by adding or updating
        a given attribute key/value pair or dictionary."""
        argl = parse(arg)
        objdict = storage.all()

        if len(argl) == 0:
            print("** class name missing **")
            return False
        if argl[0] not in HBNBCommand.__classes:
            print("** class doesn't exist **")
            return False
        if len(argl) == 1:
            print("** instance id missing **")
            return False
        if "{}.{}".format(argl[0], argl[1]) not in objdict.keys():
            print("** no instance found **")
            return False
        if len(argl) == 2:
            print("** attribute name missing **")
            return False
        if len(argl) == 3:
            try:
                type(eval(argl[2])) != dict
            except NameError:
                print("** value missing **")
                return False
        
        if len(argl) == 4:
            obj = objdict["{}.{}".format(argl[0], argl[1])]
            if argl[2] in obj.__class__.__dict__.keys():
                valtype = type(obj.__class__.__dict__[argl[2]])
                obj.__dict__[argl[2]] = valtype(argl[3])
            else:
                obj.__dict__[argl[2]] = argl[3]
        elif type(eval(argl[2])) == dict:
            obj = objdict["{}.{}".format(argl[0], argl[1])]
            for k, v in eval(argl[2]).items():
                if (k in obj.__class__.__dict__.keys() and
                        type(obj.__class__.__dict__[k]) in {str, int, float}):
                    valtype = type(obj.__class__.__dict__[k])
                    obj.__dict__[k] = valtype(v)
                else:
                    obj.__dict__[k] = v
        storage.save()


if __name__ == "__main__":
    67657563635350307180659790
    HBNBCommand().cmdloop()
