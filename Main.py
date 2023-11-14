from File import File
import os
from Mananger import FileManager
import os
import shutil
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog



class FileManagerUI:
    def __init__(self, root_folder_path, file_manager):
        self.root = tk.Tk()
        self.root.title("Administrador de Archivos")
        self.root.geometry("700x500")  # Establecer el tamaño inicial
        self.root.configure(borderwidth=5, relief="groove")  # Personalizar el contorno

        # Contenedor principal organizado en dos filas: arriba y abajo
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # Barra de botones en la parte superior
        self.container_buttons = ttk.Frame(self.main_container)
        self.container_buttons.pack(side=tk.TOP, pady=10)

        # Botones
        self.delete_button = tk.Button(self.container_buttons, text="Eliminar Carpeta", command=self.delete_selected_folder, bg="#FF6666", fg="black", font=("Arial", 9))
        self.delete_button.pack(side=tk.LEFT, padx=5)

        self.add_button = tk.Button(self.container_buttons, text="Agregar Carpeta", command=self.add_folder_prompt, bg="#66CC66", fg="black", font=("Arial", 9))
        self.add_button.pack(side=tk.LEFT, padx=5)

        self.search_label = tk.Label(self.container_buttons, text="Buscar:")
        self.search_label.pack(side=tk.LEFT, padx=5)

        self.search_entry = tk.Entry(self.container_buttons, width=20)
        self.search_entry.pack(side=tk.LEFT, padx=5)

        self.search_button = tk.Button(self.container_buttons, text="Buscar", command=self.search_folder_file, bg="#66CCFF", fg="black", font=("Arial", 9))
        self.search_button.pack(side=tk.LEFT, padx=5)

        self.rename_button = tk.Button(self.container_buttons, text="Cambiar Nombre", command=self.rename_folder_prompt, bg="#FFD700", fg="black", font=("Arial", 9))
        self.rename_button.pack(side=tk.LEFT, padx=5)

        self.reset_button = tk.Button(self.container_buttons, text="Restablecer", command=self.reset_program, bg="#CCCCCC", fg="black", font=("Arial", 9))
        self.reset_button.pack(side=tk.LEFT, padx=5)

        # Árbol a la izquierda
        self.tree = ttk.Treeview(self.main_container, selectmode='browse')
        self.tree.pack(side=tk.LEFT, fill=tk.Y)
        style = ttk.Style()
        style.configure("Treeview",
                        background="#E1E1E1",  # Color de fondo
                        fieldbackground="#E1E1E1",  # Color de fondo de la celda
                        foreground="black")  # Color del texto

        style.map("Treeview",
                background=[("selected", "#347083")],  # Color de fondo cuando se selecciona una fila
                foreground=[("selected", "white")])  # Color del texto cuando se selecciona una fila

        # Scrollbar para el árbol
        scrollbar = ttk.Scrollbar(self.main_container, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Texto para mostrar archivos y carpetas a la derecha
        self.result_text = tk.Text(self.main_container, wrap=tk.WORD, height=10, width=50)
        self.result_text.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Configurar el evento de selección en el árbol
        self.tree.bind("<<TreeviewSelect>>", self.show_folder_contents)

        self.file_manager = file_manager
        self.build_tree(file_manager.root, "")

        # Desactivar interacción del usuario con el widget de Texto
        self.result_text.bind("<Button-1>", lambda e: "break")  # Desactivar clic izquierdo
        self.result_text.bind("<KeyPress>", lambda e: "break")  # Desactivar entrada de teclado
            

    def build_tree(self, node, parent_id):
        if not node:
            return
        item_id = self.tree.insert(parent_id, 'end', text=node.name)
        for child in node.child:
            self.build_tree(child, item_id)

    def delete_selected_folder(self):
        selected_item = self.tree.selection()
        if selected_item:
            folder_name = self.tree.item(selected_item, 'text')
            self.file_manager.delete_folder_by_name(folder_name)
            # Limpiar la vista del árbol antes de reconstruirlo
            self.tree.delete(*self.tree.get_children())
            # Actualizar la vista del árbol para reflejar la eliminación de la carpeta
            self.build_tree(self.file_manager.root, "")
    
    def add_folder_prompt(self):
        selected_item = self.tree.selection()
        parent_folder = self.tree.item(selected_item, 'text')

        if parent_folder:
            # Solicitar el nombre de la nueva carpeta
            new_folder_name = tk.simpledialog.askstring("Agregar Carpeta", "Nombre de la nueva carpeta:")

            if new_folder_name:
                # Llamar al método de FileManager para agregar la carpeta en la carpeta padre seleccionada
                self.file_manager.add_folder(parent_folder, new_folder_name)
                
                # Limpiar la vista del árbol antes de reconstruirlo
                self.tree.delete(*self.tree.get_children())
                
                # Luego, actualiza la vista del árbol para reflejar la adición de la carpeta
                parent_id = ""
                self.build_tree(self.file_manager.root, parent_id)


    def show_folder_contents(self, event):
        # Obtener el elemento seleccionado en el árbol
        selected_item = self.tree.selection()
        if selected_item:
            folder_name = self.tree.item(selected_item, 'text')
            folder_node = self.file_manager.find_folder_by_name(folder_name)
            if folder_node:
                # Mostrar archivos y carpetas en la ruta seleccionada
                folder_path = os.path.join(self.file_manager.root.path, folder_node.path)
                content = self.get_content(folder_path)
                self.update_result(content)

    def get_content(self, route):
        try:
            content = os.listdir(route)
            return content
        except FileNotFoundError:
            return [f"La ruta {route} no existe."]
        except PermissionError:
            return [f"No tienes permisos para acceder a la ruta {route}."]

    def update_result(self, content):
        self.result_text.delete("1.0", tk.END)  # Limpiar el contenido actual
        for element in content:
            self.result_text.insert(tk.END, f"{element}\n")
            
    
    def search_folder_file(self):
        # Método para buscar carpetas o archivos por nombre

        # Obtener el nombre a buscar desde la entrada de búsqueda
        search_text = self.search_entry.get().strip()

        if search_text:
            # Limpiar la vista del árbol antes de realizar la búsqueda
            self.tree.delete(*self.tree.get_children())
            
            # Realizar la búsqueda en la estructura de carpetas y archivos
            search_results = self.file_manager.search_folder_file_by_name(search_text)
            
            # Construir el árbol con los resultados de la búsqueda
            parent_id = ""
            for result in search_results:
                self.build_tree(result, parent_id)

            # Limpiar y actualizar el resultado en el área de texto
            self.result_text.delete("1.0", tk.END)
            if search_results:
                self.result_text.insert(tk.END, f"El archivo {result.name} se encuentra en el disco.\n")
            else:
            # Mostrar mensaje si no se encuentra el archivo en el disco
                self.result_text.insert(tk.END, f"El archivo {search_text} NO se encuentra en el disco.\n")

         
            
        else:
            # Si no se ingresó ningún texto, mostrar un mensaje en el área de texto
            self.result_text.delete("1.0", tk.END)
            self.result_text.insert(tk.END, "Por favor, ingrese un nombre para buscar.")

            parent_id = ""
            self.build_tree(self.file_manager.root, parent_id)

    
    def rename_folder_prompt(self):
        # Método para cambiar el nombre de una carpeta con un cuadro de diálogo
        selected_item = self.tree.selection()

        if selected_item:
            old_folder_name = self.tree.item(selected_item, 'text')
            new_folder_name = tk.simpledialog.askstring("Cambiar Nombre de Carpeta", f"Nuevo nombre para '{old_folder_name}':")

            if new_folder_name:
                # Llamar al método de FileManager para cambiar el nombre de la carpeta
                success = self.file_manager.rename_folder(old_folder_name, new_folder_name)

                if success:
                    # Limpiar la vista del árbol antes de reconstruirlo
                    self.tree.delete(*self.tree.get_children())
                    # Actualizar la vista del árbol para reflejar el cambio de nombre de la carpeta
                    self.build_tree(self.file_manager.root, "")
                else:
                    # Mostrar un mensaje si no se encuentra la carpeta
                    tk.messagebox.showinfo("Error", f"No se encontró la carpeta '{old_folder_name}'.")
    
    def reset_program(self):
        # Limpiar la entrada de búsqueda
        self.search_entry.delete(0, tk.END)

        # Restaurar la vista del árbol con la estructura original
        self.tree.delete(*self.tree.get_children())
        self.build_tree(self.file_manager.root, "")

        # Limpiar el área de resultados
        self.result_text.delete("1.0", tk.END)

            

    def run(self):
        self.root.mainloop()

if __name__ == '__main__':
    root_folder_path = '/Users/juanm/Documents/Universidad/EstructuraDeDatos2/proyecto1/raiz'  # ruta de tu carpeta principal
    file_manager = FileManager(root_folder_path)
    file_manager_ui = FileManagerUI(root_folder_path, file_manager)
    file_manager_ui.run()



# root_folder_path = "/Users/juanm/Documents/Universidad/EstructuraDeDatos2/proyecto1/raiz"
# file_manager = FileManager(root_folder_path)

# # Mostrar la ruta de cada carpeta dentro de la carpeta raíz
# file_manager.display_paths(file_manager.root)


