import pandas as pd

class ExcelExporter:
    @staticmethod
    def export(df: pd.DataFrame, output_file: str):
        df.to_excel(output_file, index=False)
