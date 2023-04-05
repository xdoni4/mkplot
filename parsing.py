import numpy as np
import pandas as pd
import json


class RawSubplotData:
    def __init__(self, pltype, func_x, func_y, axes_labels, axes_pupils, color, description):
        self.type = pltype
        self.color = color
        self.func_x = func_x
        self.func_y = func_y
        self.axes_labels = axes_labels
        self.axes_pupils = axes_pupils
        self.color = color
        self.description = description

    def print(self):
        print("type: ", self.type, '\n',
              "axes_labels: ", self.axes_labels, '\n',
              "axes_pupils: ", self.axes_pupils, '\n',
              "color: ", self.color, '\n',
              "description: ", self.description, '\n')
        self.func_x.print()
        self.func_y.print()


class RawFuncData:
    def __init__(self, func_nm_table, func_nm, func_eval, expr, variables_table, variables,
                 constants, points, constants_eval, variable_errors):
        self.func_nm_table = func_nm_table
        self.func_nm = func_nm
        self.func_eval = func_eval
        self.expr = expr
        self.variables_table = variables_table
        self.variables = variables
        self.constants = constants
        self.points = points
        self.constants_eval = constants_eval
        self.variable_errors = variable_errors

    def print(self):
        print("func_nm: ", self.func_nm, '\n',
              "func_eval: ", self.func_eval, '\n',
              "expr: ", self.expr, '\n',
              "variables: ", self.variables, '\n',
              "constants: ", self.constants, '\n',
              "points: ", self.points, '\n'
                                       "constants_eval: ", self.constants_eval, '\n',
              "variable_errors: ", self.variable_errors, '\n')


class Parser:
    @classmethod
    def read(cls, filename):
        with open(filename, "r") as read_file:
            json_data = json.load(read_file)
            xl = pd.ExcelFile('table.xlsx')
        return json_data, xl

    @classmethod
    def parse_object(cls, data, xl):
        plots = []
        for i, plot in enumerate(data["data"], start=0):
            array = []
            subplots = plot["subplots"]
            for j, subplot in enumerate(subplots):
                df = pd.read_excel(xl, sheet_name=j)
                array.append(Parser.parse_subplot(subplot, df))
            plots.append((array, plot["title"]))
        return plots

    @classmethod
    def parse_df(cls, df):
        def split_cols():
            ncols = len(df.columns)
            idx = np.arange(ncols)[df.columns.str.match("Unnamed")]
            df_y = df[df.columns[:idx[0]]]
            df_x = df[df.columns[idx[0] + 1:idx[1]]]
            df_const = df[df.columns[idx[1] + 1:]]
            return df_y, df_x, df_const

        def get_function(func_df, const_df):
            func_nm_table = func_df.columns[0]
            func_nm = func_nm_table.split('.')[0]
            func_eval = func_df.iloc[:, 0].to_numpy()
            n_variables = len(np.arange(1, len(func_df.columns) - 1, 2))
            if n_variables == 0:
                n_variables += 1
            expr = func_df.columns[-1] if n_variables > 1 else func_nm
            variables_table = ' '.join(func_df.iloc[:, np.arange(1, len(func_df.columns) - 1, 2)].columns.tolist()) \
                if n_variables > 1 else func_nm_table
            variables = ' '.join(col_nm.split('.')[0] for col_nm in
                                 func_df.iloc[:, np.arange(1, len(func_df.columns) - 1, 2)].columns.tolist()) \
                if n_variables > 1 else func_nm
            constants = ' '.join(col_nm.split('.')[0] for col_nm in
                                 const_df.iloc[:, np.arange(1, len(const_df.columns) - 1, 2)].columns.tolist())
            points = func_df[variables_table.split()].to_numpy()
            constants_eval = const_df[constants.split()].iloc[0, :].to_numpy()
            variable_errors = func_df.iloc[:, np.arange(2, len(func_df.columns) - 1, 2)].to_numpy() \
                if n_variables > 1 else func_df.iloc[:, 1].to_numpy()

            return RawFuncData(func_nm_table, func_nm, func_eval, expr, variables_table, variables, constants,
                               points, constants_eval, variable_errors)

        df_y, df_x, df_const = split_cols()
        func_y = get_function(df_y, df_const)
        func_x = get_function(df_x, df_const)

        return func_x, func_y

    @classmethod
    def parse_subplot(cls, subplot, df):
        pltype = subplot["type"]
        func_x, func_y = Parser.parse_df(df)
        axes_labels = subplot["axes_labels"]
        axes_pupils = subplot["axes_pupils"]
        color = subplot["color"]
        description = subplot["description"]
        return RawSubplotData(pltype, func_x, func_y, axes_labels, axes_pupils, color, description)