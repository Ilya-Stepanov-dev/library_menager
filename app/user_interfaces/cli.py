import os
from abc import abstractmethod

from library import Book, Library
from utils import BookStatus, MenuDesignations, cprint, validator

from .base import Interface

class Menu(Interface):
    """Base class Menu"""

    @abstractmethod
    def on_enter(self) -> None:
        """The display is called when entering the interface."""

        pass

    @abstractmethod
    def handle_input(self, input) -> None:
        """Handles the user's input."""

        pass
    
    def _clear_console(self) -> None:
        """Clears the console screen. Supports Windows and Unix/Linux/MacOS."""
        
        os.system('cls' if os.name == 'nt' else 'clear')


    def _on_exit(self) -> None:
        """Exits the program when the user chooses to exit the menu."""
        
        self._clear_console()
        cprint.violet('Goodbye!')
        os._exit(0)


    def run(self) -> None:
        """Runs the CLI infinite loop."""

        try:
            self._clear_console()
            while True:
                self.on_enter()
                self = self.handle_input(input())
        except KeyboardInterrupt:
            self._clear_console()
            cprint.violet('Goodbye!')


class ValidatorInputData:
    """Class to validate input data from user."""

    def _input_data(self, name_filed: str) -> str:
        cprint.yellow(f'Enter {name_filed}: ', end='')
        data = input()
        self._clear_console()
        return data.strip()

    def _input_title(self) -> str | None:
        return validator.validate_title(title=self._input_data('Title book'))

    def _input_author(self) -> str | None:
        return validator.validate_author(author=self._input_data('Author'))

    def _input_year(self) -> int | None:
        return validator.validate_year(year=self._input_data('Year'))

    def _input_id(self) -> int | None:
        return validator.validate_id(id=self._input_data('Book ID'))

class MainMenu(Menu):

    def on_enter(self) -> None:
        cprint.blue('Library menu:\n')
        cprint.green('1. Add a book')
        cprint.green('2. Delete book')
        cprint.green('3. Search for a book')
        cprint.green('4. Show all books')
        cprint.green('5. Change book status\n')
        cprint.red(f'{MenuDesignations.EXIT.value}. Exit\n')
        cprint.yellow('Select an action: ', end='')


    def handle_input(self, user_input) -> Menu:
        self._clear_console()
        match user_input:
            case '1':
                return AddMenu()
            case '2':
                return DeleteMenu()
            case '3':
                return SearchMenu()
            case '4':
                try:
                    show_book = ShowBook(books = Library().get_all_books(), last_state=self)
                except Exception as e:
                    cprint.red(e)
                    return MainMenu()
                else:
                    return show_book
            case '5': 
                return ChangeStatusMenu()
            case MenuDesignations.EXIT.value:
                self._on_exit()
            case _:
                cprint.red('Incorrect selection. Please try again.\n')
                return MainMenu()
            

class AddMenu(Menu, ValidatorInputData):

    def __init__(self, 
                 book_title: str | None = None, 
                 author: str | None = None, 
                 year: int | None = None) -> None:
        super().__init__()
        self.book_title = book_title
        self.author =  author
        self.year = year

    def on_enter(self) -> None:
        cprint.blue('Add book menu:\n')
        cprint.green(f'1. Title book - {self.book_title}')
        cprint.green(f'2. Author - {self.author}')
        cprint.green(f'3. Year - {self.year}\n')
        cprint.red(f'{MenuDesignations.SAVE.value}. Save\t\t\t{MenuDesignations.BACK.value}. Back\n')
        cprint.yellow('Select the field you want to change: ', end='')
    

    def handle_input(self, user_input) -> Menu:
        self._clear_console()
        match user_input:
            case '1':
                try:  
                    self.book_title = self._input_title()
                except Exception as e:
                    cprint.red(e)
                    return self
                else:
                    return self
            case '2':
                try:
                    self.author = self._input_author()
                except Exception as e:
                    cprint.red(e)
                    self.author = None
                finally: 
                    return self
            case '3':
                try:
                    self.year = self._input_year()
                except Exception as e:
                    self.year = None
                    cprint.red(e)
                finally: 
                    return self
            case MenuDesignations.SAVE.value:
                try:
                    new_book = Library().add_book(self.book_title, self.author, self.year)
                except Exception as e:
                    cprint.red(e)
                    return self
                else:
                    return SuccessfulCompletion(books=[new_book], 
                                                additional_info='The book has been added successfully',
                                                last_state=AddMenu())

            case MenuDesignations.BACK.value:
                return MainMenu()
            case _:
                cprint.red('Incorrect selection. Please try again.\n')
                return self
            
class SuccessfulCompletion(Menu):

    def __init__(self, 
                 message: str='Success completion', 
                 books: list[Book] | None = None, 
                 last_state: Menu | None = None, 
                 additional_info: str | None = None) -> None:
        super().__init__()
        self.message = message
        self.books = books
        self.last_state = last_state
        self.additional_info = additional_info


    def on_enter(self) -> None:
        cprint.green(f'{self.message}')
        if self.additional_info:
            cprint.green(self.additional_info, end='\n\n')
            if self.books:
                for book in self.books:
                    cprint.violet(book)
            print('\n')
        cprint.yellow('Press any key to exit to the last menu: ', end='')

    def handle_input(self, user_input) -> Menu:
        self._clear_console()
        return self.last_state
    
