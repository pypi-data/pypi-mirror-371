import pkg_resources
import sys
import os


class ModLoadingException(Exception):
    def __init__(self, *args):
        super().__init__(*args)


class InvalidModException(ModLoadingException):
    def __init__(self, *args):
        super().__init__(*args)


class DependencyError(ModLoadingException):
    def __init__(self, *args):
        super().__init__(*args)


class ModIsNotExists(ModLoadingException):
    def __init__(self, *args):
        super().__init__(*args)


class DirectoryIsNotMod(InvalidModException):
    def __init__(self, *args):
        super().__init__(*args)


class PackageIsNotMod(InvalidModException):
    def __init__(self, *args):
        super().__init__(*args)


class ModNotImplementsInterface(InvalidModException):
    def __init__(self, *args):
        super().__init__(*args)


class ModNotHaveName(InvalidModException):
    def __init__(self, *args):
        super().__init__(*args)


class RequiredPackageNotExists(DependencyError):
    def __init__(self, *args):
        super().__init__(*args)


class RequiredModNotExists(DependencyError):
    def __init__(self, *args):
        super().__init__(*args)


class ModElementNotImplementsInterface(InvalidModException):
    def __init__(self, *args):
        super().__init__(*args)


class LoggerInterface:
    def debug(self, msg):
        pass

    def info(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        pass

    def critical(self, msg):
        pass


class Mod:
    name: str
    title: str = "Untitled mod"
    version: str = "1.0.0"
    description: str = "Description is not provided."
    requires_mods: list[str] = []
    requires_packages: list[str] = []

    def __init__(self):
        pass

    def pre_load(self):
        pass

    def on_load(self):
        pass


class ModLoader:
    loaded_mods: list[Mod] = []
    mods_will_loaded: list[str] = []

    mod_loader_globals = {}

    def __init__(self):
        pass

    def load_mod(self, path: str):
        if not os.path.exists(path):
            raise ModIsNotExists(f"Directory {path} is not exists")

        if not os.path.exists(f"{path}/mod.py"):
            raise DirectoryIsNotMod(
                f"Directory {path} is not mod because it is not contains 'mod.py'"
            )

        sys.path.append(path)

        mod: Mod
        with open(f"{path}/mod.py") as fin:
            mod_locals: dict = {}
            mod_globals: dict = {}
            exec(fin.read(), mod_globals, mod_locals)

            if "init" not in mod_locals:
                raise PackageIsNotMod(
                    f"Package '{path}/mod.py' is not mod because mod_locals ({mod_locals}) is not contains 'init()'"
                )

            mod = eval("init()", mod_globals, mod_locals)

        if not isinstance(mod, Mod):
            raise ModNotImplementsInterface(f"Mod is not implements interface")

        if not hasattr(mod, "name"):
            raise ModNotHaveName(f"Mod not have name")

        for required_mod in mod.requires_mods:
            if required_mod not in self.mods_will_loaded:
                raise RequiredModNotExists(
                    f"Required mod '{required_mod}' is not installed. Installed mods: {self.mods_will_loaded}"
                )

        installed_packages = [package.key for package in pkg_resources.working_set]
        for required_package in mod.requires_packages:
            if required_package not in installed_packages:
                raise RequiredPackageNotExists(
                    f"Required package '{required_package}' is not installed. Installed packages: {installed_packages}"
                )

        self.loaded_mods.append(mod)
        mod.pre_load()

        for element_type_dir in os.scandir(path):
            if os.path.isdir(element_type_dir):
                if not element_type_dir.name.startswith("."):
                    if hasattr(self, f"process_{element_type_dir.name}"):
                        processor = getattr(self, f"process_{element_type_dir.name}")
                        for element_dir in os.scandir(element_type_dir):
                            if os.path.isdir(element_dir):
                                try:
                                    processor(os.path.abspath(element_dir))

                                finally:
                                    continue

        mod.on_load()

    def process_test_elements(self, path: str):
        print(f"Test package: {path}")
