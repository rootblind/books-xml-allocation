import tkinter as tk
from tkinter import filedialog, messagebox
import xml.etree.ElementTree as ET
import os

class LibraryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Book Allocation in Library") # setting the title
        
        # Adding a label for instructions
        self.label_instructions = tk.Label(root, text="Select the XML files: carti, categorii, rafturi")
        self.label_instructions.pack(pady=10) #setting its position in the window

        # adding a button for each xml file to be selected
        self.button_select_books = tk.Button(root, text="Select carti.xml", command=self.select_books)
        self.button_select_books.pack(pady=5)
        self.button_select_categories = tk.Button(root, text="Select categorii.xml", command=self.select_categories)
        self.button_select_categories.pack(pady=5)
        self.button_select_shelves = tk.Button(root, text="Select rafturi.xml", command=self.select_shelves)
        self.button_select_shelves.pack(pady=5)
        self.button_generate = tk.Button(root, text="Generate repartizare.xml", command=self.generate_allocation)
        self.button_generate.pack(pady=20)
        # initializing the pathing to each file
        self.books_path = None
        self.categories_path = None
        self.shelves_path = None

    # pressing a button calls the corresponding function which will open the file location and then confirm which file path was selected
    def select_books(self):
        self.books_path = filedialog.askopenfilename(filetypes=[("XML files", "*.xml")]) # the function that opens a file browser and lets the user to select a file
        if self.books_path:
            messagebox.showinfo("Selected", f"File selected: {self.books_path}") #the function that pops an informative window

    def select_categories(self):
        self.categories_path = filedialog.askopenfilename(filetypes=[("XML files", "*.xml")])
        if self.categories_path:
            messagebox.showinfo("Selected", f"File selected: {self.categories_path}")

    def select_shelves(self):
        self.shelves_path = filedialog.askopenfilename(filetypes=[("XML files", "*.xml")])
        if self.shelves_path:
            messagebox.showinfo("Selected", f"File selected: {self.shelves_path}")

    # when selecting the "Generate repartizare.xml" button, all three files must be selected beforehand and the information will be
    # processed and allocated
    def generate_allocation(self):
        if not all([self.books_path, self.categories_path, self.shelves_path]):
            messagebox.showwarning("Warning", "You need to select all three XML files!")
            return
        
        try:
            # parsing each xml file to a variable and then getting the root element of the xml structure and returning it as an object
            tree_books = ET.parse(self.books_path)
            root_books = tree_books.getroot() 
            tree_categories = ET.parse(self.categories_path)
            root_categories = tree_categories.getroot()
            tree_shelves = ET.parse(self.shelves_path)
            root_shelves = tree_shelves.getroot()
            
            # creating a dictionary for categories with 'name' as key and 'id' as value for categories, iterating over the root_categories
            categories = {category.find('name').text: category.find('id').text for category in root_categories.findall('category')}
            # creating a dictionary for shelves with category id as key and shelf id as value by using the zip function which
            # pairs corresponding elements both roots
            shelves = {category.find('id').text: shelf.find('id').text for shelf, category in zip(root_shelves.findall('shelf'), root_categories.findall('category'))}
            
            allocation = {} # allocation dictionary is used to keep track of what elements are allocated yet
            # fetching all books and their details
            for book in root_books.findall('book'):
                book_id = book.find('id').text
                title = book.find('title').text
                category = book.find('category').text
                # mapping categoies and shelves
                category_id = categories.get(category, None)
                shelf_id = shelves.get(category_id, None)
                if shelf_id:
                    if shelf_id not in allocation: # if shelf id exists and is not allocated, then it is defined first before appending elements
                        allocation[shelf_id] = []
                    allocation[shelf_id].append({'id': book_id, 'title': title, 'category': category})
            
            # constructing xml document for the output file
            # each element will be a shelf represented by an ID and its subelements will be represented by books that have
            # their own id, title and category
            root_allocation = ET.Element('repartizare')
            for shelf_id, books in allocation.items():
                shelf_elem = ET.SubElement(root_allocation, 'shelf', id=shelf_id)
                for book in books:
                    ET.SubElement(shelf_elem, 'book', id=book['id'], title=book['title'], category=book['category'])
            
            tree_allocation = ET.ElementTree(root_allocation)
            output_path = os.path.join(os.path.dirname(self.books_path), 'repartizare.xml')
            tree_allocation.write(output_path, encoding='utf-8', xml_declaration=True)
            # confirmation window
            messagebox.showinfo("Success", f"The file repartizare.xml has been successfully generated at {output_path}")
        
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

if __name__ == "__main__":
    root = tk.Tk() # initializing the main window
    app = LibraryApp(root) # creating an instance of the application object
    root.mainloop() # keeps the application going and waiting for events until the X button is pressed
