import os
from File import File
import shutil


class FileManager:
    def __init__(self, root_folder_path):
        self.root = File(os.path.basename(root_folder_path), root_folder_path)
        self.build_tree(root_folder_path, self.root, root_folder_path)

    def build_tree(self, path, parent_folder, root_path):
        try:
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path):
                    relative_path = os.path.relpath(item_path, root_path)
                    new_folder = File(item, relative_path)
                    parent_folder.child.append(new_folder)
                    self.build_tree(item_path, new_folder, root_path)
        except PermissionError as e:
            print(f"No hay permisos  '{path}'")

    def display_paths(self, node, current_path=""):
        if not node:
            return
        current_path = os.path.join(current_path, node.path)
        print(current_path)
        for child in node.child:
            self.display_paths(child, current_path)

    def find_folder_by_name(self, folder_name, node=None):
        if node is None:
            node = self.root
        if node.name == folder_name:
            return node
        for child in node.child:
            result = self.find_folder_by_name(folder_name, child)
            if result is not None:
                return result
        return None

    def delete_folder_by_name(self, folder_name, node=None):
        if node is None:
            node = self.root

        for child in node.child:
            if child.name == folder_name:
                try:
                    full_path = os.path.join(self.root.path, child.path)
                    shutil.rmtree(full_path)
                    print(f"Carpeta borrada: {full_path}")
                    node.child.remove(child)
                    return True
                except PermissionError as e:
                    print(f"No hay permisos para borrar '{folder_name}'")
                    return False
            elif self.delete_folder_by_name(folder_name, child):
                return True

        return False

    def check_and_display_folder(self, folder_name):
        folder_node = self.find_folder_by_name(folder_name)
        if folder_node is not None:
            print(f"La carpeta '{folder_name}' está presente.")
            print(f"Ruta: {os.path.join(self.root.path, folder_node.path)}")
        else:
            print(f"La carpeta '{folder_name}' no se encuentra.")

    def add_folder(self, parent_name, new_folder_name):
        parent_node = self.find_folder_by_name(parent_name)
        if parent_node:
            # Modificar para construir correctamente la ruta de la nueva carpeta
            new_folder_path = os.path.join(self.root.path, parent_node.path, new_folder_name)
            # Verificar si la carpeta ya existe en el disco antes de crearla
            if not os.path.exists(new_folder_path):
                os.mkdir(new_folder_path)
                new_folder = File(new_folder_name, os.path.relpath(new_folder_path, self.root.path))
                parent_node.child.append(new_folder)
                print(f"Se ha creado la carpeta '{new_folder_name}' en '{parent_name}'")
                # Actualiza la vista del árbol para reflejar la adición de la carpeta
                self.display_paths(self.root)
            else:
                print(f"La carpeta '{new_folder_name}' ya existe en '{parent_name}'")
        else:
            print(f"No se puede crear la carpeta. '{parent_name}' no se encontró.")

    def search_folder_file_by_name(self, search_text, node=None):
        # Método para buscar carpetas o archivos por nombre
        if node is None:
            node = self.root

        search_results = []

        if node.name.lower().startswith(search_text.lower()):
            # Si el nombre del nodo coincide, agregarlo a los resultados
            search_results.append(node)

        for child in node.child:
            # Realizar la búsqueda en los hijos recursivamente
            search_results.extend(self.search_folder_file_by_name(search_text, child))

        return search_results
    
    def rename_folder(self, old_name, new_name, node=None):
        # Método para cambiar el nombre de una carpeta
        if node is None:
            node = self.root

        for child in node.child:
            if child.name == old_name and isinstance(child, File):
                # Obtener la ruta completa de la carpeta antigua y nueva
                old_folder_path = os.path.join(self.root.path, child.path)
                new_folder_path = os.path.join(self.root.path, os.path.dirname(child.path), new_name)

                try:
                    # Renombrar la carpeta en el sistema de archivos
                    os.rename(old_folder_path, new_folder_path)
                except Exception as e:
                    # Manejar cualquier error que pueda ocurrir durante el cambio de nombre
                    print(f"Error al cambiar el nombre de la carpeta: {e}")
                    return False

                # Actualizar el nombre y la ruta del nodo
                child.name = new_name
                child.path = os.path.relpath(new_folder_path, self.root.path).replace(os.sep, '/')
                
                # Actualizar las rutas de los hijos recursivamente
                self.update_paths(child, child.path)

                return True
            elif self.rename_folder(old_name, new_name, child):
                return True

        return False

    def update_paths(self, node, parent_path):
        # Método para actualizar las rutas de los nodos hijos recursivamente
        for child in node.child:
            child.path = os.path.join(parent_path, child.name)
            self.update_paths(child, child.path)


# Uso de la clase FileManager
# root_folder_path = "/Users/juanm/Documents/Universidad/EstructuraDeDatos2/proyecto1/raiz"
# file_manager = FileManager(root_folder_path)

# Mostrar la ruta de cada carpeta dentro de la carpeta raíz
# file_manager.display_paths(file_manager.root)

#Eliminar una carpeta por su nombre de nodo
# folder_name_to_delete = "nodo3"
# file_manager.delete_folder_by_name(folder_name_to_delete)
# print("_____________________________")

#buscar por nombre si la carpeta e encuientra en a carpeta raiz
# folder_name_to_find = "nodo2"
# file_manager.check_and_display_folder(folder_name_to_find)

#Crear una nueva carpeta hija de una carpeta existente
# parent_folder_name = "raiz"
# new_folder_name = "nodo7"
# file_manager.add_folder(parent_folder_name, new_folder_name)

# Mostrar la ruta de cada carpeta después de agregar la nueva carpeta