class DeleteMenu(Menu, ValidatorInputData):

    def __init__(self, 
                 book_title: str | None = None, 
                 book_id: int | None = None,
                 book: Book | None = None) -> None:
        super().__init__()
        self.book_id = book_id
        self.book = book


    def on_enter(self) -> None:
        cprint.blue('Delete book menu:\n')
        cprint.green('Enter ID Book\n')
        if self.book:
            cprint.yellow(' --- ')
            cprint.violet(self.book)
            cprint.yellow(' --- \n')

        cprint.red(f'{MenuDesignations.DELETE.value}. Delete book\t\t\t {MenuDesignations.BACK.value}. Back\n')
        cprint.yellow('Search filed ID: ', end='')
    
    def validate_input_id(self, data: str) -> int:
        return validator.validate_id(data)
    
    def handle_input(self, user_input) -> Menu:
        self._clear_console()
        match user_input:
            case MenuDesignations.BACK.value:
                return MainMenu()

            case MenuDesignations.DELETE.value:
                try:
                    delete_book = Library().remove_book(self.book_id)
                except Exception as e:
                    cprint.red(e)
                    return self
                else:
                    return SuccessfulCompletion(books=[delete_book], 
                                                additional_info='The book has been deleted successfully',
                                                last_state=DeleteMenu())
            case _:
                try:
                    self.book = Library().find_book_id(book_id=self.validate_input_id(user_input))
                    self.book_id = self.book.id
                except Exception as e:
                    cprint.red(e)
                finally:
                    return self
        

class SearchMenu(Menu):

    def on_enter(self) -> None:
        cprint.blue('Search Book menu:\n')
        cprint.green('Search by title, author or year\n')
        cprint.red(f'{MenuDesignations.BACK.value}. Back\n')
        cprint.yellow('Search filed: ', end='')
        

    def handle_input(self, user_input) -> Menu:
        self._clear_console()
        match user_input:
            case MenuDesignations.BACK.value:
                return MainMenu()
            case _:
                try:
                    show_book = ShowBook(books=Library().find_books(user_input), last_state=self)
                except Exception as e:
                    cprint.red(e)
                    return self
                else:
                    return show_book
            
class ShowBook(Menu):

    def __init__(self, 
                 books: list[Book]=[], 
                 last_state: Menu=MainMenu(),
                 messages: str = 'Press any key to exit to the last menu: ') -> None:
        super().__init__()
        self.books = books
        self.last_state = last_state
        self.message = messages

    def on_enter(self) -> None:
        cprint.blue('Show books:')
        for book in self.books:
            cprint.yellow(' --- ')
            cprint.violet(book)
        cprint.yellow(' --- \n')
        cprint.yellow(self.message, end='')

    def handle_input(self, input) -> Menu:
        self._clear_console()
        return self.last_state


class ChangeStatusMenu(Menu, ValidatorInputData):

    def __init__(self, 
                 book_id: int | None = None, 
                 status: str | None = None) -> None:
        super().__init__()
        self.book_id = book_id
        self.status = status

    def on_enter(self) -> None:
        cprint.blue('Change status book\n')
        cprint.green(f'1. Book ID - {self.book_id}')
        cprint.green(f'2. Status - {self.status}\n')
        cprint.red(f'{MenuDesignations.SAVE.value}. Change Status\t\t\t{MenuDesignations.BACK.value}. Back\n')
        cprint.yellow('Select the field you want to change: ', end='')

    
    def change_status(self) -> BookStatus | None:
        cprint.blue('Select status:')
        cprint.green(f'Current status: {self.status}')
        for index_status, status in enumerate(BookStatus):
            cprint.violet(f'{index_status + 1}. {status.value}')
        cprint.red(f'\n{MenuDesignations.BACK.value}. Back\n')
        cprint.yellow('Select a new status: ', end='')
        
        try:
            index_status = validator.validate_id(input())
            status = validator.validate_status(list(BookStatus)[index_status - 1].value)
        except IndexError:
            validator.validate_status(status='')
        except Exception as e:
            raise e
        else:
            return status
        finally:
            self._clear_console()
            

    def handle_input(self, user_input) -> Menu:
        self._clear_console()
        match user_input:
            case '1':
                try:
                    self.book_id = self._input_id()
                    book = Library().find_book_id(book_id=self.book_id)
                    self.status = book.status
                except Exception as e:
                    self.book_id = None
                    cprint.red(e)
                finally:
                    return self
            case '2':
                try:
                    self.status = self.change_status()
                except Exception as e:
                    cprint.red(e)
                finally:
                    return self
            case MenuDesignations.SAVE.value:
                try:
                    Library().change_status(self.book_id, self.status)
                except Exception as e:
                    cprint.red(e)
                    return self
                else:
                    success = SuccessfulCompletion()
                    success.additional_info = 'Book status changed successfully'
                    success.last_state = self
                    return success
            case MenuDesignations.BACK.value:
                return MainMenu()
            case _:
                cprint.red('Incorrect selection. Please try again\n')
                return self
    
