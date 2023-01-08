from collections import UserDict
from datetime import datetime
from pathlib import Path
import pickle
import re


path = Path('contacts.bin')


class Field:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return self.value


class Birthday(Field):
    def __str__(self):
        return datetime.strftime(self.value, '%d %B')

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        birthdate = ''
        for i in filter(lambda x: x.isnumeric(), value):
            birthdate += i
            if len(birthdate) == 4:
                break
        self.__value = datetime.strptime(birthdate, '%d%m')


class Name(Field):
    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        self.__value = value.title()


class Phone(Field):
    def __eq__(self, __o) -> bool:
        if self.value == __o.value:
            return True
        return False

    def __str__(self):
        return ''.join(self.value)

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        phone = ''
        for i in filter(lambda x: x.isnumeric(), value):
            phone += i
            if len(phone) == 12:
                break
        self.__value = phone


class Record:
    def __init__(self, name: Name, phone: Phone = None, birthday=None):
        self.name = name
        self.birthday = birthday

        self.phones = []
        if phone:
            self.phones.append(phone)

    def __repr__(self):
        return f'{self.name}, {" ".join(map(str, self.phones))}, {self.birthday}'

    def add_phone(self, phone: Phone):
        if isinstance(phone, Phone):
            self.phones.append(phone)
        return f'Sorry, phone must be a Phone instance'

    def delete_phone(self, phone: Phone):
        self.phones.remove(phone)

    def edit_phone(self, old_phone: Phone, new_phone: Phone):
        self.phones[self.phones.index(old_phone)] = new_phone

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def days_to_birthday(self):
        current_date = datetime.now().date()
        current_year = current_date.year
        if self.birthday:
            birth_date = self.birthday.value.date().replace(year=current_year)
            if birth_date >= current_date:
                delta = birth_date - current_date
            else:
                delta = birth_date.replace(
                    year=current_year + 1) - current_date
            return f"{delta.days} days left until {self.name}'s birthday"
        else:
            return f'The birthday of the contact {self.name} is not set'


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def iterator(self, N=1):
        for contact in self.data.values():
            yield f'{contact.name}: {" ".join(map(str, contact.phones))} {str(contact.birthday)} {self.data[contact.name.value].days_to_birthday()}'

    def load(self, path):
        if path.exists():
            with open(path, 'rb') as fh:
                self.data = pickle.load(fh)

    def save(self, path):
        with open(path, 'wb') as fh:
            pickle.dump(self.data, fh)


contacts = AddressBook()
contacts.load(path)


def input_error(func):
    def wrapper(*args):
        try:
            result = func(*args)
            return result
        except KeyError:
            return 'Wrong command! Please, try again!'
        except ValueError:
            return 'Wrong command! Please, try again!'
        except IndexError:
            return 'Wrong command! Please, try again!'
    return wrapper


@input_error
def add_contact(message):
    name, phone, *birthday = message.lower().split()
    name = Name(name)
    phone = Phone(phone)
    if name.value in contacts:
        if phone in contacts[name.value].phones:
            return f'{phone.value} already exists in contact {name.value}'
        else:
            contacts[name.value].add_phone(phone)
            return f'{phone.value} successfully added to contact {name.value}'
    else:
        contact = Record(name)
        contacts.add_record(contact)
        contacts[name.value].add_phone(phone)
        if birthday:
            contacts[name.value].add_birthday(*birthday)
        return f'Contact {name.value} has been added'


@input_error
def change_number(message):
    name, old_phone, new_phone = message.lower().split()
    name = Name(name)
    old_phone = Phone(old_phone)
    new_phone = Phone(new_phone)
    if name.value in contacts:
        contacts[name.value].edit_phone(old_phone, new_phone)
        return f'{old_phone.value} has been changed on {new_phone.value} for contact {name.value}'
    else:
        return f'Contact {name.value} does not exist'


@input_error
def delete_number(message):
    name, phone = message.lower().split()
    name = Name(name)
    phone = Phone(phone)
    if name.value in contacts:
        contacts[name.value].delete_phone(phone)
        return f'{phone.value} has been deleted from contact {name.value}'
    else:
        return f'Contact {name.value} does not exist'


def goodbye():
    contacts.save(path)
    return 'Good bye!'


@input_error
def greeting(message):
    return 'How can I help you?'


@input_error
def show_all(message):
    item = ''
    for contact in contacts.values():
        item += f'{contact.name}: {" ".join(map(str, contact.phones))} {str(contact.birthday)} {contacts[contact.name.value].days_to_birthday()}\n'
    return item.rstrip('\n')


@input_error
def show_phone(message):
    name = message.lower()
    name = Name(name)
    if name.value in contacts:
        contact = contacts[name.value]
        return f'{contact.name}: {" ".join(map(str, contact.phones))}'
    else:
        return f'Contact {name.value} does not exist'


@input_error
def search_contacts(message):
    result = []
    if message:
        for contact in contacts:
            if re.search(message.lower(), str(contacts[contact]).lower()):
                result.append(contacts[contact])
                continue
    else:
        raise ValueError
    if result:
        item = ''
        for contact in result:
            item += f'{contact.name}: {" ".join(map(str, contact.phones))} {str(contact.birthday)} {contacts[contact.name.value].days_to_birthday()}\n'
        return item.rstrip('\n')
    else:
        return 'No matches found'


commands = {
    'add': add_contact,
    'change': change_number,
    'delete': delete_number,
    'hello': greeting,
    'phone': show_phone,
    'show all': show_all
}


@input_error
def parser(command):
    for key in commands:
        if command.lower().strip().startswith(key):
            return commands[key](command[len(key):].strip())


@input_error
def main():
    while True:
        command = input('>>>: ')

        if command.lower() in ('.', 'close', 'exit', 'good bye'):
            print(goodbye())
            break
        elif command.lower().startswith(tuple(key for key in commands.keys())):
            print(parser(command))
        else:
            print(search_contacts(command))


if __name__ == '__main__':
    main()
