from typing import Any
import sqlalchemy
from sqlalchemy.orm import class_mapper

# def to_dict(obj: Any, max_depth=2) -> dict:
#     def _to_dict(obj: Any, depth=0) -> dict:
#         if obj is None or depth > max_depth:
#             return None
#         data = {c.key: getattr(obj, c.key) for c in sqlalchemy.inspect(obj).mapper.column_attrs}
#         for name, relation in sqlalchemy.inspect(obj).mapper.relationships.items():
#             related_obj = getattr(obj, name)
#             if related_obj is None:
#                 data[name] = None
#             elif relation.uselist:
#                 data[name] = [_to_dict(child, depth+1) for child in related_obj]
#             else:
#                 data[name] = _to_dict(related_obj, depth+1)
#         return data
#     return _to_dict(obj).

def to_dict(obj):
    return {c.key: getattr(obj, c.key) for c in sqlalchemy.inspect(obj).mapper.column_attrs}

def conference_to_dict(conference):
    data = {c.key: getattr(conference, c.key) for c in sqlalchemy.inspect(conference).mapper.column_attrs}
    for name in ['location', 'status', 'client', 'venue', 'sponsors', 'exhibitors']:
        related_obj = getattr(conference, name, None)
        if related_obj is None:
            data[name] = None
        elif isinstance(related_obj, list):
            data[name] = [to_dict(child) for child in related_obj if hasattr(child, '_sa_class_manager')]
        elif hasattr(related_obj, '_sa_class_manager'):
            related_obj_dict = to_dict(related_obj)
            if name == 'client' and 'status' not in related_obj_dict:
                related_obj_dict['status'] = 'inactive'  # replace 'default_status' with the actual default status
            data[name] = related_obj_dict
    return data