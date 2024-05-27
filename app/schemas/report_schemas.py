from pydantic import BaseModel


class Report(BaseModel):
    template_id: str
    input_data: dict
    output_filename: str