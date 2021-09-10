import os

from kivymd.app import MDApp

app = MDApp.get_running_app()


class Config:
    variable_dict = {}

    def get_variable(self, variable):
        if variable in self.variable_dict:
            return self.variable_dict[variable]
        else:
            raise Exception(f"{variable} Doesn't Exist in variable dictionary")

    def set_variables(self, variable_dict=None):
        if variable_dict is None:
            variable_dict = {}
        self.variable_dict = variable_dict
        for var, value in variable_dict.items():
            if 'self.' in var:
                var = var.replace('self.', '')
            if var != 'dark_mode':
                if type(value) != str:
                    exec(f'app.{var}={value}')
                else:
                    exec(f"app.{var}='{value}'")

    def save_variables(self):
        for var in list(self.variable_dict.keys()):
            if 'self.' in var:
                del self.variable_dict[var]
                var = var.replace('self.', '')
            exec(f"self.variable_dict['{var}']= app.{var}")
        with open('variable_dict.txt', 'w') as file:
            file.write(str(self.variable_dict))

    def restore_variables(self):
        if os.path.exists('variable_dict.txt'):
            with open('variable_dict.txt', 'r') as file:
                self.variable_dict = eval(file.read())
            self.set_variables(self.variable_dict)
            if self.variable_dict != {}:
                return True
            else:
                return False
        else:
            return False
